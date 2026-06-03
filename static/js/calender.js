(() => {
    const eventsData = [
        { id: 1, title: "경쟁전: 합동 연무제", start: "2026-05-16", end: "2026-05-17", desc: "왕실 기사단에서 우리의 실력을 확인한대요! 한 수 보여줘야 하지 않겠어요?", colorClass: "event-color-1"},
        { id: 2, title: "???", start: "2026-05-19", end: "2026-05-19", desc: "누군가는 웃고 누군가는 우는 날이 되리라!", colorClass: "event-color-1" },
        { id: 3, title: "왕실 연회", start: "2026-05-21", end: "2026-05-22", desc: "출정식 전 마지막 연회입니다. 왕비님께서는 원정대의 사이 좋은 모습을 보고 싶다고 하시네요.", colorClass: "event-color-2" },
        { id: 4, title: "MAIN STORY", start: "2026-05-23", end: "2026-05-24", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 5, title: "공백기", start: "2026-05-25", end: "2026-05-26", desc: "운영 정비 기간입니다. 텍관란 조율이 가능합니다.", colorClass: "event-color-2" },
        { id: 6, title: "MAIN STORY", start: "2026-05-27", end: "2026-05-27", desc: "22:00부터 자유 참가로 짧게 진행됩니다.", colorClass: "event-color-3" },
        { id: 7, title: "조사", start: "2026-05-28", end: "2026-05-29", desc: "27일의 선택지에 따라 짧은 조사가 진행될 수 있습니다.", colorClass: "event-color-1" },
        { id: 8, title: "MAIN STORY", start: "2026-05-31", end: "2026-05-31", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 9, title: "SUB STORY", start: "2026-06-06", end: "2026-06-06", desc: "카페에서 서브 스토리가 진행됩니다.", colorClass: "event-color-1" },
        { id: 10, title: "MAIN STORY", start: "2026-06-07", end: "2026-06-07", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 11, title: "MAIN STORY", start: "2026-06-13", end: "2026-06-14", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 12, title: "공백기", start: "2026-06-15", end: "2026-06-16", desc: "운영 정비 기간입니다. 활동이 제한됩니다.", colorClass: "event-color-2" },
        { id: 13, title: "SUB STORY(축성제)", start: "2026-06-17", end: "2026-06-17", desc: "카페에서 서브 스토리가 진행됩니다.", colorClass: "event-color-1" },
        { id: 14, title: "MAIN STORY", start: "2026-06-19", end: "2026-06-21", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 14, title: "SUB STORY", start: "2026-06-19", end: "2026-06-19", desc: "카페에서 서브 스토리가 진행됩니다.", colorClass: "event-color-1" },
        { id: 14, title: "SUB STORY", start: "2026-06-21", end: "2026-06-21", desc: "카페에서 서브 스토리가 진행됩니다.", colorClass: "event-color-1" },
        { id: 14, title: "공백기", start: "2026-06-23", end: "2026-06-24", desc: "운영 정비 기간입니다. 활동이 제한됩니다.", colorClass: "event-color-2" },
        { id: 14, title: "MAIN STORY", start: "2026-06-27", end: "2026-06-28", desc: "카페에서 메인 스토리가 진행됩니다.", colorClass: "event-color-3" },
        { id: 14, title: "SUB STORY", start: "2026-06-28", end: "2026-06-28", desc: "카페에서 서브 스토리가 진행됩니다.", colorClass: "event-color-1" }
    ];

    const ALLOWED_MONTHS = [5, 6];
    const YEAR = 2026;

    let currentMonth = new Date().getMonth();
    if (currentMonth < 3) currentMonth = 3;
    if (currentMonth > 6) currentMonth = 6;

    const grid = document.getElementById("cal-grid");
    const monthYearTitle = document.getElementById("cal-month-year");
    const prevBtn = document.getElementById("cal-prev");
    const nextBtn = document.getElementById("cal-next");
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

        for (let i = firstDay - 1; i >= 0; i--) {
            createDayCell(daysInPrevMonth - i, true);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const currentDateStr = formatDate(YEAR, month, day);
            const dayDiv = createDayCell(day, false);
            dayDiv.style.position = "relative";

            const todaysEvents = eventsData.filter(e => e.start <= currentDateStr && e.end >= currentDateStr);

            todaysEvents.forEach((event, index) => {
                const barContainer = document.createElement("div");
                barContainer.className = "event-bar-container";

                const topPosition = 24 + (index * 18);

                const bar = document.createElement("div");
                bar.className = `event-bar ${event.colorClass}`;
                bar.dataset.id = event.id;
                bar.style.top = topPosition + "px";

                const isStart = event.start === currentDateStr;
                const isEnd = event.end === currentDateStr;

                if (isStart && isEnd) {
                    bar.classList.add("is-start", "is-end");
                    bar.textContent = event.title;
                    bar.style.width = "calc(100% - 4px)";
                } else if (isStart) {
                    bar.classList.add("is-start");
                    bar.textContent = event.title;
                    bar.style.width = "calc(100% - 4px)";
                } else if (isEnd) {
                    bar.classList.add("is-end");
                    bar.textContent = "\u00A0";
                    bar.style.width = "calc(100% - 4px)";
                } else {
                    bar.classList.add("is-middle");
                    bar.textContent = "\u00A0";
                    bar.style.width = "100%";
                }

                barContainer.appendChild(bar);
                dayDiv.appendChild(barContainer);
            });

            grid.appendChild(dayDiv);
        }

        const totalCellsFilled = firstDay + daysInMonth;
        const remainingCells = 42 - totalCellsFilled;
        for (let i = 1; i <= remainingCells; i++) {
            if (totalCellsFilled <= 35 && i > (35 - totalCellsFilled)) break;
            createDayCell(i, true);
        }

        prevBtn.disabled = month <= ALLOWED_MONTHS[0];
        nextBtn.disabled = month >= ALLOWED_MONTHS[ALLOWED_MONTHS.length - 1];
    }

    function createDayCell(dayNum, isOtherMonth) {
        const dayDiv = document.createElement("div");
        dayDiv.className = `cal-day ${isOtherMonth ? 'other-month' : ''}`;
        dayDiv.innerHTML = `<div class="date-num">${dayNum}</div>`;
        if (isOtherMonth) grid.appendChild(dayDiv);
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

    grid.addEventListener("mouseover", (e) => {
        if (e.target.classList.contains("event-bar")) {
            const eventId = parseInt(e.target.dataset.id);
            const evData = eventsData.find(ev => ev.id === eventId);
            if (evData) {
                detailTitle.textContent = evData.title;
                detailDate.textContent = `${evData.start} ~ ${evData.end}`;
                detailDesc.textContent = evData.desc;
                detailPanel.style.display = "block";
            }
        }
    });

    grid.addEventListener("mousemove", (e) => {
        if (e.target.classList.contains("event-bar")) {
            detailPanel.style.position = "fixed";
            detailPanel.style.left = e.clientX - 220 + "px";
            detailPanel.style.top = e.clientY - 100 + "px";
            detailPanel.style.zIndex = 10;
        }
    });

    grid.addEventListener("mouseout", (e) => {
        if (e.target.classList.contains("event-bar")) {
            detailPanel.style.display = "none";
        }
    });

    renderCalendar(currentMonth);
})();