from django.urls import path
from . import views

app_name = 'member'

urlpatterns = [
    path('', views.members_view, name='member'),
    path('transfer-item/', views.transfer_item, name='transfer_item'),
    path('<str:name_en>/', views.character, name='character'),
    # urls.py
    

]