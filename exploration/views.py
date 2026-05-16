import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import ExplorationMap
from main.models import Item, Inventory
from users.models import CharInfo

# 1. 맵 에디터 페이지
def map_editor(request, map_id):
    map_obj = get_object_or_404(ExplorationMap, id=map_id)
    return render(request, 'exploration/editor.html', {
        'map_id': map_id,  
        'map_data': json.dumps(map_obj.content_data)
    })

# exploration/views.py

def save_map(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            map_id = data.get('map_id')
            content_data = data.get('content_data') # JS에서 보낸 데이터

            # 💡 중요: map_id로 정확한 객체를 찾아야 합니다.
            map_obj = get_object_or_404(ExplorationMap, id=map_id)
            map_obj.content_data = content_data
            map_obj.save()

            return JsonResponse({"success": True})
        except Exception as e:
            # 에러 발생 시 메시지를 반환하도록 설정
            return JsonResponse({"success": False, "message": str(e)}, status=400)

# 3. 조사 진행 및 스탯 해금 로직 (play_exploration과 통합!)
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login')
def play_node(request, map_id, node_id):
    # 스탯 표시 이름 매핑 (8종 스탯 일치)
    STAT_NAMES = {
        'stat_str': '근력', 'stat_agi': '민첩', 'stat_int': '지능',
        'stat_luk': '행운', 'stat_rep': '평판', 'stat_good': '선의',
        'stat_mag': '마력', 'stat_div': '신성력'
    }
    user = request.user
    charinfo = CharInfo.objects.get(user=user)
    character = charinfo.char
    explore_map = get_object_or_404(ExplorationMap, id=map_id)

    # 문자열 비교 안정성을 위해 str 변환
    node_id_str = str(node_id)

    if character.energy <= 0:
        messages.error(request, "활력이 부족하여 더 이상 탐색할 수 없습니다.")
        return redirect('exploration:play_node', map_id=map_id, node_id=charinfo.last_explore_node_id)

    try:
        all_nodes = explore_map.content_data['drawflow']['Home']['data']
        current_node = all_nodes[node_id_str]
        node_custom_data = current_node['data']
    except KeyError:
        return redirect('exploration:play_node', map_id=map_id, node_id='1')

    # 🛠️ [최적화 추가] 에디터에서 입력한 이미지 파일명을 가져옵니다.
    # 에디터 인풋 창의 df-bg_img_name, df-speaker_img_name 과 매핑됩니다.
    # 입력 값이 없거나 빈 문자열일 경우를 대비해 기본 파일명(default)을 지정해 줍니다.
    bg_img_name = node_custom_data.get('bg_img_name') or 'default_bg.png'
    speaker_img_name = node_custom_data.get('speaker_img_name') or 'default_speaker.png'

    # 🛠️ [중요] 팝업창 판단을 위해 '진짜 예전 기록'을 변수에 따로 백업해 둡니다.
    previous_saved_node = charinfo.last_explore_node_id

    # 🛠️ [해결] 활력(Energy) 차감 및 아이템 획득 로직 (중복 실행 방지)
    # 진짜로 노드가 변경되었을 때만 실행합니다.
    if previous_saved_node != node_id_str:
        
        # HTML에서 ?return=true 신호를 보냈는지 확인합니다.
        is_return_action = request.GET.get('return') == 'true'

        if is_return_action:
            stamina_cost = 1
        else:
            stamina_cost = int(node_custom_data.get('stamina', 0) or 0)

        if stamina_cost > 0:
            character.energy = max(0, character.energy - stamina_cost)
            character.save()

        # 아이템 획득 로직 (돌아가기 액션일 때는 중복 지급 방지)
        if not is_return_action:
            item_name = node_custom_data.get('item_name')
            if item_name:
                item_obj, _ = Item.objects.get_or_create(name=item_name)
                inv, created = Inventory.objects.get_or_create(
                    user=request.user, 
                    item=item_obj,
                    defaults={'quantity': 0}
                )
                inv.quantity += 1
                inv.save()

    # 🛠️ [해결] 진행 상황 저장 통일 및 27번 노드 예외 처리
    # 현재 노드가 '27'번이 아닐 때만 데이터베이스를 전면 갱신합니다.
    # 이렇게 해야 다른 곳에 갔다와도 예전 기록(예: 108)이 유지되어 팝업창이 뜹니다!
    if node_id_str != '27':
        charinfo.last_explore_map_id = map_id
        charinfo.last_explore_node_id = node_id_str
        charinfo.save()

    # 선택지 중복 제거 및 통합 로직
    choices = []
    seen_ids = set() 
    outputs = current_node.get('outputs', {})

    for out_key in outputs:
        connections = outputs[out_key].get('connections', [])
        for conn in connections:
            next_id = str(conn['node'])
            if next_id in seen_ids:
                continue
                
            next_node_data = all_nodes[next_id]['data']
                
            req_stat = next_node_data.get('req_stat')
            req_op = next_node_data.get('req_operator', 'gte') 
            req_val = int(next_node_data.get('req_val', 0) or 0)
                
            is_unlocked = True
            if req_stat:
                char_stat_val = getattr(character, req_stat, 0)
                    
                if req_op == 'gte':
                    is_unlocked = char_stat_val >= req_val
                elif req_op == 'lt':
                    is_unlocked = char_stat_val < req_val
                        
            choices.append({
                'next_node_id': next_id,
                'text': next_node_data.get('title', '다음으로'),
                'is_unlocked': is_unlocked,
                'req_stat_name': STAT_NAMES.get(req_stat, req_stat),
                'req_operator': req_op,  
                'req_val': req_val,
                'stamina_cost': next_node_data.get('stamina', 0)
            })
            seen_ids.add(next_id)

    context = {
        'map_title': explore_map.title,
        'map_id': map_id,
        'node_data': node_custom_data, 
        'choices': choices,
        'character': character,
        # 🛠️ 템플릿에는 아까 백업해 둔 '진짜 예전 기록'을 넘겨주어야 자바스크립트가 인지합니다!
        'last_node_id': previous_saved_node,
        
        # 🛠️ [최적화 추가] 템플릿에서 쉽게 분기하고 가져다 쓸 수 있도록 이미지 파일명을 담아 보냅니다.
        'bg_img_name': bg_img_name,
        'speaker_img_name': speaker_img_name,
    }
    return render(request, 'exploration/play.html', context)