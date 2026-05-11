let currentSelectedItem = null;

// =========================================
// 1. 아이템 선택 시 좌측 패널 업데이트
// =========================================
function selectItem(id, name, price, desc, imgUrl) {
    currentSelectedItem = { id: id, name: name, price: price };
    
    // 빈 화면 숨기고 상세 카드 보이기
    document.getElementById('emptyDetail').style.display = 'none';
    document.getElementById('itemDetailCard').style.display = 'block';
    
    // 정보 채우기
    document.getElementById('detailImg').src = imgUrl;
    document.getElementById('detailName').textContent = name;
    document.getElementById('detailDesc').textContent = desc;
    document.getElementById('detailPrice').textContent = price;
}

// =========================================
// 2. 카테고리 탭 필터링 로직 (한국어 버전)
// =========================================
document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll('.store-tab');
    const items = document.querySelectorAll('.store-item');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 💡 한국어 값을 그대로 가져옵니다. (양끝 띄어쓰기만 제거)
            const filterValue = tab.getAttribute('data-filter').trim();

            items.forEach(item => {
                // 💡 아이템의 카테고리(한국어)도 그대로 가져옵니다.
                const itemCategory = (item.getAttribute('data-category') || '').trim();
                
                // 조건: '전체보기'를 눌렀거나, 카테고리가 일치할 때만 보여줌
                if (filterValue === '전체보기' || itemCategory === filterValue) {
                    item.style.display = 'flex'; 
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});

// =========================================
// 3. 팝업창(Modal) 및 수량 조절 로직
// =========================================
function openModal(modalId) {
    if (!currentSelectedItem) return;

    if (modalId === 'buyModal') {
        document.getElementById('buyItemName').textContent = currentSelectedItem.name;
        document.getElementById('buyItemPrice').textContent = currentSelectedItem.price + ' G';
        document.getElementById('buyQty').value = 1;
    } else if (modalId === 'giftModal') {
        document.getElementById('giftItemName').textContent = currentSelectedItem.name;
        document.getElementById('giftItemPrice').textContent = currentSelectedItem.price + ' G';
        document.getElementById('giftQty').value = 1;
        document.getElementById('giftTarget').value = '';
        document.getElementById('giftMsg').value = '';
        document.getElementById('giftAnon').checked = false;
    }
    
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// =========================================
// 수량 조절 및 가격 자동 계산 로직
// =========================================
function changeQty(inputId, amount) {
    const input = document.getElementById(inputId);
    let currentVal = parseInt(input.value) || 1;
    let newVal = currentVal + amount;
    
    // 수량은 최소 1개, 최대 99개까지만 가능하도록 제한
    if (newVal >= 1 && newVal <= 99) {
        input.value = newVal;
        
        // 💡 핵심: 수량에 맞춰 총 가격 계산 (1개 가격 * 변경된 수량)
        // currentSelectedItem.price는 selectItem 함수에서 저장해둔 원가입니다.
        let totalPrice = currentSelectedItem.price * newVal;
        
        // 계산된 총 가격을 팝업창에 업데이트
        if (inputId === 'buyQty') {
            document.getElementById('buyItemPrice').textContent = totalPrice + ' G';
        } else if (inputId === 'giftQty') {
            document.getElementById('giftItemPrice').textContent = totalPrice + ' G';
        }
    }
}

// =========================================
// 4. 구매 및 선물 백엔드 전송 (Django 연결)
// =========================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function submitAction(actionType) {
    if (!currentSelectedItem) return;
    const csrftoken = getCookie('csrftoken');
    
    // 💡 URL 경로를 확인하세요 (앱 이름이 붙어있다면 '/myapp/store/buy/' 형식이 될 수 있습니다)
    let url = actionType === '구매' ? '/store/buy/' : '/store/gift/';
    let bodyData = {};

    if (actionType === '구매') {
        bodyData = { 
            'item_id': currentSelectedItem.id, 
            'qty': document.getElementById('buyQty').value 
        };
    } else {
        bodyData = {
            'item_id': currentSelectedItem.id,
            'qty': document.getElementById('giftQty').value,
            'target_id': document.getElementById('giftTarget').value,
            'message': document.getElementById('giftMsg').value,
            'is_anon': document.getElementById('giftAnon').checked
        };
        if (!bodyData.target_id) { alert("대상을 선택해주세요."); return; }
    }

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(bodyData)
    })
    .then(response => {
        if (!response.ok) throw new Error('서버 응답 오류 (404 또는 500)');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert(data.msg);
            // 💡 텍스트 유지하며 골드 수치만 업데이트
            document.querySelector('.current-gold').textContent = `보유 자금 | ${data.remain_gold} G`;
            closeModal(actionType === '구매' ? 'buyModal' : 'giftModal');
        } else {
            alert(data.msg);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("요청을 처리할 수 없습니다. URL 경로를 확인해주세요.");
    });
}