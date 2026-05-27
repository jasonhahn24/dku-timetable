
window.updateTimetable = null;

document.addEventListener('DOMContentLoaded', function() {
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
            hourEnd: 19     
        },
        template: {
            weekDayname: function(model) {
                return `<span class="custom-dayname">${model.dayName}</span>`;
            }
        }
    });

    // 2. 백엔드 데이터(요일/시간)를 tui-calendar 날짜로 변환하는 내부 함수
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

    // 3. 데이터를 받아 캘린더에 동적으로 그려주는 메인 렌더링 함수
    window.updateTimetable = function(lectures) {
        calendar.clear();

        if (!lectures || lectures.length === 0) return;

        const schedules = lectures.map(lecture => {
            return {
                id: lecture.id,
                calendarId: 'lecture-schedule',
                title: lecture.name,
                category: 'time',
                start: getParsedDate(lecture.day, lecture.startTime),
                end: getParsedDate(lecture.day, lecture.endTime),
                bgColor: lecture.color || '#3b82f6',
                color: '#ffffff',
                borderColor: lecture.color || '#3b82f6'
            };
        });

        
        calendar.createSchedules(schedules);
    };

    console.log("DKU 시간표 그리드 준비 완료 (데이터 대기 중...)");
    
   
    window.updateTimetable([]); 
});