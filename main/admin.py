from django.contrib import admin

# Register your models here.
from main.models import *
from member.models import *


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    # 1. 엑셀의 열(Column)처럼 리스트에서 보여줄 항목들
    list_display = ('id', 'name', 'category', 'price', 'is_sellable')
    
    # 2. 클릭했을 때 상세 페이지로 넘어갈 수 있게 해주는 항목
    list_display_links = ('id', 'name')
    
    # 3. 우측에 나타나는 필터 (카테고리별, 판매여부별로 모아보기 가능)
    list_filter = ('category', 'is_sellable')
    
    # 4. 검색창에서 검색할 기준 (아이템 이름으로 검색)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # 1. 레시피 목록에서 한눈에 볼 항목들
    list_display = ('id', 'itemName', 'category', 'material1', 'material2', 'material3','material4','discovered', 'discoverer')
    
    list_display_links = ('id', 'itemName')
    
    # 2. 우측 필터 (카테고리별, 발견여부별 모아보기)
    list_filter = ('category', 'discovered')
    
    # 3. 💡 강력한 검색 기능! 결과물 이름뿐만 아니라 "재료"로도 검색 가능하게 설정
    search_fields = ('itemName', 'material1', 'material2', 'material3', 'material4', 'discoverer')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    # 1. 목록에서 보여줄 필드들 (번호, 한국어 이름, 영어 이름, 골드, 에너지)
    list_display = ('id', 'name_kr', 'name_en', 'gold', 'energy')
    
    # 2. 목록에서 바로 수정 가능하게 만들기 (클릭 한 번으로 수치 변경 가능)
    # ⚠️ 주의: list_display에 포함된 필드여야 하며, list_display_links에 포함된 필드는 안 됩니다.
    list_editable = ('gold', 'energy')
    
    # 3. 이름으로 검색 가능하게 설정
    search_fields = ('name_kr', 'name_en')
    
    # 4. 수치별로 필터링 (골드나 에너지가 특정 범위인 캐릭터 찾기용)
    list_filter = ('gold', 'energy')
    
    # 5. 한 페이지에 보여줄 캐릭터 수 (기본 100개로 설정)
    list_per_page = 100
    
    # 상세 페이지에서 필드 순서 정렬
    fields = ('name_kr', 'name_en', 'gold', 'energy')



@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    # 1. 목록에서 한눈에 볼 항목들 (번호, 보낸사람, 받는사람, 아이템, 수량, 수령여부, 보낸시간)
    list_display = ('id', 'sender', 'receiver', 'item', 'quantity', 'is_claimed', 'created_at')
    
    # 2. 클릭해서 상세 페이지로 들어갈 수 있는 링크
    list_display_links = ('id', 'item')
    
    # 3. 우측 필터 (수령 여부, 익명 여부, 보낸 날짜별 모아보기)
    list_filter = ('is_claimed', 'is_anonymous', 'created_at')
    
    # 4. 💡 강력한 검색 기능! 
    # 주의: 다른 모델과 연결된(ForeignKey) 데이터의 이름을 검색할 때는 언더바 2개(__)를 씁니다.
    search_fields = (
        'sender__username',     # 보낸 유저의 아이디로 검색
        'receiver__name_kr',    # 받는 캐릭터의 한국어 이름으로 검색
        'item__name',           # 아이템 이름으로 검색
        'message'               # 메시지 내용으로 검색
    )
    
    # 5. 목록 화면에서 체크박스 클릭 한 번으로 '수령 완료/취소' 처리 가능
    list_editable = ('is_claimed',)
    
    # 6. 한 페이지에 보여줄 개수
    list_per_page = 50



from django.contrib import admin
from .models import Inventory # Inventory 모델 임포트

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    # 1. 목록에서 한눈에 볼 항목 (소유자, 아이템 이름, 수량)
    list_display = ('id', 'user', 'item', 'quantity')
    
    # 2. 클릭해서 상세 페이지로 들어갈 항목
    list_display_links = ('id', 'item')
    
    # 3. 우측 필터 (유저별로 모아보기, 아이템별로 모아보기)
    # 아이템의 카테고리별로도 필터링하고 싶다면 'item__category'를 추가하세요.
    list_filter = ('user', 'item')
    
    # 4. 검색 기능 (유저 아이디나 아이템 이름으로 검색)
    search_fields = ('user__username', 'item__name')
    
    # 5. 수량을 목록에서 바로 수정 가능하게 설정 (GM 전용 쾌속 수정)
    list_editable = ('quantity',)
    
    # 6. 한 페이지에 표시할 데이터 수
    list_per_page = 50