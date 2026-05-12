import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Item, Recipe
from member.models import Character
from .models import Inventory
from users.models import CharInfo
from django.db import transaction
from django.views.decorators.http import require_POST
from main.models import Inventory, Gift
from main.models import Item, Inventory, Gift

def main_page(request):
    return render(request, "main.html")



@login_required(login_url='/login')
def store(request):
    """상점 메인 화면 렌더링"""
    # 1. 판매용 아이템 가져오기
    items_qs = Item.objects.filter(is_sellable=True)
    
    items_data = []
    for item in items_qs:
        cat_name = str(item.category).strip() if item.category else '미분류'
        items_data.append({
            'id': item.id,
            'name': item.name,
            'category': cat_name,
            'category_display': item.get_category_display() if hasattr(item, 'get_category_display') else cat_name,
            'price': item.price,
            'desc': item.description,
            'img': item.image.url if hasattr(item, 'image') and item.image else f'/static/img/도트/{item.name}.png'
        })
    
    # 2. 내 캐릭터 정보와 골드 가져오기
    try:
        mechar_info = CharInfo.objects.get(user=request.user)
        user_gold = mechar_info.char.gold # Character 모델의 gold 필드 사용
    except CharInfo.DoesNotExist:
        user_gold = 0
    
    # 3. 선물 대상 목록 (나를 제외한 모든 캐릭터)
    characters = Character.objects.all()

    context = {
        'items_data': items_data,
        'user_gold': user_gold,
        'characters': characters,
    }
    return render(request, "store.html", context)


@login_required
@transaction.atomic
def buy_item(request):
    """아이템 구매 처리"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            qty = int(data.get('qty', 1))
            
            item = Item.objects.get(id=item_id)
            total_price = item.price * qty
            
            # 💡 유저의 캐릭터 및 골드 정보 가져오기
            char_info = CharInfo.objects.get(user=request.user)
            my_char = char_info.char
            
            if my_char.gold >= total_price:
                # 1. 골드 차감 (캐릭터 모델에서)
                my_char.gold -= total_price
                my_char.save()
                
                # 2. 인벤토리에 아이템 추가
                inv_slot, created = Inventory.objects.get_or_create(
                    user=request.user, 
                    item=item, 
                    defaults={'quantity': 0}
                )
                inv_slot.quantity += qty
                inv_slot.save()
                
                return JsonResponse({
                    'success': True, 
                    'remain_gold': my_char.gold, 
                    'msg': f'[{item.name}] {qty}개를 구매했습니다.'
                })
            else:
                return JsonResponse({'success': False, 'msg': '보유한 골드가 부족합니다.'})
                
        except (Item.DoesNotExist, CharInfo.DoesNotExist):
            return JsonResponse({'success': False, 'msg': '정보를 찾을 수 없습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})

@login_required
@transaction.atomic
def gift_item(request):
    """아이템 선물 처리"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            qty = int(data.get('qty', 1))
            target_id = data.get('target_id')
            message = data.get('message', '')
            is_anon = data.get('is_anon', False)
            
            item = Item.objects.get(id=item_id)
            target_char = Character.objects.get(id=target_id)
            total_price = item.price * qty
            
            char_info = CharInfo.objects.get(user=request.user)
            my_char = char_info.char
            
            if my_char.gold >= total_price:
                # 1. 골드 차감
                my_char.gold -= total_price
                my_char.save()
                
                # 2. 선물 데이터 생성 (GiftBox 페이지로 전달됨)
                Gift.objects.create(
                    sender=request.user,
                    receiver=target_char,
                    item=item,
                    quantity=qty,
                    message=message,
                    is_anonymous=is_anon
                )
                
                return JsonResponse({
                    'success': True, 
                    'remain_gold': my_char.gold, 
                    'msg': f'{target_char.name_kr}님에게 선물을 보냈습니다!'
                })
            else:
                return JsonResponse({'success': False, 'msg': '골드가 부족합니다.'})
                
        except (Item.DoesNotExist, Character.DoesNotExist, CharInfo.DoesNotExist):
            return JsonResponse({'success': False, 'msg': '대상 정보를 찾을 수 없습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})


from datetime import date, timedelta
from django.utils import timezone
import random

@login_required(login_url='/login')
def supply(request):
    getUser = request.user
    charinfo = CharInfo.objects.get(user=getUser)
    userinfo = charinfo.char
    
    current_time = timezone.localtime(timezone.now())
    current_hour = current_time.hour
    today_date = current_time.date()
    
    if request.method == "POST":
        if 0 <= current_hour < 20:
            if charinfo.attendance_date == today_date:
                show_modal = "modal2"
                modal_message = "이미 오늘의 보급을 수령했습니다."
                item_name = ""
                is_success = False
            else:
                # 1. 기본 재화 지급 (골드 추가 및 에너지 100으로 MAX 충전)
                userinfo.gold += 100 
                userinfo.energy = 100  # 💡 에너지를 최대치(100)로 꽉 채워줍니다.
                userinfo.save()        # 💡 [중요] 변경된 캐릭터 정보를 DB에 저장!
                
                # 2. 랜덤 아이템 지급 로직
                items = Item.objects.all()
                item_name = ""
                if items.exists():
                    random_item = random.choice(items) # 아이템 중 1개 무작위 뽑기
                    
                    # 인벤토리에 아이템 추가 (없으면 만들고, 있으면 수량 +1)
                    inventory_item, created = Inventory.objects.get_or_create(
                        user=getUser, 
                        item=random_item,
                        defaults={'quantity': 0}
                    )
                    inventory_item.quantity += 1
                    inventory_item.save()
                    item_name = random_item.name # 모달창에 띄워줄 아이템 이름
                
                # 3. 출석 기록 업데이트
                charinfo.attendance_date = today_date
                charinfo.today_attended = True
                charinfo.attendance_count += 1
                charinfo.save()
                
                show_modal = "modal1"
                modal_message = "오늘의 보급품이 도착했습니다!"
                is_success = True
                
        else:
            show_modal = "modal2"
            modal_message = "보급 신청이 가능한 시각이 아닙니다. (06:00 ~ 19:59)"
            item_name = ""
            is_success = False
            
        return JsonResponse({
            'show_modal': show_modal, 
            'modal_message': modal_message,
            'is_success': is_success,        # 성공 여부 추가
            'item_name': item_name,          # 뽑힌 랜덤 아이템 이름 추가
            'attendance_count': charinfo.attendance_count,
            'today_attended': charinfo.today_attended 
        })
    
    context = {
        'character': userinfo,
        'attendance_count': charinfo.attendance_count,
        'today_attended': charinfo.today_attended 
    }
    
    return render(request, "supply.html", context)








@login_required(login_url='/login')
def recipe(request):
    inven = Inventory.objects.filter(user=request.user, quantity__gt=0)
    
    try:
        char_info = CharInfo.objects.get(user=request.user)
        token = char_info.char.gold 
    except CharInfo.DoesNotExist:
        token = 0
        
    # --- ✨ 레시피 북을 위한 데이터 가공 ---
    all_recipes_data = []
    for recipe_obj in Recipe.objects.all().order_by('itemName'):
        # 💡 수정됨: material 1~4 필드를 하나로 모으되, 빈 칸(None)은 제외합니다.
        materials = [
            recipe_obj.material1, 
            recipe_obj.material2, 
            recipe_obj.material3, 
            recipe_obj.material4
        ]
        ingredients = [m for m in materials if m] # 값이 있는 재료만 리스트로 만듦

        discoverer_first_name = ""
        if recipe_obj.discoverer:
            discoverer_first_name = recipe_obj.discoverer.split(' ')[0]

        all_recipes_data.append({
            'recipe': recipe_obj,
            'ingredients': ingredients,
            'discoverer_first_name': discoverer_first_name 
        })
        
    context = {
        'inventory_items': inven,
        'token': token,
        'all_recipes': all_recipes_data,
    }
    return render(request, "recipe.html", context)

from collections import Counter
import json
import ast

from django.db import transaction # 💡 꼭 맨 위에 임포트 해주세요!
from collections import Counter

@require_POST
@login_required
@transaction.atomic # 💡 추가됨: 중간에 에러 나면 재료 증발을 막고 전부 원상복구
def combine(request):
    try:
        data = json.loads(request.body)
        selected_items = data.get('selected_items', [])
        
        # 💡 유저가 올린 재료의 개수를 셉니다 (예: {'약초': 2})
        required_counts = Counter(selected_items)
        
        user = request.user
        char_info = CharInfo.objects.get(user=user)

        # 1. 경험치 부족 확인
        if char_info.char.energy < 3:
            return JsonResponse({'error': '경험치가 부족합니다.'}, status=400)
        
        # 2. 인벤토리 재료 보유 여부 및 수량 확인
        for item_name, count in required_counts.items():
            inv_item = Inventory.objects.filter(user=user, item__name=item_name).first()
            if not inv_item or inv_item.quantity < count:
                return JsonResponse({'error': f"'{item_name}' 재료가 부족합니다."}, status=400)

        # 3. 💡 조합법 확인 (수정됨: 완벽한 개수 비교)
        found_recipe = None
        for recipe_obj in Recipe.objects.all():
            materials = [
                recipe_obj.material1, 
                recipe_obj.material2, 
                recipe_obj.material3, 
                recipe_obj.material4
            ]
            # DB 레시피의 재료 목록에서 빈칸(None)을 빼고 개수를 셉니다
            recipe_counter = Counter([m for m in materials if m])
            
            # 유저가 올린 재료(종류+개수)와 레시피가 100% 똑같을 때만 성공!
            if required_counts == recipe_counter:
                found_recipe = recipe_obj
                break

        # --- 4. 재료 및 비용 차감 (성공/실패 공통) ---
        char_info.char.energy -= 3
        char_info.char.save()

        for item_name, count in required_counts.items():
            inv_item = Inventory.objects.get(user=user, item__name=item_name)
            inv_item.quantity -= count
            if inv_item.quantity == 0:
                inv_item.delete()
            else:
                inv_item.save()

        # 5. 결과 처리
        if found_recipe:
            # 성공 로직
            if not found_recipe.discovered:
                message = f"『 {found_recipe.itemName} 』조합에 최초로 성공했습니다!"
                found_recipe.discovered = True
                found_recipe.discoverer = user.username
                found_recipe.save()
            else:
                message = f"『 {found_recipe.itemName} 』조합에 성공했습니다!"
            
            result_item = Item.objects.get(name=found_recipe.itemName)
            inv_slot, created = Inventory.objects.get_or_create(user=user, item=result_item, defaults={'quantity': 0})
            inv_slot.quantity += 1
            inv_slot.save()
            
            result_image = f"{found_recipe.itemName}.png"
            result_status = "success"
        else:
            # 실패 로직
            message = "아무 일도 일어나지 않았습니다..."
            result_image = "망한 아이템.png"
            result_status = "failure"

            failed_item = Item.objects.get(name="망한 아이템")
            inv_slot, created = Inventory.objects.get_or_create(user=user, item=failed_item, defaults={'quantity': 0})
            inv_slot.quantity += 1
            inv_slot.save()

        return JsonResponse({'result': result_status, 'image': result_image, 'message': message})

    except Item.DoesNotExist:
        return JsonResponse({'error': 'DB에 해당 이름의 아이템 원본이 존재하지 않습니다. 상점 아이템 목록을 확인해주세요!'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    









    # 1. 선물함 화면 렌더링
@login_required(login_url='/login')
def giftbox_view(request):
    try:
        # 내 유저 계정과 연결된 캐릭터(CharInfo) 찾기
        char_info = CharInfo.objects.get(user=request.user)
        my_char = char_info.char
        
        # 내가 받은 선물 중 아직 수령하지 않은(is_claimed=False) 선물만 최신순으로 가져오기
        gifts = Gift.objects.filter(receiver=my_char, is_claimed=False).order_by('-created_at')
        
    except CharInfo.DoesNotExist:
        gifts = []

    return render(request, "giftbox.html", {'gifts': gifts})

# 2. 보관하기 버튼 클릭 시 인벤토리로 이동 (AJAX 통신용)
@require_POST
@login_required
def claim_gift(request):
    try:
        data = json.loads(request.body)
        gift_id = data.get('gift_id')
        
        # 해당 선물 찾기
        gift = Gift.objects.get(id=gift_id, is_claimed=False)
        
        # 본인이 받은 선물이 맞는지 한 번 더 검증
        char_info = CharInfo.objects.get(user=request.user)
        if gift.receiver != char_info.char:
            return JsonResponse({'success': False, 'msg': '본인의 선물만 수령할 수 있습니다.'})
        
        # ✨ 인벤토리에 아이템 추가
        inv_slot, created = Inventory.objects.get_or_create(
            user=request.user, 
            item=gift.item, 
            defaults={'quantity': 0}
        )
        inv_slot.quantity += gift.quantity
        inv_slot.save()
        
        # ✨ 선물 수령 처리 (True로 바꾸면 선물함 목록에서 사라짐)
        gift.is_claimed = True
        gift.save()
        
        return JsonResponse({'success': True, 'msg': f"'{gift.item.name}'을(를) 인벤토리에 보관했습니다!"})

    except Gift.DoesNotExist:
        return JsonResponse({'success': False, 'msg': '이미 수령했거나 존재하지 않는 선물입니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'msg': str(e)})