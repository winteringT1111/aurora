document.addEventListener("DOMContentLoaded", function () {
    // 1. DOM 요소 가져오기
    const slots = document.querySelectorAll('.slot'); // 새로 만든 4개의 빈 슬롯
    const items = document.querySelectorAll('.item'); // 우측 인벤토리의 아이템들
    const resetBtn = document.getElementById('reset-btn');
    const craftBtn = document.getElementById('craft-btn');
    
    let selectedItems = []; // 선택된 아이템의 데이터(이름, 이미지 src)를 담을 배열

    // 2. 우측 인벤토리 아이템 클릭 이벤트
    items.forEach(item => {
        item.addEventListener('click', () => {
            const itemCountSpan = item.querySelector('.item-count');
            let count = parseInt(item.dataset.count);

            // 슬롯이 다 차지 않았고(4개 미만), 해당 아이템의 개수가 1개 이상일 때만 추가
            if (selectedItems.length < 4 && count > 0) {
                // 개수 감소 및 UI 업데이트
                count--;
                item.dataset.count = count;
                itemCountSpan.textContent = `x${count}`;
                
                // 만약 개수가 0이 되면 흐리게 처리(disabled)
                if (count === 0) {
                    item.classList.add('disabled');
                }

                // 선택된 아이템 정보 저장
                const itemName = item.dataset.name;
                const itemImgSrc = item.querySelector('img').src;
                selectedItems.push({ name: itemName, src: itemImgSrc });

                // 좌측 슬롯 UI 업데이트
                updateSlotsUI();
            }
        });
    });

    // 3. 좌측 빈 슬롯 UI 업데이트 함수
    function updateSlotsUI() {
        // 모든 슬롯을 일단 비움
        slots.forEach(slot => slot.innerHTML = '');

        // selectedItems 배열에 있는 만큼 이미지를 채워 넣음
        selectedItems.forEach((itemInfo, index) => {
            slots[index].innerHTML = `<img src="${itemInfo.src}" alt="${itemInfo.name}">`;
        });
    }

    // 4. 초기화 버튼 (새로고침 없이 상태만 초기화하도록 개선)
    resetBtn.addEventListener('click', () => {
        // 배열 비우기 및 슬롯 비우기
        selectedItems = [];
        updateSlotsUI();

        // 인벤토리 아이템 개수 원상복구 (서버에서 가져온 초기값으로)
        items.forEach(item => {
            // dataset에서 초기값을 가져오는 로직 (HTML 렌더링 시 data-initial-count 속성을 추가해두면 좋지만, 
            // 여기서는 페이지 새로고침으로 깔끔하게 리셋하는 방식을 추천합니다)
        });
        
        // 새로고침 방식 유지
        location.reload(); 
    });

    // 5. 조합하기 버튼 클릭
    craftBtn.addEventListener('click', () => {
        if (selectedItems.length < 2) {
            alert('최소 2개의 마법 재료를 솥에 넣어주세요.');
            return;
        }

        const selectedItemNames = selectedItems.map(item => item.name);

        // 💡 1. 정확한 URL로 수정 (urls.py에 맞게 변경하세요! 예: '/combine/')
        const fetchUrl = '/combine/'; 

        const getCookie = (name) => {
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
        };
        const csrftoken = getCookie('csrftoken');

        fetch(fetchUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ selected_items: selectedItemNames }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error) });
            }
            return response.json();
        })
        .then(data => {
            const resultModalTitle = document.getElementById("resultModalTitle");
            const resultModalMessage = document.getElementById("resultModalMessage");
            const resultModalImage = document.getElementById("resultModalImage");

            if (data.result === "success") {
                resultModalTitle.textContent = "조합 성공!";
                resultModalTitle.style.color = "#ba9e7a"; 
            } else {
                resultModalTitle.textContent = "조합 실패...";
                resultModalTitle.style.color = "#a39887"; 
            }

            // 💡 2 & 3. 백엔드에서 보내준 메시지와 올바른 이미지 경로 사용
            resultModalMessage.textContent = data.message; 
            resultModalImage.src = `/static/img/도트/${data.image}`;

            // 💡 4. jQuery 대신 순수 JS 방식으로 모달 띄우기
            const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
            resultModal.show();
        })
        .catch(error => alert(error.message)); // 경험치 부족 등 서버 에러 메시지 띄우기
    });

    // 6. 결과 모달창 닫기 버튼
    document.querySelector('.close-result-btn').addEventListener('click', () => {
        // 모달 닫기 애니메이션을 기다릴 필요 없이 바로 새로고침하면 깔끔합니다
        location.reload(); 
    });

    // 7. 조합 기록(레시피 북) 버튼 클릭 이벤트
    const recipeBookBtn = document.getElementById('recipe-book-btn');
    if (recipeBookBtn) {
        recipeBookBtn.addEventListener('click', () => {
            const recipeBookModal = new bootstrap.Modal(document.getElementById('recipeBookModal'));
            recipeBookModal.show();
        });
    }
});