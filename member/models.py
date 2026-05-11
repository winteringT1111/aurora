from django.db import models
from django.conf import settings

class Character(models.Model):
    name_kr = models.CharField(max_length=50, verbose_name="이름 (한글)")
    name_en = models.CharField(max_length=100, verbose_name="이름 (영문)")
    catchphrase = models.CharField(max_length=100, verbose_name="캐치프레이즈")
    quote = models.CharField(max_length=100, verbose_name="한마디")

    # =========================================
    # 3. 신상 정보 (Profile)
    # =========================================
    origin = models.CharField(max_length=50, verbose_name="출신지")
    gender = models.CharField(max_length=20, verbose_name="성별")
    age = models.CharField(max_length=30, verbose_name="나이") # '432세', '불명' 등 입력 가능
    race = models.CharField(max_length=30, verbose_name="종족")
    animal_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="동물 객체 (수인의 경우)")
    height = models.CharField(max_length=30, verbose_name="신장") # '178cm'
    weight = models.CharField(max_length=30, verbose_name="체중")

    # =========================================
    # 4. 성격 및 설정 서술 (Descriptions)
    # =========================================
    keyword1 = models.CharField(max_length=20, verbose_name="성격 키워드 1")
    keyword2 = models.CharField(max_length=20, verbose_name="성격 키워드 2")
    keyword3 = models.CharField(max_length=20, verbose_name="성격 키워드 3")
    
    appearance = models.TextField(verbose_name="외관 서술")
    personality = models.TextField(verbose_name="성격 서술")
    other_info = models.TextField(verbose_name="특징 서술")

    # =========================================
    # 5. 스탯 (Stats)
    # =========================================
    stat_str = models.PositiveIntegerField(default=0, verbose_name="근력")
    stat_agi = models.PositiveIntegerField(default=0, verbose_name="민첩")
    stat_int = models.PositiveIntegerField(default=0, verbose_name="지능")
    stat_luk = models.PositiveIntegerField(default=0, verbose_name="행운")
    stat_rep = models.PositiveIntegerField(default=0, verbose_name="평판")
    stat_good = models.PositiveIntegerField(default=0, verbose_name="선의")
    stat_mag = models.PositiveIntegerField(default=0, verbose_name="마력")
    stat_div = models.PositiveIntegerField(default=0, verbose_name="신성력")

    gold = models.IntegerField(default=100, verbose_name="골드")
    energy = models.IntegerField(default=100, verbose_name="활력")

    def __str__(self):
        return f"{self.name_kr} ({self.name_en})"

    class Meta:
        verbose_name = "캐릭터"