let currentSelectedItem = null;

function selectItem(id, name, price, desc, imgUrl) {
    currentSelectedItem = { id, name, price };
    document.getElementById('emptyDetail').style.display = 'none';
    document.getElementById('itemDetailCard').style.display = 'block';
    document.getElementById('detailImg').src = imgUrl;
    document.getElementById('detailName').textContent = name;
    document.getElementById('detailDesc').textContent = desc;
    document.getElementById('detailPrice').textContent = price;
}

// ✅ DOMContentLoaded → 즉시실행
(() => {
    const tabs = document.querySelectorAll('.store-tab');
    const items = document.querySelectorAll('.store-item');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const filterValue = tab.getAttribute('data-filter').trim();

            items.forEach(item => {
                const itemCategory = (item.getAttribute('data-category') || '').trim();
                if (filterValue === '전체보기' || itemCategory === filterValue) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
})();

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

function changeQty(inputId, amount) {
    const input = document.getElementById(inputId);
    let newVal = (parseInt(input.value) || 1) + amount;

    if (newVal >= 1 && newVal <= 99) {
        input.value = newVal;
        let totalPrice = currentSelectedItem.price * newVal;
        if (inputId === 'buyQty') {
            document.getElementById('buyItemPrice').textContent = totalPrice + ' G';
        } else if (inputId === 'giftQty') {
            document.getElementById('giftItemPrice').textContent = totalPrice + ' G';
        }
    }
}

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