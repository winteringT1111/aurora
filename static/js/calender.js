document.addEventListener("DOMContentLoaded", () => {
    // 1. 임시 데이터 (나중에 Django Admin에서 넘어올 JSON 데이터)
    const eventsData = [
        { id: 1, title: "경쟁전: 합동 연무제", start: "2026-05-16", end: "2026-05-17", desc: "왕실 기사단에서 우리의 실력을 확인한대요! 한 수 보여줘야 하지 않겠어요?", colorClass: "event-color-1"},
        { id: 2, title: "???", start: "2026-05-19", end: "2026-05-19", desc: "누군가는 웃고 누군가는 우는 날이 되리라!", colorClass: "event-color-1" },
        { id: 3, title: "왕실 연회", start: "2026-05-21", end: "2026-05-22", desc: "출정식 전 마지막 연회입니다. 왕비님께서는 원정대의 사이 좋은 모습을 보고 싶다고 하시네요.", colorClass: "event-color-2" },
        { id: 4, title: "MAIN STORY", start: "2026-05-23", end: "2026-05-24", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 5, title: "공백기", start: "2026-05-25", end: "2026-05-26", desc: "운영 정비 기간입니다. 텍관란 조율이 가능합니다.", colorClass: "event-color-2" },
        { id: 6, title: "MAIN STORY", start: "2026-05-27", end: "2026-05-27", desc: "22:00부터 자유 참가로 짧게 진행됩니다.", colorClass: "event-color-3" },
        { id: 7, title: "조사", start: "2026-05-28", end: "2026-05-29", desc: "27일의 선택지에 따라 짧은 조사가 진행될 수 있습니다.", colorClass: "event-color-1" },
        { id: 8, title: "MAIN STORY", start: "2026-05-31", end: "2026-05-31", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" }
    ];

    const ALLOWED_MONTHS = [4,5]; 
    const YEAR = 2026;
    
    let currentMonth = new Date().getMonth(); 
    if (currentMonth < 3) currentMonth = 3;
    if (currentMonth > 6) currentMonth = 6;

    // DOM 요소
    const grid = document.getElementById("cal-grid");
    const monthYearTitle = document.getElementById("cal-month-year");
    const prevBtn = document.getElementById("cal-prev");
    const nextBtn = document.getElementById("cal-next");
    
    // 💡 상세 패널 (툴팁) DOM
    const detailPanel = document.getElementById("event-detail-panel");
    const detailTitle = document.getElementById("detail-title");
    const detailDate = document.getElementById("detail-date");
    const detailDesc = document.getElementById("detail-desc");

    const monthNames = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"];
    const formatDate = (y, m, d) => `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;

    function renderCalendar(month) {
        grid.innerHTML = ""; 
        monthYearTitle.textContent = `${monthNames[month]}`;

        const firstDay = new Date(YEAR, month, 1).getDay();
        const daysInMonth = new Date(YEAR, month + 1, 0).getDate();
        const daysInPrevMonth = new Date(YEAR, month, 0).getDate();

        // (1) 이전 달 빈 칸
        for (let i = firstDay - 1; i >= 0; i--) {
            createDayCell(daysInPrevMonth - i, true);
        }

        // (2) 이번 달 날짜 및 일정
        for (let day = 1; day <= daysInMonth; day++) {
            const currentDateStr = formatDate(YEAR, month, day);
            const dayDiv = createDayCell(day, false);
            
            // 날짜 칸을 기준으로 상대 위치를 잡기 위함 (바를 띄우기 위해)
            dayDiv.style.position = "relative";

            const todaysEvents = eventsData.filter(e => e.start <= currentDateStr && e.end >= currentDateStr);

            // 중요: 바(Bar)를 겹치지 않게 쌓기 위해 index 활용
            todaysEvents.forEach((event, index) => {
                const barContainer = document.createElement("div");
                barContainer.className = "event-bar-container";
                
                // 바 세로 위치 계산 (겹치지 않게 top 값 조절)
                const topPosition = 24 + (index * 18); // 20px부터 18px 간격으로 쌓음
                
                const bar = document.createElement("div");
                bar.className = `event-bar ${event.colorClass}`;
                bar.dataset.id = event.id;
                bar.style.top = topPosition + "px"; // 세로 위치 고정

                // 💡 핵심: 연속 일정 판단 및 모양/글씨 조절
                const isStart = event.start === currentDateStr;
                const isEnd = event.end === currentDateStr;
                
                if (isStart && isEnd) {
                    // 하루짜리 일정
                    bar.classList.add("is-start", "is-end");
                    bar.textContent = event.title;
                    bar.style.width = "calc(100% - 4px)"; 
                } else if (isStart) {
                    // 연속 일정 시작 (양옆 여백 제거)
                    bar.classList.add("is-start");
                    bar.textContent = event.title;
                    bar.style.width = "calc(100% - 4px)";
                } else if (isEnd) {
                    // 연속 일정 종료
                    bar.classList.add("is-end");
                    bar.textContent = "\u00A0"; // 글씨 숨김
                    bar.style.width = "calc(100% - 4px)";
                } else {
                    // 연속 일정 중간 (양옆 여백 완전히 제거하여 이음)
                    bar.classList.add("is-middle");
                    bar.textContent = "\u00A0"; // 글씨 숨김
                    bar.style.width = "100%";
                }

                // 주가 바뀔 때(일요일, 토요일) 시각적 단절 방지를 위한 CSS 처리
                barContainer.appendChild(bar);
                dayDiv.appendChild(barContainer);
            });

            grid.appendChild(dayDiv);
        }

        // (3) 다음 달 빈 칸
        const totalCellsFilled = firstDay + daysInMonth;
        const remainingCells = 42 - totalCellsFilled; 
        for (let i = 1; i <= remainingCells; i++) {
            if(totalCellsFilled <= 35 && i > (35 - totalCellsFilled)) break; 
            createDayCell(i, true);
        }

        prevBtn.disabled = month <= ALLOWED_MONTHS[0];
        nextBtn.disabled = month >= ALLOWED_MONTHS[ALLOWED_MONTHS.length - 1];
    }

    function createDayCell(dayNum, isOtherMonth) {
        const dayDiv = document.createElement("div");
        dayDiv.className = `cal-day ${isOtherMonth ? 'other-month' : ''}`;
        dayDiv.innerHTML = `<div class="date-num">${dayNum}</div>`;
        if(isOtherMonth) grid.appendChild(dayDiv);
        return dayDiv;
    }

    prevBtn.addEventListener("click", () => {
        if (currentMonth > ALLOWED_MONTHS[0]) {
            currentMonth--;
            renderCalendar(currentMonth);
        }
    });

    nextBtn.addEventListener("click", () => {
        if (currentMonth < ALLOWED_MONTHS[ALLOWED_MONTHS.length - 1]) {
            currentMonth++;
            renderCalendar(currentMonth);
        }
    });

    // ==========================================
    // 💡 수정됨: 마우스를 따라다니는 툴팁 (간격 줄임)
    // ==========================================
    grid.addEventListener("mouseover", (e) => {
        if (e.target.classList.contains("event-bar")) {
            const eventId = parseInt(e.target.dataset.id);
            const evData = eventsData.find(ev => ev.id === eventId);
            
            if(evData) {
                detailTitle.textContent = evData.title;
                detailDate.textContent = `${evData.start} ~ ${evData.end}`;
                detailDesc.textContent = evData.desc;
                
                detailPanel.style.display = "block"; // 툴팁 보이기
            }
        }
    });

    grid.addEventListener("mousemove", (e) => {
        if (e.target.classList.contains("event-bar")) {
            // 💡 팁: 간격(gap)을 줄이기 위해 좌표 계산 수정
            // e.clientX, e.clientY는 마우스 커서의 화면 좌표입니다.
            // 여기에 아주 작은 오프셋(+5px)만 주어 커서 바로 옆에 붙게 만듭니다.
            detailPanel.style.position = "fixed"; // fixed로 설정해야 화면 좌표를 따름
            detailPanel.style.left = e.clientX -220 + "px"; // 마우스 오른쪽으로 5px
            detailPanel.style.top = e.clientY -100 + "px";  // 마우스 아래로 5px
            detailPanel.style.zIndex = 10
            // 만약 툴팁이 화면 오른쪽이나 아래를 벗어나면 좌표를 반대로 조절하는 로직을 추가할 수 있습니다.
        }
    });

    grid.addEventListener("mouseout", (e) => {
        if (e.target.classList.contains("event-bar")) {
            detailPanel.style.display = "none"; // 툴팁 숨기기
        }
    });

    renderCalendar(currentMonth);
});