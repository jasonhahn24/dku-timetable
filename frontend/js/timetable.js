// timetable.js - tui-calendar 연동

const COURSE_COLORS = [
    '#4f46e5', '#0891b2', '#059669', '#d97706',
    '#dc2626', '#7c3aed', '#db2777', '#65a30d'
];

window.updateTimetable = null;

document.addEventListener('DOMContentLoaded', function () {
    const Calendar = window.tui.Calendar;

    const calendar = new Calendar('#calendar', {
        defaultView: 'week',
        taskView: false,
        scheduleView: ['time'],
        usageStatistics: false,
        week: {
            startDayOfWeek: 1,
            daynames: ['일', '월', '화', '수', '목', '금', '토'],
            workweek: true,
            hourStart: 9,
            hourEnd: 22
        },
        template: {
            weekDayname: function (model) {
                return `<span class="custom-dayname">${model.dayName}</span>`;
            }
        }
    });

    function addThirtyMin(timeStr) {
        if (!timeStr) return timeStr;
        const [h, m] = timeStr.split(':').map(Number);
        const total = h * 60 + m + 30;
        const nh = String(Math.floor(total / 60)).padStart(2, '0');
        const nm = String(total % 60).padStart(2, '0');
        return `${nh}:${nm}`;
    }

    // 요일 문자열 → 날짜 변환
    function getParsedDate(dayOfWeekStr, timeStr) {
        const baseDate = calendar.getDate().getTime();
        const currentDay = calendar.getDate().getDay();

        const daysMap = { '월': 1, '화': 2, '수': 3, '목': 4, '금': 5 };
        const targetDayNum = daysMap[dayOfWeekStr] || 1;

        const diffDays = targetDayNum - (currentDay === 0 ? 7 : currentDay);
        const targetDate = new Date(baseDate);
        targetDate.setDate(targetDate.getDate() + diffDays);

        const yyyy = targetDate.getFullYear();
        const mm = String(targetDate.getMonth() + 1).padStart(2, '0');
        const dd = String(targetDate.getDate()).padStart(2, '0');

        return `${yyyy}-${mm}-${dd}T${timeStr}:00+09:00`;
    }

    // CSP 엔진 결과 → tui-calendar 표시
    window.updateTimetable = function (timetable) {
        calendar.clear();
        if (!timetable || timetable.length === 0) return;

        const colorMap = {};
        let colorIdx = 0;

        const schedules = [];

        timetable.forEach(course => {
            if (!colorMap[course.name]) {
                colorMap[course.name] = COURSE_COLORS[colorIdx % COURSE_COLORS.length];
                colorIdx++;
            }
            const color = colorMap[course.name];

            const slots = course.slots || [];
            slots.forEach(slot => {
                if (!slot.start || !slot.end) return;
                schedules.push({
                    id: `${course.id}-${slot.day}`,
                    calendarId: 'lecture',
                    title: `${course.name}\n${course.professor}\n${slot.room}`,
                    category: 'time',
                    start: getParsedDate(slot.day_kor, slot.start),
                    end: getParsedDate(slot.day_kor, addThirtyMin(slot.end)),
                    bgColor: color,
                    color: '#ffffff',
                    borderColor: color
                });
            });
        });

        calendar.createSchedules(schedules);
    };

    console.log('tui-calendar 초기화 완료');
    window.updateTimetable([]);
});
