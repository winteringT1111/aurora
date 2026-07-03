import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Item, UseLog
from member.models import Character
from .models import Inventory
from users.models import CharInfo
from django.db import transaction
from django.views.decorators.http import require_POST
from main.models import Inventory, Gift
from main.models import Item, Inventory, Gift

def main_page(request):
    top3 = Character.objects.order_by('-points')[:3]
    bottom3 = Character.objects.order_by('points')[:3]

    context = {
        'top3': top3,
        'bottom3': bottom3,
    }
    return render(request, "main.html", context)



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
        if 6 <= current_hour < 20:
            if charinfo.attendance_date == today_date:
                show_modal = "modal2"
                modal_message = "이미 오늘의 보급을 수령했습니다."
                item_name = ""
                is_success = False
            else:
                # 1. 기본 재화 지급 (골드 추가 및 에너지 100으로 MAX 충전)
                userinfo.gold += 100 
                if userinfo.energy > 200:
                    pass
                else:
                    userinfo.energy = 200
                    userinfo.save()
                
                # 2. 랜덤 아이템 지급 로직
                excluded_items = ['봉인의 지팡이', '역대 성녀의 초상화', '봉인의 성유물']
                items = Item.objects.exclude(name__in=excluded_items)
                item_name = ""
                if items.exists():
                    random_item = random.choice(list(items))
                    
                    # 인벤토리에 아이템 추가 (없으면 만들고, 있으면 수량 +1)
                    inventory_item, created = Inventory.objects.get_or_create(
                        user=getUser, 
                        item=random_item,
                        defaults={'quantity': 0}
                    )
                    inventory_item.quantity += 1
                    inventory_item.save()
                    item_name = random_item.name
                
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
            'is_success': is_success,
            'item_name': item_name,
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
    









@login_required
def giftbox_view(request):
    try:
        char = CharInfo.objects.get(user=request.user).char
    except CharInfo.DoesNotExist:
        return render(request, 'giftbox.html', {'gifts': [], 'sent_gifts': []})

    # 받은 선물
    gifts = Gift.objects.filter(
        receiver=char
    ).order_by('is_claimed', '-created_at')

    # ✅ 보낸 선물
    sent_gifts = Gift.objects.filter(
        sender=request.user
    ).order_by('-created_at')

    return render(request, 'giftbox.html', {
        'gifts': gifts,
        'sent_gifts': sent_gifts,
    })



# 2. 보관하기 버튼 클릭 시 인벤토리로 이동 (AJAX 통신용)
@login_required
@transaction.atomic
def claim_gift(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        gift_id = data.get('gift_id')

        try:
            char = CharInfo.objects.get(user=request.user).char  # ✅ 수정
            gift = Gift.objects.get(id=gift_id, receiver=char, is_claimed=False)

            inv, created = Inventory.objects.get_or_create(
                user=request.user,
                item=gift.item,
                defaults={'quantity': 0}
            )
            inv.quantity += gift.quantity
            inv.save()

            gift.is_claimed = True
            gift.save()

            return JsonResponse({'success': True, 'msg': f'[{gift.item.name}] x{gift.quantity} 보관 완료!'})

        except CharInfo.DoesNotExist:
            return JsonResponse({'success': False, 'msg': '캐릭터 정보를 찾을 수 없습니다.'})
        except Gift.DoesNotExist:
            return JsonResponse({'success': False, 'msg': '선물을 찾을 수 없습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'msg': str(e)})












@login_required
@require_POST
def use_item_view(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        item_name = data.get('item_name')
        
        user = request.user
        charinfo = CharInfo.objects.get(user=user)
        character = charinfo.char  # 내 캐릭터 스탯 모델 객체

        # 1. 수량 검증 검사
        inv_item = Inventory.objects.filter(user=user, item_id=item_id, quantity__gt=0).first()
        if not inv_item:
            return JsonResponse({'success': False, 'message': '인벤토리에 해당 아이템 수량이 부족합니다.'})

        # ========================================================
        # 💡 1. 성해의 파편수 처리
        # ========================================================
        if item_name == "성해의 파편수":
            reallocated = data.get('reallocated_stats')
            if not reallocated:
                return JsonResponse({'success': False, 'message': '재분배된 스탯 데이터가 누락되었습니다.'})
            
            # 원래 가지고 있던 원본 총합 스탯 검증 검사 (치트 방지)
            original_total = (character.stat_str + character.stat_agi + character.stat_int + character.stat_luk +
                              character.stat_rep + character.stat_good + character.stat_mag + character.stat_div)
            
            new_total = sum(int(v) for v in reallocated.values())
            if original_total != new_total:
                return JsonResponse({'success': False, 'message': '포인트 변조가 감지되었습니다. 총합이 일치하지 않습니다.'})

            for k, v in reallocated.items():
                if int(v) < 1:
                    return JsonResponse({'success': False, 'message': '모든 스탯의 최솟값은 1입니다.'})

            # 검증 통과 시 일괄 주입
            character.stat_str = reallocated['stat_str']
            character.stat_agi = reallocated['stat_agi']
            character.stat_int = reallocated['stat_int']
            character.stat_luk = reallocated['stat_luk']
            character.stat_rep = reallocated['stat_rep']
            character.stat_good = reallocated['stat_good']
            character.stat_mag = reallocated['stat_mag']
            character.stat_div = reallocated['stat_div']
            character.save()

        
        # ========================================================
        # 💡 2. 각성의 결정 처리
        # ========================================================
        elif item_name == "각성의 결정":
            target_stat = data.get('target_stat')
            if not target_stat or not hasattr(character, target_stat):
                return JsonResponse({'success': False, 'message': '올바른 타겟 스탯을 선택하지 않았습니다.'})
            
            # 스탯 5 가산
            current_val = getattr(character, target_stat, 0)
            setattr(character, target_stat, current_val + 5)
            character.save()


        elif item_name == "용사의 검":
            gain = random.randint(1, 5)
            character.points = (character.points or 0) + gain
            character.save()
            inv_item.quantity -= 1
            inv_item.save()
            return JsonResponse({'success': True, 'message': f'용사 기여도가 {gain} 상승했습니다! (현재: {character.points})'})
        
        elif item_name == "마법의 레시피":
            from main.models import RecipeHint

            hints = list(RecipeHint.objects.select_related('item').all())
            if not hints:
                return JsonResponse({'success': False, 'message': '레시피 데이터가 없습니다.'})

            hint_obj = random.choice(hints)

            # ✅ item_name 대신 hint_obj.item.name 사용
            if hint_obj.item:
                inv, created = Inventory.objects.get_or_create(
                    user=user,
                    item=hint_obj.item,
                    defaults={'quantity': 0}
                )
                inv.quantity += 1
                inv.save()

            inv_item.quantity -= 1
            inv_item.save()

            return JsonResponse({
                'success': True,
                'message': '레시피 힌트를 얻었습니다!',
                'recipe_name': hint_obj.recipe_name,
                'hint': hint_obj.hint,
                'item_name': hint_obj.item.name if hint_obj.item else f"{hint_obj.recipe_name} 레시피",  # ✅ 수정
                'is_magic_recipe': True,
            })
        elif item_name == "닳고 닳은 검":
            target_char_id = data.get('target_character_id')
            if not target_char_id:
                return JsonResponse({'success': False, 'message': '대상을 선택해 주세요.'})

            target_character = Character.objects.filter(id=target_char_id).first()
            if not target_character:
                return JsonResponse({'success': False, 'message': '대상을 찾을 수 없습니다.'})

            loss = random.randint(1, 5)
            target_character.points = max(0, (target_character.points or 0) - loss)  # 0 아래로 안 내려가게
            target_character.save()

            inv_item.quantity -= 1
            inv_item.save()
            return JsonResponse({'success': True, 'message': f'{target_character.name_kr}의 용사 기여도가 {loss} 감소했습니다! (현재: {target_character.points})'})

        # ========================================================
        # 💡 3. 약탈의 낙인석 처리
        # ========================================================
        elif item_name == "약탈의 낙인석":
            target_char_id = data.get('target_character_id')
            target_stat = data.get('target_stat')
            
            if not target_char_id or not target_stat:
                return JsonResponse({'success': False, 'message': '약탈 대상 또는 스탯 특성이 누락되었습니다.'})
            
            target_character = Character.objects.filter(id=target_char_id).first()
            if not target_character:
                return JsonResponse({'success': False, 'message': '약탈 대상을 데이터베이스에서 찾을 수 없습니다.'})
            
            # 대상의 스탯이 최소 5 초과는 되어야 뺏을 수 있도록 안전장치 확인 (스탯이 음수가 되는 방지)
            target_val = getattr(target_character, target_stat, 0)
            if target_val < 5:
                return JsonResponse({'success': False, 'message': f'대상의 {target_stat} 스탯 수치가 5 미만이라 각인석 약탈이 불가능합니다.'})
            
            # 양방향 정산 실행
            setattr(target_character, target_stat, target_val - 5)
            setattr(character, target_stat, getattr(character, target_stat, 0) + 5)
            
            target_character.save()
            character.save()
            
            msg = f"{target_character.name_kr}님의 영혼에서 스탯 특성을 5 강탈하여 내 스탯으로 동기화했습니다."
            inv_item.quantity -= 1
            inv_item.save()
            return JsonResponse({'success': True, 'message': msg})

        
        elif item_name == "도박꾼의 지갑":
            # 하루 3회 제한 체크
            today = timezone.now().date()
            today_uses = UseLog.objects.filter(
                user=user,
                item=inv_item.item,
                used_at__date=today
            ).count()
            if today_uses >= 3:
                return JsonResponse({'success': False, 'message': '오늘 사용 횟수를 초과했습니다. (하루 3회 제한)'})

            # 결과 목록 (실패 확률 높게)
            outcomes = [-500, -500, -500, -400, -400, -300, +500, +600, +1000]
            result = random.choice(outcomes)

            character.gold = max(0, character.gold + result)  # 0 아래로 안 내려가게
            character.save()

            inv_item.quantity -= 1
            inv_item.save()

            UseLog.objects.create(user=user, item=inv_item.item)

            sign = '+' if result > 0 else ''
            return JsonResponse({
                'success': True,
                'message': f'결과: {sign}{result}G! (현재 보유금: {character.gold}G)'
            })

        elif item_name == "악마의 계약서":
            current_gold = character.gold
            if random.random() < 0.5:  # 50% 확률
                character.gold = current_gold * 5
                msg = f'성공! 보유금이 5배가 되었습니다! ({current_gold}G → {character.gold}G)'
            else:
                character.gold = 0
                msg = f'실패... 보유금이 0G가 되었습니다. ({current_gold}G → 0G)'

            character.save()
            inv_item.quantity -= 1
            inv_item.save()
            return JsonResponse({'success': True, 'message': msg})

        elif item_name == "잡화 꾸러미":
            # 하루 5회 제한 체크
            today = timezone.now().date()
            today_uses = UseLog.objects.filter(
                user=user,
                item=inv_item.item,
                used_at__date=today
            ).count()
            if today_uses >= 5:
                return JsonResponse({'success': False, 'message': '오늘 사용 횟수를 초과했습니다. (하루 5회 제한)'})

            # 랜덤 재료 아이템 뽑기 (NORMAL, ORGANIC, MINERAL 중에서)
            material_items = list(Item.objects.filter(
                category__in=['일반재료', '유기재료', '광물']
            ))

            if len(material_items) < 4:
                return JsonResponse({'success': False, 'message': '재료 아이템이 부족합니다.'})

            count = random.randint(4, 6)  # 4~6개 랜덤
            chosen = random.choices(material_items, k=count)

            for item_obj in chosen:
                inv, created = Inventory.objects.get_or_create(
                    user=user,
                    item=item_obj,
                    defaults={'quantity': 0}
                )
                inv.quantity += 1
                inv.save()

            inv_item.quantity -= 1
            inv_item.save()

            UseLog.objects.create(user=user, item=inv_item.item)

            item_names = ', '.join([i.name for i in chosen])
            return JsonResponse({'success': True, 'message': f'획득: {item_names}'})

        else:
            return JsonResponse({'success': False, 'message': '알 수 없는 아이템 형식 규칙입니다.'})

        # 공용 처리: 수량 1개 정직하게 차감 후 저장
        inv_item.quantity -= 1
        inv_item.save()
        return JsonResponse({'success': True, 'message': f'[{item_name}] 사용이 완료되어 효과가 영구히 귀속되었습니다!'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'서버 연산 치명적 실패: {str(e)}'})