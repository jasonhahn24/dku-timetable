# 🗓️ 시간표 마법사 — CSP 기반 최적 시간표 자동 생성기

![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat&logo=react)
![Python](https://img.shields.io/badge/Backend-Python-3776AB?style=flat&logo=python)
![Flask](https://img.shields.io/badge/API-Flask-000000?style=flat&logo=flask)
![License](https://img.shields.io/badge/License-MIT-534AB7?style=flat)

> 단국대학교 수강신청, 조건만 말하면 최적 시간표를 자동으로 생성해드립니다.

---

## 📌 프로젝트 소개

매 학기 수강신청 기간마다 학생들은 금공강 확보, 필수 과목 포함, 아침 수업 회피 등 수십 가지 조건을 동시에 만족하는 시간표를 손으로 직접 짜는 데 많은 시간을 소비합니다.

기존 에브리타임 마법사는 경우의 수가 일정 기준을 초과하면 실행 자체가 차단되는 한계가 있었습니다. 본 프로젝트는 **CSP(Constraint Satisfaction Problem) 알고리즘**과 **자연어 챗봇 인터페이스**를 결합하여 조건이 복잡할수록 더 효과적으로 동작하는 시간표 자동 생성 웹 서비스를 개발합니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 자연어 조건 입력 | "금공강이고 아침은 싫어, 운영체제 무조건 넣어줘" |
| 시간표 자동 생성 | CSP 알고리즘 기반, 어떤 조건에도 3초 이내 결과 반환 |
| 후보 시간표 비교 | 조건 충족 개수 기준으로 복수 후보 제시 |
| 충돌 리포트 | 조건 충돌 시 원인 분석 및 구체적 대안 제시 |
| 시간표 저장 / 관리 | 학기별 시간표 저장 및 불러오기 |
| 강의 데이터 수집 | 단국대 포털 크롤러 기반 자동 수집 |

---

## 🛠️ 기술 스택

| 영역 | 기술 |
|---|---|
| 프론트엔드 | HTML, CSS, JavaScript |
| 시간표 UI | tui-calendar (NHN 오픈소스) |
| 데이터 시각화 | Chart.js |
| 챗봇 파싱 | 키워드 매칭 + Gemini API |
| CSP 알고리즘 | Python, Backtracking + Forward Checking |
| 백엔드 API | Flask |
| 데이터 수집 | Playwright (단국대 포털 크롤러) |
| 버전 관리 | GitHub (main / dev / feature/*) |
| 협업 도구 | Discord |

---

## 🏗️ 시스템 구조

```
사용자 입력 (자연어)
    ↓
챗봇 UI (JavaScript)
    ↓
Gemini API → 제약 조건 파싱
    ↓
Flask API 서버
    ↓
CSP 엔진 (Python)
  - AC-3 알고리즘 (탐색 공간 축소)
  - MRV 휴리스틱 (최적 탐색 순서)
  - 백트래킹 (충돌 시 되돌아가기)
    ↓
최적 시간표 반환
    ↓
tui-calendar 시각화
```

---

## 📅 개발 일정

| 기간 | 내용 |
|---|---|
| 4/2 ~ 4/12 | 요구사항 확정, 와이어프레임, 환경 세팅 |
| 4/13 ~ 4/24 | 중간고사 (최소 작업) |
| 4/25 ~ 5/14 | 핵심 기능 개발 (CSP, 챗봇, UI) |
| 5/15 ~ 5/21 | 프론트 ↔ 백엔드 통합 |
| 5/22 ~ 5/28 | 버그 수정, 발표 자료 준비 |
| 5/29 ~ 6/4 | 최종 리허설 및 발표 |

---

## 👥 팀원

| 이름 | 역할 | 담당 기술 |
|---|---|---|
| 한상윤 | CSP 알고리즘, Flask 백엔드, 크롤러 | Python, Flask |
| 양진혁 | 챗봇 UI, Gemini API 연동, 파싱 모듈 | Python, JavaScript |
| 박현준 | UI/UX 설계, HTML/CSS, tui-calendar | HTML, CSS, JavaScript |
| 안병규 | Chart.js 시각화, 저장 기능, 반응형 | JavaScript, Chart.js |

---

## 🚀 시작하기

> 개발 진행 중입니다. 설치 방법은 추후 업데이트 예정입니다.

```bash
# 저장소 클론
git clone https://github.com/본인아이디/dku-timetable.git
cd dku-timetable

# 프론트엔드
cd frontend
npm install
npm start

# 백엔드
cd backend
pip install -r requirements.txt
python app.py
```

---

## 📂 프로젝트 구조

```
dku-timetable/
├── frontend/           # HTML, CSS, JavaScript
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── chatbot.js  # 챗봇 UI + Gemini API
│       ├── timetable.js# tui-calendar 연동
│       └── chart.js    # Chart.js 시각화
├── backend/            # Python Flask
│   ├── app.py          # Flask API 서버
│   ├── csp/
│   │   ├── solver.py   # CSP 알고리즘
│   │   ├── ac3.py      # AC-3 알고리즘
│   │   └── mrv.py      # MRV 휴리스틱
│   └── crawler/
│       └── dku_crawler.py  # 단국대 포털 크롤러
└── docs/               # 제안서 및 문서
```

---

## 🤝 기여 방법

1. 이 저장소를 Fork 합니다
2. 새 브랜치를 생성합니다 (`git checkout -b feature/기능명`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add: 기능 설명'`)
4. 브랜치에 Push 합니다 (`git push origin feature/기능명`)
5. Pull Request를 생성합니다

---

## 📚 과목 정보

단국대학교 오픈소스 SW 기초 (2026년 1학기)

---

## 📄 라이선스

MIT License © 2026 dku-timetable team
