# exploration/models.py
from django.db import models

class ExplorationMap(models.Model):
    title = models.CharField(max_length=200) # 맵 이름 (예: 안개 낀 고성)
    # Drawflow의 전체 데이터를 저장하는 필드
    # JSONField를 쓰면 파이썬 딕셔너리처럼 다루기 편합니다.
    content_data = models.JSONField(verbose_name="노드 데이터") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title