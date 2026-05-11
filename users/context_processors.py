from  users.models import CharInfo

def char_info_context(request):
    if request.user.is_authenticated and int(request.user.is_superuser) is 0:
        getUser = request.user
        userinfo = CharInfo.objects.get(user=getUser)
        return {"charInfo": userinfo}
    else:
        return {}