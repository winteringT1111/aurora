from django.shortcuts import render

# Create your views here.
# exploration/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import ExplorationMap

def map_editor(request, map_id):
    map_obj = get_object_or_404(ExplorationMap, id=map_id)
    return render(request, 'exploration/editor.html', {
        'map_id': map_id,  # 👈 이 줄이 반드시 있어야 {{ map_id }}가 작동합니다!
        'map_data': json.dumps(map_obj.content_data)
    })

# AJAX 저장 요청 처리
# exploration/views.py

def save_map(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            map_id = data.get('map_id') # JS에서 보낸 ID
            content_data = data.get('content_data')

            # ID를 기준으로 해당 지도를 찾아 데이터를 업데이트합니다.
            map_obj = ExplorationMap.objects.get(id=map_id)
            map_obj.content_data = content_data
            map_obj.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)



# exploration/views.py
def play_exploration(request, node_id):
    # 1. 현재 노드 정보를 가져옴
    map_obj = ExplorationMap.objects.first() # 실제론 유저 세션에서 관리
    node_data = map_obj.content_data['drawflow']['Home']['data'][str(node_id)]
    
    # 2. 다음으로 갈 수 있는 연결 노드들을 찾음
    connections = node_data['outputs']['output_1']['connections']
    choices = []
    for conn in connections:
        next_id = conn['node']
        next_node = map_obj.content_data['drawflow']['Home']['data'][next_id]
        choices.append({'id': next_id, 'title': next_node['data']['title']})

    return render(request, 'exploration/play.html', {
        'current_node': node_data['data'],
        'choices': choices
    })




# exploration/views.py
from django.shortcuts import render, get_object_or_404
from .models import ExplorationMap
import json

# exploration/views.py (해당 함수 부분만 수정)

def play_node(request, node_id):
    map_obj = ExplorationMap.objects.first() 
    data = map_obj.content_data['drawflow']['Home']['data']
    current_node = data.get(str(node_id))
    
    choices = []
    if current_node:
        connections = current_node['outputs']['output_1']['connections']
        for conn in connections:
            target_id = conn['node']
            target_node = data[target_id]
            
            choices.append({
                'id': target_id,
                'title': target_node['data'].get('title', '이동하기'),
                'stamina_cost': target_node['data'].get('stamina', 10),
                # 💡 새로 추가할 부분: 연결된 다음 노드의 행운 조건 데이터를 가져옵니다.
                'req_luck': target_node['data'].get('req_luck', 0) 
            })

    return render(request, 'exploration/play.html', {
        'node': current_node['data'],
        'choices': choices
    })