# exploration/urls.py
from django.urls import path
from . import views

app_name = 'exploration'

urlpatterns = [
    # ... 기존 URL들 ...

    # 💡 에디터 접속용 URL (예: /editor/1/)
    path('editor/<int:map_id>/', views.map_editor, name='map_editor'),
    
    # (참고) 에디터 저장용 AJAX URL
    path('save_map/', views.save_map, name='save_map'),
    
    # (참고) 플레이 화면 URL
    path('play/<int:map_id>/<str:node_id>/', views.play_node, name='play_node'),
]