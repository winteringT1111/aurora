from django.contrib import admin
from main.models import *
from member.models import *
from users.models import *
from exploration.models import ExplorationMap

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_sellable')
    list_display_links = ('id', 'name')
    list_filter = ('category', 'is_sellable')
    list_editable = ('price', 'is_sellable')
    search_fields = ('name',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'itemName', 'category', 'material1', 'material2', 'material3','material4','discovered', 'discoverer')
    list_display_links = ('id', 'itemName')
    list_filter = ('category', 'discovered')
    
    # 💡 수정: discoverer가 User 모델 등과 연결된 외래키라면 __username을 붙여야 에러가 안 납니다!
    # (만약 Character 모델과 연결되었다면 discoverer__name_kr 로 변경해 주세요)
    search_fields = ('itemName', 'material1', 'material2', 'material3', 'material4', 'discoverer__username')

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_kr', 'name_en', 'gold', 'energy')
    list_editable = ('gold', 'energy')
    search_fields = ('name_kr', 'name_en')
    list_filter = ('gold', 'energy')
    list_per_page = 100
    fields = ('name_kr', 'name_en', 'gold', 'energy')

@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'item', 'quantity', 'is_claimed', 'created_at')
    list_display_links = ('id', 'item')
    list_filter = ('is_claimed', 'is_anonymous', 'created_at')
    search_fields = ('sender__username', 'receiver__name_kr', 'item__name', 'message')
    list_editable = ('is_claimed',)
    list_per_page = 50

# 🚨 수정: 중간에 끼어있던 불필요한 import 구문을 삭제했습니다.
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item', 'quantity')
    list_display_links = ('id', 'item')
    list_filter = ('user', 'item')
    search_fields = ('user__username', 'item__name')
    list_editable = ('quantity',)
    list_per_page = 50

@admin.register(ExplorationMap)
class ExplorationMapAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')

@admin.register(CharInfo)
class CharInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'char', 'attendance_count', 'today_attended', 'attendance_date')
    list_display_links = ('id', 'user')
    list_filter = ('today_attended', 'attendance_date')
    search_fields = ('user__username', 'char__name_kr', 'char__name_en')
    list_editable = ('attendance_count', 'today_attended')
    list_per_page = 50