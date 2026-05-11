from django.db import models
from django.conf import settings


class CharInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    attendance_date = models.DateField(null=True, blank=True) 
    attendance_count = models.IntegerField(default=0)  # 누적 출석 일 수 추가
    today_attended = models.BooleanField(default=False)  # 금일 출석 여부 추가
    chap = models.IntegerField(default=0)
    char = models.ForeignKey('member.Character', on_delete=models.CASCADE)
