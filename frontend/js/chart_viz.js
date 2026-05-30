// chart_viz.js - Chart.js 시각화

let scoreChartInstance = null;
let dayChartInstance = null;
let breakdownChartInstance = null;

window.updateCharts = function(solutions, currentIdx) {
    if (!solutions || solutions.length === 0) {
        document.getElementById('chartArea').style.display = 'none';
        return;
    }

    document.getElementById('chartArea').style.display = 'block';

    updateScoreChart(solutions, currentIdx);
    updateDayChart(solutions[currentIdx]);
    updateBreakdownChart(solutions[currentIdx]);
};

// 1. 후보 시간표 점수 비교 막대 차트
function updateScoreChart(solutions, currentIdx) {
    const ctx = document.getElementById('scoreChart').getContext('2d');

    const labels = solutions.map((s, i) => `\ud6c4\ubcf4 ${i + 1}`);
    const data = solutions.map(s => s.score);
    const colors = solutions.map((s, i) =>
        i === currentIdx ? '#4f46e5' : '#c7d2fe'
    );

    if (scoreChartInstance) scoreChartInstance.destroy();

    scoreChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '\uc810\uc218',
                data: data,
                backgroundColor: colors,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: '\ud6c4\ubcf4 \uc2dc\uac04\ud45c \uc810\uc218 \ube44\uad50',
                    font: { size: 13 }
                }
            },
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
}

// 2. 요일별 수업 분포 막대 차트
function updateDayChart(solution) {
    const ctx = document.getElementById('dayChart').getContext('2d');

    const dayMap = { MON: '\uc6d4', TUE: '\ud654', WED: '\uc218', THU: '\ubaa9', FRI: '\uae08' };
    const dayCount = { MON: 0, TUE: 0, WED: 0, THU: 0, FRI: 0 };

    solution.timetable.forEach(course => {
        course.slots.forEach(slot => {
            if (dayCount[slot.day] !== undefined) {
                dayCount[slot.day] += slot.periods.length;
            }
        });
    });

    const labels = Object.keys(dayMap).map(k => dayMap[k]);
    const data = Object.keys(dayCount).map(k => dayCount[k]);
    const colors = data.map(v => v === 0 ? '#e5e7eb' : '#6366f1');

    if (dayChartInstance) dayChartInstance.destroy();

    dayChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '\uad50\uc2dc \uc218',
                data: data,
                backgroundColor: colors,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: '\uc694\uc77c\ubcc4 \uc218\uc5c5 \uad50\uc2dc \uc218',
                    font: { size: 13 }
                }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// 3. 조건 충족 breakdown 도넛 차트
function updateBreakdownChart(solution) {
    const ctx = document.getElementById('breakdownChart').getContext('2d');

    const breakdown = solution.breakdown || {};
    const labels = Object.keys(breakdown);
    const data = Object.values(breakdown);

    const colors = [
        '#4f46e5', '#6366f1', '#818cf8', '#a5b4fc',
        '#c7d2fe', '#e0e7ff'
    ];

    if (breakdownChartInstance) breakdownChartInstance.destroy();

    if (labels.length === 0) {
        document.getElementById('breakdownChart').style.display = 'none';
        return;
    }

    document.getElementById('breakdownChart').style.display = 'block';

    breakdownChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { font: { size: 11 } }
                },
                title: {
                    display: true,
                    text: '\uc810\uc218 \ub124\uc774\ud2b8',
                    font: { size: 13 }
                }
            }
        }
    });
}
