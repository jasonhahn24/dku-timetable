# 🗓️ 시간표 마법사 — CSP 기반 최적 시간표 자동 생성기

![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat&logo=react)
![Python](https://img.shields.io/badge/Backend-Python-3776AB?style=flat&logo=python)
![Flask](https://img.shields.io/badge/API-Flask-000000?style=flat&logo=flask)
![License](https://img.shields.io/badge/License-MIT-534AB7?style=flat)


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
| 4/3 ~ 4/12 | 요구사항 확정, 와이어프레임, 환경 세팅 |
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
| 박현준 | 챗봇 UI, Gemini API 연동, 파싱 모듈 | Python, JavaScript |
| 양진혁 | UI/UX 설계, HTML/CSS, tui-calendar | HTML, CSS, JavaScript |
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

## 🚀 기술적 차별점

### 1. CSP(Constraint Satisfaction Problem) 기반 탐색 최적화
단순 Brute-Force 방식이 아닌 **백트래킹(Backtracking), AC-3 알고리즘, MRV 휴리스틱**을 적용하여 탐색 공간을 수십만 배 이상 축소했습니다. 이를 통해 수억 가지 이상의 경우의 수도 3초 이내에 최적해로 수렴하며, 기존 서비스의 탐색 한계를 극복했습니다.

### 2. AI 파싱 한계 극복 및 캐싱 메커니즘
자연어 처리를 위해 Gemini API를 활용하는 과정에서 두 가지 기술적 난관이 발생했습니다. 
* **문제점**: 
    * **API 호출 제한(Rate Limit)**: 사용자의 매 요청마다 AI를 호출할 경우 서비스 호출 한계를 초과하여 일시적으로 서비스가 중단되는 문제가 있었습니다.
    * **응답 속도 및 비용**: 모든 입력에 대해 AI 연산을 수행하는 것은 불필요한 비용과 대기 시간을 발생시켰습니다.
* **해결책 (유사도 기반 캐싱 시스템)**: 
    * **동작 원리**: 사용자의 입력이 들어오면 기존에 저장된 데이터셋과 **코사인 유사도(Cosine Similarity) 또는 레벤슈타인 거리(Levenshtein Distance)**를 계산합니다.
    * **캐시 HIT**: 유사도가 기준값 이상인 기존 데이터가 발견되면, AI 호출 없이 즉시 결과(Constraint 변환 값)를 반환합니다.
    * **캐시 MISS**: 새로운 형태의 입력일 때만 Gemini API를 호출하여 결과를 생성하고, 이후 재사용을 위해 DB에 저장합니다.
* **기대 효과**: 반복적인 조건 입력에 대해 0.1초 내외의 초고속 응답을 제공하며, API 사용량을 최적화하여 서비스의 안정성을 극대화했습니다.

---

## 🔮 향후 확장 기능 (Future Roadmap)

본 프로젝트는 현재 단국대학교 시간표 최적화에 최적화되어 있으나, 범용성을 확보하기 위해 다음과 같은 기능을 고도화할 계획입니다.

* **타 대학 데이터 연동**: 크롤러 모듈을 모듈화하여 국내 주요 대학 포털 시스템을 즉시 지원할 수 있도록 구조 개선
* **멀티 플랫폼 지원**: 웹 환경뿐만 아니라 Discord 챗봇 및 카카오톡 챗봇 연동을 통한 접근성 확대
* **AI 추천 알고리즘 고도화**: 사용자의 과거 수강 이력 및 선호도를 분석하여, 단순히 조건을 만족하는 시간표를 넘어 '성공적인 학점 관리를 위한 최적 경로'를 추천하는 개인화 엔진 도입
* **실시간 강의 인원 모니터링**: 수강신청 기간 중 분반별 잔여석을 실시간으로 추적하여, 신청 가능성이 높은 시간표를 우선순위로 제안하는 기능

---
## 🤝 기여 방법

1. 이 저장소를 Fork 합니다
2. 새 브랜치를 생성합니다 (`git checkout -b feature/기능명`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add: 기능 설명'`)
4. 브랜치에 Push 합니다 (`git push origin feature/기능명`)
5. Pull Request를 생성합니다

---

## 📄 라이선스

MIT License © 2026 dku-timetable team
