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

from django.contrib import admin
from .models import Character

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    # 1. 목록 화면에 보여줄 필드들 (id를 맨 앞에 두고, 서술형 TextField는 뺐습니다)
    list_display = (
         'id','name_kr', 'name_en', 
        
        'gold', 'energy','points'
    )
    
    # 2. 목록 화면에서 마우스 클릭으로 바로 수정할 필드들 (id 제외하고 전부 등록)
    list_editable = (
        'name_kr', 'name_en', 
        
        'gold', 'energy','points'
    )
    
    # 3. 검색 기능 (한글 이름, 영어 이름으로 검색 가능)
    search_fields = ('name_kr', 'name_en')
    
    # 4. 우측 필터 사이드바 (종족이나 성별로 필터링하면 관리하기 편합니다)
    list_filter = ('race', 'gender')
    
    # 5. 한 페이지에 보여줄 개수
    list_per_page = 100
    
    # 6. 개별 캐릭터를 클릭해 들어갔을 때(상세 페이지) 보여줄 레이아웃 그룹화
    fieldsets = (
        ('기본 정보', {
            'fields': ('name_kr', 'name_en', 'catchphrase', 'quote')
        }),
        ('신상 정보', {
            'fields': ('origin', 'gender', 'age', 'race', 'animal_type', 'height', 'weight')
        }),
        ('성격 및 설정 서술', {
            'fields': ('keyword1', 'keyword2', 'keyword3', 'appearance', 'personality', 'other_info')
        }),
        ('스탯 및 재화', {
            'fields': ('stat_str', 'stat_agi', 'stat_int', 'stat_luk', 'stat_rep', 'stat_good', 'stat_mag', 'stat_div', 'gold', 'energy')
        }),
    )

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
