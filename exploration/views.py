import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import ExplorationMap
from main.models import Item, Inventory
from users.models import CharInfo


@login_required(login_url='/login')
def play_main(request):
    user = request.user
    
    # 🛠️ [안전장치 추가] get 대신 filter().first()를 사용하여 데이터가 없어도 에러가 나지 않게 합니다.
    charinfo = CharInfo.objects.filter(user=user).first()
    
    # 만약 로그인한 유저의 CharInfo 데이터가 아예 없다면 예외 처리
    if charinfo:
        character = charinfo.char
    else:
        character = None
        # 필요하다면 messages.warning(request, "캐릭터 정보가 존재하지 않습니다.") 등을 넣을 수 있습니다.
    
    # DB에 등록된 모든 탐색 맵을 가져옵니다 (발테리온-수도, 왕도 등)
    maps = ExplorationMap.objects.filter(id=4)
    
    # 각 맵 ID별 시작 노드 번호 매핑
    START_NODES = {
        1: '27',  # 1번 맵의 시작 노드는 27
        3: '93',   # 2번 맵의 시작 노드는 1
        4: '93',   # 2번 맵의 시작 노드는 1
    }
    
    for emap in maps:
        emap.start_node = START_NODES.get(emap.id, '1')

    context = {
        'maps': maps,
        'character': character, # 이제 데이터가 없어도 None으로 안전하게 패스됩니다.
    }
    return render(request, 'exploration/play_main.html', context)


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

    # 🛠️ [최적화] 에디터에서 입력한 이미지 파일명을 가져옵니다. (없으면 기본값)
    bg_img_name = node_custom_data.get('bg_img_name') or 'default_bg.png'
    speaker_img_name = node_custom_data.get('speaker_img_name') or 'default_speaker.png'

    # 🛠️ [동적 처리 추가] 각 맵 ID별 '시작 노드 번호' 매핑
    START_NODES = {
        1: '27',  # 1번 맵의 시작 노드는 27
        2: '1',   # 2번 맵의 시작 노드는 1
    }
    start_node_id = START_NODES.get(map_id, '1')

    # 🛠️ 팝업창 판단을 위해 '진짜 예전 기록'을 변수에 따로 백업해 둡니다.
    previous_saved_node = charinfo.last_explore_node_id

    # 🛠️ 활력(Energy) 차감 및 아이템 획득 로직 (중복 실행 방지)
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

    # 🛠️ 진행 상황 저장 통일 및 각 맵별 시작 노드 예외 처리
    # 현재 노드가 해당 맵의 시작 노드가 아닐 때만 데이터베이스를 전면 갱신합니다.
    if node_id_str != start_node_id:
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
        'last_node_id': previous_saved_node,
        'bg_img_name': bg_img_name,
        'speaker_img_name': speaker_img_name,
        
        # 🛠️ 자바스크립트가 동적으로 시작 노드를 인지할 수 있도록 보냅니다.
        'start_node_id': start_node_id, 
    }
    return render(request, 'exploration/play.html', context)