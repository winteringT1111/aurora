from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # 에디터 화면 (예: /exploration/editor/1/)
    path('', views.main_page, name='main_page'),
    path('supply', views.supply, name='supply'),
    path('store/', views.store, name='store'),
    path('recipe/', views.recipe, name='recipe'),
    path('combine/', views.combine, name='combine'),
    path('giftbox/', views.giftbox_view, name='giftbox'),
    path('giftbox/claim/', views.claim_gift, name='claim_gift'),
    path('store/buy/', views.buy_item, name='buy_item'),
    path('store/gift/', views.gift_item, name='gift_item'),
]