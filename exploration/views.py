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

    if character.energy <= 0:
        # 메시지와 함께 이전 노드로 돌려보내거나 특정 에러 페이지로 유도
        messages.error(request, "활력이 부족하여 더 이상 탐색할 수 없습니다.")
        return redirect('exploration:play_node', map_id=map_id, node_id=charinfo.last_explore_node_id)

    try:
        all_nodes = explore_map.content_data['drawflow']['Home']['data']
        current_node = all_nodes[str(node_id)]
        node_custom_data = current_node['data']
    except KeyError:
        return redirect('exploration:play_node', map_id=map_id, node_id='1')

    # 진행 상황 저장
    charinfo.last_explore_map_id = map_id
    charinfo.last_explore_node_id = str(node_id)
    charinfo.save()

    # 1. 활력(Energy) 차감 로직
    # 현재 노드에 진입할 때 소모되는 에너지를 계산합니다.
    stamina_cost = int(node_custom_data.get('stamina', 0))
    if stamina_cost > 0:
        # 캐릭터의 현재 에너지를 차감 (최소 0 유지)
        character.energy = max(0, character.energy - stamina_cost)
        character.save()

    # 2. 아이템 획득 및 인벤토리 추가 로직
    item_name = node_custom_data.get('item_name')
    if item_name:
        # 아이템 모델에서 이름으로 찾거나 생성
        item_obj, _ = Item.objects.get_or_create(name=item_name)
        # 인벤토리에 수량 1개 추가
        inv, created = Inventory.objects.get_or_create(
            character=character, 
            item=item_obj,
            defaults={'quantity': 0}
        )
        inv.quantity += 1
        inv.save()

    # 💡 [해결] 선택지 중복 제거 및 통합 로직
    choices = []
    seen_ids = set() # 중복 방지용
    outputs = current_node.get('outputs', {})

    for out_key in outputs:
        connections = outputs[out_key].get('connections', [])
        for conn in connections:
            next_id = str(conn['node'])
            next_node_data = all_nodes[next_id]['data']
                
            req_stat = next_node_data.get('req_stat')
            req_op = next_node_data.get('req_operator', 'gte') # 기본값은 gte(이상)
            req_val = int(next_node_data.get('req_val', 0) or 0)
                
            is_unlocked = True
            if req_stat:
                char_stat_val = getattr(character, req_stat, 0)
                    
                # 💡 연산자에 따른 비교 로직 분기
                if req_op == 'gte':
                    is_unlocked = char_stat_val >= req_val
                elif req_op == 'lt':
                    is_unlocked = char_stat_val < req_val
                        
            choices.append({
                'next_node_id': next_id,
                    'text': next_node_data.get('title', '다음으로'),
                    'is_unlocked': is_unlocked,
                    'req_stat_name': STAT_NAMES.get(req_stat, req_stat),
                    'req_val': req_val,
                    'stamina_cost': next_node_data.get('stamina', 0)
            })
            seen_ids.add(next_id)

    context = {
        'map_title': explore_map.title,
        'map_id': map_id,
        'node_data': node_custom_data, 
        'choices': choices,
        'character': character
    }
    return render(request, 'exploration/play.html', context)