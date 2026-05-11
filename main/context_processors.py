# context_processors.py
from users.models import CharInfo

def character_context(request):
    if request.user.is_authenticated:
        try:
            # 로그인한 유저의 CharInfo를 가져와 연결된 캐릭터 정보를 리턴
            char_info = CharInfo.objects.get(user=request.user)
            return {'my_char': char_info.char}
        except CharInfo.DoesNotExist:
            return {}
    return {}