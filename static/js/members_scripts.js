document.addEventListener("DOMContentLoaded", () => {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.member-card');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // 1. 모든 버튼에서 active 클래스 제거 후, 클릭한 버튼에만 추가
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // 2. 선택된 필터값 가져오기 (예: '발테리온', 'all')
            const filterValue = btn.getAttribute('data-filter');

            // 3. 카드 필터링 (스르륵 나타나고 사라지는 효과를 위해 opacity 사용)
            cards.forEach(card => {
                const origin = card.getAttribute('data-origin');

                if (filterValue === 'all' || origin === filterValue) {
                    card.style.display = 'block';
                    // 약간의 딜레이를 주어 부드럽게 나타나게 함
                    setTimeout(() => { card.style.opacity = '1'; }, 10);
                } else {
                    card.style.opacity = '0';
                    // 투명해진 후 공간 차지 없애기
                    setTimeout(() => { card.style.display = 'none'; }, 300);
                }
            });
        });
    });
});

