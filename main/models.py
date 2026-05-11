from django.db import models

# Create your models here.
from django.db import models

class Item(models.Model):
    # 1. 아이템 종류 카테고리 (원하시는 만큼 추가 가능)
    CATEGORY_CHOICES = (
        ('ESSENCE', '정수'),
        ('FOOD', '음식'),
        ('CONSUMABLE', '소모품'),
        ('EQUIPMENT', '소지품'),
        ('SPECIAL', '특수 아이템'),
    )

    # 기본 정보
    name = models.CharField(max_length=100, verbose_name="아이템명")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="종류")
    description = models.TextField(verbose_name="설명")
    price = models.PositiveIntegerField(default=0, verbose_name="가격(G)") # 비매품이면 0

    # 2. 획득처 및 속성 구별 플래그 (True/False 로 구별)
    is_sellable = models.BooleanField(default=False, verbose_name="상점 판매 여부")
    is_investigation_reward = models.BooleanField(default=False, verbose_name="조사 보상 여부")
    is_craft_result = models.BooleanField(default=False, verbose_name="조합 결과물 여부")
    
    # 3. 추가 확장 필드 (세계관 및 시스템용)
    origin = models.CharField(max_length=50, blank=True, null=True, verbose_name="특산품 출처") # ex: '발테리온', '노르드바인'
    
    # 4. 특수 효과 (용사 기여도 증감 등)
    # effect_type을 지정하고, effect_value로 수치를 조절합니다.
    EFFECT_CHOICES = (
        ('NONE', '효과 없음'),
        ('CONTRIBUTION_UP', '용사 기여도 증가'),
        ('CONTRIBUTION_DOWN', '용사 기여도 감소'),
        ('HP_RECOVERY', '체력 회복'),
    )
    effect_type = models.CharField(max_length=30, choices=EFFECT_CHOICES, default='NONE', verbose_name="특수 효과 종류")
    effect_value = models.IntegerField(default=0, verbose_name="특수 효과 수치")

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"

    class Meta:
        verbose_name = "아이템"
        verbose_name_plural = "아이템 목록"



from django.db import models
from django.conf import settings
# from .models import Item, Character (이미 상단에 import 되어 있다면 생략)

# =========================================
# 인벤토리 모델 (Inventory)
# =========================================
class Inventory(models.Model):
    # 💡 시스템 설정에 따라 user 대신 character를 연결하셔도 됩니다.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory', verbose_name="플레이어")
    item = models.ForeignKey('Item', on_delete=models.CASCADE, verbose_name="보유 아이템")
    
    quantity = models.PositiveIntegerField(default=1, verbose_name="수량")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최근 변동일")

    class Meta:
        # 💡 핵심: 한 유저가 같은 아이템을 중복으로 여러 줄 가지지 않고, '수량'만 오르내리도록 설정
        unique_together = ('user', 'item')
        verbose_name = "인벤토리"
        verbose_name_plural = "인벤토리 목록"

    def __str__(self):
        return f"[{self.user.username}] {self.item.name} x{self.quantity}"

    # 수량 증가/감소를 위한 헬퍼 메서드 (views.py에서 사용하기 편하게)
    def add_item(self, amount=1):
        self.quantity += amount
        self.save()

    def remove_item(self, amount=1):
        if self.quantity >= amount:
            self.quantity -= amount
            if self.quantity == 0:
                self.delete() # 수량이 0이 되면 인벤토리 창에서 사라짐
            else:
                self.save()
            return True
        return False



from member.models import Character # 앱 이름에 맞게 수정해주세요
from main.models import Item        # 앱 이름에 맞게 수정해주세요

class Gift(models.Model):
    # 선물을 보낸 사람 (유저 계정)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_gifts')
    # 선물을 받는 대상 (캐릭터)
    receiver = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='received_gifts')
    
    # 선물 내용물
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    # 부가 정보
    message = models.TextField(blank=True, null=True, verbose_name="메시지")
    is_anonymous = models.BooleanField(default=False, verbose_name="익명 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="받은 날짜")
    
    # 수령 여부 (True가 되면 선물함에서 사라지고 인벤토리로 감)
    is_claimed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver.name_kr} ({self.item.name})"




class Recipe(models.Model):
    # 1. 번호: 장고가 기본으로 제공하는 'id' 필드를 사용하므로 생략합니다.

    # 2. 아이템 (결과물 이름)
    itemName = models.CharField(max_length=100, unique=True, verbose_name="아이템")
    
    # 3. 카테고리 (예: '무기', '포션' 등)
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="카테고리")
    
    # 4. 설명
    desc = models.TextField(blank=True, null=True, verbose_name="설명")

    # 5. 재료 1~4 (재료가 2개만 들어가는 레시피도 있으므로 2, 3, 4는 비워둘 수 있게 설정)
    material1 = models.CharField(max_length=100, blank=True, null=True, verbose_name="재료1")
    material2 = models.CharField(max_length=100, blank=True, null=True, verbose_name="재료2")
    material3 = models.CharField(max_length=100, blank=True, null=True, verbose_name="재료3")
    material4 = models.CharField(max_length=100, blank=True, null=True, verbose_name="재료4")

    # 6. 기존 로직 연동을 위한 최초 발견 시스템
    discovered = models.BooleanField(default=False, verbose_name="최초 발견 여부")
    discoverer = models.CharField(max_length=100, null=True, blank=True, verbose_name="최초 발견자")

    def __str__(self):
        return f"[{self.id}] {self.itemName}" # 관리자 페이지에서 "번호 아이템명"으로 보이게 설정