# exploration/urls.py
from django.urls import path
from . import views

app_name = 'exploration'

urlpatterns = [
    # 에디터 화면 (예: /exploration/editor/1/)
    path('editor/<int:map_id>/', views.map_editor, name='map_editor'),
    # 저장 요청용 AJAX 경로
    path('save_map/', views.save_map, name='save_map'),
    path('play/<str:node_id>/', views.play_node, name='play_node'),
]