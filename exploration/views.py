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

# 2. 맵 데이터 저장 (AJAX)
def save_map(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            map_id = data.get('map_id')
            content_data = data.get('content_data')

            map_obj = ExplorationMap.objects.get(id=map_id)
            map_obj.content_data = content_data
            map_obj.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

# 3. 조사 진행 및 스탯 해금 로직 (play_exploration과 통합!)
@login_required(login_url='/login')
def play_node(request, map_id, node_id):
    STAT_NAMES = {
        'strength': '근력', 'agility': '민첩', 'intelligence': '지능',
        'luck': '행운', 'stamina': '체력', 'charisma': '매력',
        'willpower': '의지', 'perception': '통찰'
    }
    user = request.user
    charinfo = CharInfo.objects.get(user=user)
    character = charinfo.char

    # 맵 정보 가져오기
    explore_map = get_object_or_404(ExplorationMap, id=map_id)

    # Drawflow 노드 찾기
    try:
        all_nodes = explore_map.content_data['drawflow']['Home']['data']
        current_node = all_nodes[str(node_id)]
        node_custom_data = current_node['data']
    except KeyError:
        return redirect('play_node', map_id=map_id, node_id='1')

    # 진행 상황 저장
    charinfo.last_explore_map_id = map_id
    charinfo.last_explore_node_id = str(node_id)
    charinfo.save()

    # 아이템 즉시 획득 로직
    reward_item_id = node_custom_data.get('reward_item_id')
    if reward_item_id:
        try:
            item = Item.objects.get(id=reward_item_id)
            inventory_item, created = Inventory.objects.get_or_create(
                user=user, item=item, defaults={'quantity': 0}
            )
            inventory_item.quantity += 1
            inventory_item.save()
        except Item.DoesNotExist:
            pass 

    # 💡 [핵심] Drawflow 연결선을 추적하여 선택지 & 스탯 해금 만들기
    choices = []
    connections = current_node.get('outputs', {}).get('output_1', {}).get('connections', [])
    
    for conn in connections:
        next_id = conn['node']
        next_node_data = all_nodes[str(next_id)]['data']
        
        req_stat = next_node_data.get('req_stat')
        req_val = int(next_node_data.get('req_val', 0))
        
        is_unlocked = True
        if req_stat:
            char_stat_val = getattr(character, req_stat, 0)
            is_unlocked = char_stat_val >= req_val
        
        choices.append({
            'next_node_id': next_id,
            'text': next_node_data.get('title', '다음으로'),
            'is_unlocked': is_unlocked,
            'req_stat_name': STAT_NAMES.get(req_stat, req_stat), # '근력' 등으로 변환
            'req_val': req_val,
            'stamina_cost': next_node_data.get('stamina_cost', 0)
        })
    outputs = current_node.get('outputs', {})
    
    # 현재 노드에서 뻗어나간 모든 연결선(outputs)을 확인
    for output_key, output_data in outputs.items():
        connections = output_data.get('connections', [])
        for conn in connections:
            next_id = conn['node']
            try:
                next_node = all_nodes[str(next_id)]
                next_node_data = next_node['data']
                
                # 다음 노드에 설정된 진입 조건(스탯)을 확인합니다.
                req_stat = next_node_data.get('req_stat') # 예: 'str', 'dex', 'int' 등
                req_val = int(next_node_data.get('req_val', 0) or 0)
                
                # 스탯 비교 로직
                is_unlocked = True
                if req_stat:
                    # getattr로 캐릭터의 8개 스탯 중 하나를 동적으로 꺼내옵니다.
                    char_stat_val = getattr(character, req_stat, 0)
                    is_unlocked = char_stat_val >= req_val
                
                choices.append({
                    'next_node_id': next_id,
                    'text': next_node_data.get('title', '이동하기'), # 다음 노드의 제목을 선택지 텍스트로 사용
                    'is_unlocked': is_unlocked,
                    'req_stat': req_stat,
                    'req_val': req_val
                })
            except KeyError:
                continue

    context = {
        'map_title': explore_map.title,
        'map_id': map_id,
        'node_data': node_custom_data, 
        'choices': choices,
        'character': character
    }
    return render(request, 'exploration/play.html', context)