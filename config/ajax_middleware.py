# ajax_middleware.py
from django.http import HttpResponse

class AjaxPartialMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # 그냥 통과 — JS에서 직접 파싱
        return response