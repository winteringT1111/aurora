from django.shortcuts import render, get_object_or_404
# 사용할 모델들을 불러옵니다 (앱 이름은 실제 환경에 맞게 수정하세요)
from member.models import Character 
from main.models import *
from users.models import CharInfo
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def character(request, name_en):
    # 1. 캐릭터 객체 가져오기
    target_char = get_object_or_404(Character, name_en=name_en)
    
    # 기본값 세팅
    inven = []
    is_own_profile = False
    recipient_list = []
    
    # 2. 💡 CharInfo를 통해 오너(user) 찾기
    # .get() 대신 .filter().first()를 쓰면 CharInfo가 아직 없는 캐릭터여도 에러가 나지 않습니다.
    char_info = CharInfo.objects.filter(char=target_char).first()
    owner = char_info.user if char_info else None

    if owner:
        # 3. 💡 인벤토리는 누구나 볼 수 있도록 바깥으로 뺌 (수량이 1개 이상인 것만!)
        inven = Inventory.objects.filter(user=owner, quantity__gt=0).select_related('item')
        
        # 4. 💡 양도 대상 목록은 접속한 사람이 '오너'일 때만 세팅
        if request.user.is_authenticated and request.user == owner:
            is_own_profile = True
            recipient_list = Character.objects.exclude(id=target_char.id).order_by('name_kr')

    context = {
        'charname': target_char.name_en, 
        'charinfo': char_info,           # CharInfo 정보도 템플릿에 같이 넘겨줍니다 (출석수 등 활용 가능)
        'char': target_char,
        'items': inven,                  # 이제 누구나 인벤토리를 볼 수 있습니다.
        'is_own_profile': is_own_profile,# 내가 오너일 때만 True
        'recipient_list': recipient_list,# 내가 오너일 때만 리스트가 채워짐
    }

    return render(request, "charac/character.html", context)


def members_view(request):
    # 💡 .all() 대신 .order_by('정렬할_필드명')을 쓰면 가나다순(오름차순)으로 가져옵니다.
    characters = Character.objects.order_by('name_kr')
    
    return render(request, 'charac/members.html', {'characters': characters})

import json
from django.db import transaction


@login_required
@transaction.atomic
def transfer_item(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            recipient_id = data.get('recipient_id')
            quantity = int(data.get('quantity', 1))
            message = data.get('message', '')

            # 1. 데이터 확인
            item = get_object_or_404(Item, id=item_id)
            target_char = get_object_or_404(Character, id=recipient_id)
            
            # 2. 내 인벤토리에서 재료 보유 확인 및 차감
            my_inv = Inventory.objects.get(user=request.user, item=item)
            
            if my_inv.quantity < quantity:
                return JsonResponse({'success': False, 'msg': '보유 수량이 부족합니다.'})

            # 내 인벤토리 차감
            my_inv.quantity -= quantity
            if my_inv.quantity == 0:
                my_inv.delete()
            else:
                my_inv.save()

            Gift.objects.create(
                sender=request.user,
                receiver=target_char,
                item=item,
                quantity=quantity,
                message=message,
                is_anonymous=False,
                is_claimed=False
            )

            return JsonResponse({
                'success': True, 
                'msg': f'{target_char.name_kr}님에게 [{item.name}] {quantity}개를 양도했습니다!'
            })

        except Inventory.DoesNotExist:
            return JsonResponse({'success': False, 'msg': '아이템을 보유하고 있지 않습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})