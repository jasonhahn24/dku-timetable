// chatbot.js - 챗봇 UI + Flask API 연결

const API_BASE = 'http://localhost:5000';

// 현재 누적된 제약 조건
let constraints = {
    required_courses: [],
    no_class_days: [],
    no_class_periods: [],
    preferred_professors: [],
    excluded_professors: [],
    lecture_types: [],
    required_types: {},
    user_dept: '',
    grade: '',
    no_online: false,
    target_credit: 18,
    max_credit: 19,
    min_credit: 12
};

// 후보 시간표 목록
let solutions = [];
let currentIdx = 0;

// 로딩 메시지 목록
const LOADING_STEPS = [
    '조건 분석 중...',
    '강의 데이터 불러오는 중...',
    '불가능한 시간대 제거 중...',
    '최적 조합 탐색 중...',
    '시간표 점수 계산 중...'
];

document.addEventListener('DOMContentLoaded', function () {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const generateBtn = document.getElementById('generateBtn');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const saveBtn = document.getElementById('saveBtn');

    // 전송 버튼
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') handleSend();
    });

    // 시간표 생성 버튼
    generateBtn.addEventListener('click', handleGenerate);

    // 후보 이동
    prevBtn.addEventListener('click', () => {
        if (currentIdx > 0) {
            currentIdx--;
            showSolution(currentIdx);
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentIdx < solutions.length - 1) {
            currentIdx++;
            showSolution(currentIdx);
        }
    });

    // 저장 버튼
    saveBtn.addEventListener('click', handleSave);

    // 저장 목록 불러오기
    loadSavedList();
});


// ── 챗봇 메시지 처리 ──────────────────────────────────────

async function handleSend() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    addUserMessage(text);

    try {
        const res = await fetch(`${API_BASE}/api/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify({ text })
        });

        const data = await res.json();
        applyConstraints(data.constraints, data.tags);

        const summary = buildSummaryMessage(data.constraints);
        addBotMessage(summary);

    } catch (e) {
        addBotMessage('서버 연결에 실패했어요. Flask 서버가 실행 중인지 확인해주세요.');
    }
}


// ── 시간표 생성 ───────────────────────────────────────────

async function handleGenerate() {
    showLoading(true);
    hideConflict();

    let step = 0;
    const interval = setInterval(() => {
        document.getElementById('loadingText').textContent = LOADING_STEPS[step % LOADING_STEPS.length];
        step++;
    }, 600);

    try {
        const res = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify({ constraints })
        });

        const data = await res.json();
        clearInterval(interval);
        showLoading(false);

        if (data.conflicts && data.conflicts.length > 0) {
            showConflict(data.conflicts);
            addBotMessage(`⚠️ 조건 충돌이 발생했어요.\n${data.conflicts.map(c => c.desc).join('\n')}`);
            return;
        }

        if (!data.solutions || data.solutions.length === 0) {
            addBotMessage('조건을 만족하는 시간표를 찾지 못했어요. 조건을 조금 완화해볼까요?');
            return;
        }

        solutions = data.solutions;
        currentIdx = 0;
        showSolution(0);
        addBotMessage(`✅ ${data.total_found}개의 후보 시간표를 찾았어요! (${data.elapsed_ms}ms)\n좌우 화살표로 비교해보세요.`);

    } catch (e) {
        clearInterval(interval);
        showLoading(false);
        addBotMessage('시간표 생성 중 오류가 발생했어요.');
    }
}


// ── 후보 시간표 표시 ──────────────────────────────────────

function showSolution(idx) {
    const sol = solutions[idx];
    if (!sol) return;

    // 시간표 그리드 업데이트
    if (window.updateTimetable) {
        window.updateTimetable(sol.timetable);
    }

    // 후보 정보 업데이트
    document.getElementById('candidateNav').style.display = 'flex';
    document.getElementById('candidateInfo').textContent = `후보 ${idx + 1} / ${solutions.length}`;
    document.getElementById('scoreBadge').textContent = `${sol.score}점`;
}


// ── 조건 태그 관리 ────────────────────────────────────────

function applyConstraints(newConstraints, tags) {
    // 배열 필드는 누적
    const arrayFields = ['required_courses', 'no_class_days', 'no_class_periods',
                         'preferred_professors', 'excluded_professors', 'lecture_types'];

    arrayFields.forEach(field => {
        if (newConstraints[field] && newConstraints[field].length > 0) {
            constraints[field] = [...new Set([...constraints[field], ...newConstraints[field]])];
        }
    });

    // 단일 필드는 덮어쓰기
    const singleFields = ['user_dept', 'grade', 'no_online', 'target_credit', 'max_credit'];
    singleFields.forEach(field => {
        if (newConstraints[field] !== undefined && newConstraints[field] !== '') {
            constraints[field] = newConstraints[field];
        }
    });

    // required_types 병합
    if (newConstraints.required_types) {
        Object.assign(constraints.required_types, newConstraints.required_types);
    }

    renderTags();
}

function renderTags() {
    const container = document.getElementById('conditionTags');
    container.innerHTML = '';

    const tagData = buildTagsFromConstraints();
    tagData.forEach(tag => {
        const el = document.createElement('span');
        el.className = 'tag';
        el.innerHTML = `${tag.label} <span class="tag-remove" onclick="removeTag('${tag.key}', '${tag.value || ''}')">×</span>`;
        container.appendChild(el);
    });
}

function buildTagsFromConstraints() {
    const tags = [];
    const dayMap = { 'MON': '월', 'TUE': '화', 'WED': '수', 'THU': '목', 'FRI': '금' };

    constraints.no_class_days.forEach(d => {
        tags.push({ label: `${dayMap[d] || d}공강`, key: 'no_class_days', value: d });
    });

    if (constraints.no_class_periods.length > 0) {
        const min = Math.min(...constraints.no_class_periods);
        const max = Math.max(...constraints.no_class_periods);
        tags.push({ label: `${min}~${max}교시 제외`, key: 'no_class_periods' });
    }

    constraints.required_courses.forEach(c => {
        tags.push({ label: `${c} 필수`, key: 'required_courses', value: c });
    });

    constraints.preferred_professors.forEach(p => {
        tags.push({ label: `${p} 선호`, key: 'preferred_professors', value: p });
    });

    constraints.excluded_professors.forEach(p => {
        tags.push({ label: `${p} 기피`, key: 'excluded_professors', value: p });
    });

    if (constraints.no_online) {
        tags.push({ label: '원격 제외', key: 'no_online' });
    }

    if (constraints.user_dept) {
        tags.push({ label: constraints.user_dept, key: 'user_dept' });
    }

    if (constraints.target_credit !== 18) {
        tags.push({ label: `${constraints.target_credit}학점`, key: 'target_credit' });
    }

    Object.entries(constraints.required_types).forEach(([type, count]) => {
        tags.push({ label: `${type} ${count}개`, key: 'required_types', value: type });
    });

    return tags;
}

function removeTag(key, value) {
    if (key === 'no_class_days') {
        constraints.no_class_days = constraints.no_class_days.filter(d => d !== value);
    } else if (key === 'no_class_periods') {
        constraints.no_class_periods = [];
    } else if (key === 'required_courses') {
        constraints.required_courses = constraints.required_courses.filter(c => c !== value);
    } else if (key === 'preferred_professors') {
        constraints.preferred_professors = constraints.preferred_professors.filter(p => p !== value);
    } else if (key === 'excluded_professors') {
        constraints.excluded_professors = constraints.excluded_professors.filter(p => p !== value);
    } else if (key === 'no_online') {
        constraints.no_online = false;
    } else if (key === 'user_dept') {
        constraints.user_dept = '';
    } else if (key === 'target_credit') {
        constraints.target_credit = 18;
    } else if (key === 'required_types') {
        delete constraints.required_types[value];
    }
    renderTags();
}


// ── 저장/불러오기 ─────────────────────────────────────────

function handleSave() {
    if (!solutions[currentIdx]) return;

    const sol = solutions[currentIdx];
    const key = `timetable_${Date.now()}`;
    const saved = {
        key,
        semester: '2026년 1학기',
        score: sol.score,
        credit: sol.total_credit,
        count: sol.timetable.length,
        timetable: sol.timetable,
        constraints: { ...constraints }
    };

    localStorage.setItem(key, JSON.stringify(saved));
    loadSavedList();
    addBotMessage('✅ 시간표가 저장됐어요!');
}

function loadSavedList() {
    const container = document.getElementById('savedItems');
    const listWrap = document.getElementById('savedList');
    container.innerHTML = '';

    const keys = Object.keys(localStorage).filter(k => k.startsWith('timetable_'));

    if (keys.length === 0) {
        listWrap.style.display = 'none';
        return;
    }

    listWrap.style.display = 'block';

    keys.sort().reverse().forEach(key => {
        const data = JSON.parse(localStorage.getItem(key));
        const item = document.createElement('div');
        item.className = 'saved-item';
        item.innerHTML = `
            <div class="saved-item-info">
                <div>${data.semester}</div>
                <div class="saved-item-meta">${data.score}점 · ${data.credit}학점 · ${data.count}과목</div>
            </div>
            <button class="load-btn" onclick="loadSaved('${key}')">불러오기</button>
        `;
        container.appendChild(item);
    });
}

function loadSaved(key) {
    const data = JSON.parse(localStorage.getItem(key));
    if (!data) return;

    constraints = data.constraints;
    renderTags();

    if (window.updateTimetable) {
        window.updateTimetable(data.timetable);
    }

    document.getElementById('candidateNav').style.display = 'flex';
    document.getElementById('candidateInfo').textContent = '저장된 시간표';
    document.getElementById('scoreBadge').textContent = `${data.score}점`;

    addBotMessage(`📂 ${data.semester} 시간표를 불러왔어요.`);
}


// ── UI 헬퍼 ──────────────────────────────────────────────

function addBotMessage(text) {
    const container = document.getElementById('chatMessages');
    const el = document.createElement('div');
    el.className = 'bot-message';
    el.style.whiteSpace = 'pre-line';
    el.textContent = text;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
}

function addUserMessage(text) {
    const container = document.getElementById('chatMessages');
    const el = document.createElement('div');
    el.className = 'user-message';
    el.textContent = text;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
}

function showLoading(show) {
    document.getElementById('loadingMsg').style.display = show ? 'block' : 'none';
    document.getElementById('candidateNav').style.display = show ? 'none' : (solutions.length > 0 ? 'flex' : 'none');
}

function showConflict(conflicts) {
    const report = document.getElementById('conflictReport');
    const list = document.getElementById('conflictList');
    list.innerHTML = '';
    conflicts.forEach(c => {
        const item = document.createElement('div');
        item.className = 'conflict-item';
        item.innerHTML = `<div>${c.desc}</div><div class="conflict-fix">💡 ${c.fix}</div>`;
        list.appendChild(item);
    });
    report.style.display = 'block';
}

function hideConflict() {
    document.getElementById('conflictReport').style.display = 'none';
}

function buildSummaryMessage(c) {
    const parts = [];
    const dayMap = { 'MON': '월', 'TUE': '화', 'WED': '수', 'THU': '목', 'FRI': '금' };

    if (c.no_class_days && c.no_class_days.length > 0) {
        parts.push(`공강 요일: ${c.no_class_days.map(d => dayMap[d] || d).join(', ')}요일`);
    }
    if (c.no_class_periods && c.no_class_periods.length > 0) {
        parts.push(`제외 교시: ${Math.min(...c.no_class_periods)}~${Math.max(...c.no_class_periods)}교시`);
    }
    if (c.required_courses && c.required_courses.length > 0) {
        parts.push(`필수 과목: ${c.required_courses.join(', ')}`);
    }
    if (c.user_dept) parts.push(`학과: ${c.user_dept}`);
    if (c.no_online) parts.push('원격 수업 제외');

    if (parts.length === 0) return '조건이 추가됐어요. 더 추가하거나 시간표를 생성해보세요!';
    return `조건을 확인했어요:\n${parts.join('\n')}\n\n더 추가하거나 [시간표 생성하기]를 눌러주세요!`;
}
