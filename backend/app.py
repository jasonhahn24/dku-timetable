"""
Flask API 서버 - CSP 시간표 자동 생성기
POST /api/parse    - 자연어 -> 제약 조건 변환 (Gemini API)
POST /api/generate - 제약 조건 -> 시간표 생성 (CSP 엔진)
"""

# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

# CSP 엔진 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'csp'))
from csp_solver import generate_timetables

app = Flask(__name__)
CORS(app)  # 프론트엔드에서 요청 허용

# Gemini API 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# 강의 데이터 경로
COURSES_JSON = os.path.join(os.path.dirname(__file__), 'crawler', 'dku_courses_csp.json')

# 키워드 매칭 (Gemini API 호출 줄이기 위해 1차 처리)
KEYWORD_MAP = {
    "\uae08\uacf5\uac15": {"no_class_days": ["\uAE08"]},
    "\uc6d4\uacf5\uac15": {"no_class_days": ["\uC6D4"]},
    "\ud654\uacf5\uac15": {"no_class_days": ["\uD654"]},
    "\uc218\uacf5\uac15": {"no_class_days": ["\uC218"]},
    "\ubaa9\uacf5\uac15": {"no_class_days": ["\uBAA9"]},
    "\uc544\uce68": {"no_class_periods": [1, 2, 3, 4]},
    "1\uad50\uc2dc": {"no_class_periods": [1, 2]},
    "\uc57c\uac04": {"no_night": True},
    "\uc800\ub141": {"no_night": True},
    "\uc6d0\uaca9 \uc81c\uc678": {"no_online": True},
    "\ub300\uba74\ub9cc": {"no_online": True},
    "\uc628\ub77c\uc778 \uc81c\uc678": {"no_online": True},
    "\uc18c\ud504\ud2b8\uc6e8\uc5b4\ud559\uacfc": {"user_dept": "\uc18c\ud504\ud2b8\uc6e8\uc5b4\ud559\uacfc"},
    "\ucef4\ud4e8\ud130\uacf5\ud559\uacfc": {"user_dept": "\ucef4\ud4e8\ud130\uacf5\ud559\uacfc"},
    "\uae30\uacc4\uacf5\ud559\uacfc": {"user_dept": "\uae30\uacc4\uacf5\ud559\uacfc"},
    "\uc804\uae30\uc804\uc790\uacf5\ud559\uacfc": {"user_dept": "\uc804\uae30\uc804\uc790\uacf5\ud559\uacfc"},
    "\uc628\ub77c\uc778 \uc704\uc8fc": {"no_online": False, "lecture_types": ["\uc6d0\uaca9\uc218\uc5c5"]},
    "\uc628\ub77c\uc778\ub9cc": {"no_online": False, "lecture_types": ["\uc6d0\uaca9\uc218\uc5c5"]},
    "\uc6d0\uaca9 \uc704\uc8fc": {"no_online": False, "lecture_types": ["\uc6d0\uaca9\uc218\uc5c5"]},
    "\ub300\uba74 \uc704\uc8fc": {"lecture_types": ["\ub300\uba74\uc218\uc5c5"]},
    "\ub300\uba74\ub9cc": {"lecture_types": ["\ub300\uba74\uc218\uc5c5"]},
    "\uad50\uc591 \ub123\uc5b4\uc918": {"include_liberal": True},
    "\uad50\uc591\ub3c4 \ub123\uc5b4": {"include_liberal": True},
    "\uad50\uc591 \ud3ec\ud568": {"include_liberal": True}
}


def keyword_parse(text: str) -> dict:
    """키워드 매칭으로 1차 파싱"""
    result = {}
    for keyword, constraint in KEYWORD_MAP.items():
        if keyword in text:
            for k, v in constraint.items():
                if k in result and isinstance(result[k], list):
                    result[k] = list(set(result[k] + v))
                else:
                    result[k] = v
    return result


def gemini_parse(text: str) -> dict:
    """Gemini API로 자연어 파싱"""
    prompt = f"""
다음 사용자 입력에서 시간표 제약 조건을 추출해서 JSON으로만 반환해. 다른 말은 하지 마.

추출 가능한 필드:
- no_class_days: 공강 요일 리스트 (영어로: MON, TUE, WED, THU, FRI)
- no_class_periods: 제외 교시 리스트 (숫자)
- required_courses: 필수 과목명 리스트
- excluded_courses: 제외 과목명 리스트
- excluded_professors: 기피 교수명 리스트
- preferred_professors: 선호 교수명 리스트
- target_credit: 목표 학점 (숫자)
- max_credit: 최대 학점 (숫자)
- no_online: 원격 수업 제외 여부 (true/false)
- user_dept: 학과명 (예: 소프트웨어학과)
- grade: 학년 (숫자 문자열, 예: "3")
- lecture_types: 수업유형 리스트 (예: ["대면수업"])
- required_types: 이수구분별 최소 개수 (예: {{"전공필수": 1, "교양필수": 1}})

예시 출력:
- "송인식 교수 수업으로 해줘" -> {{"preferred_professors": ["송인식"]}}
- "송인식 교수 빼줘" -> {{"excluded_professors": ["송인식"]}}
- "3학년 수업 위주로" -> {{"grade": "3"}}
- "온라인 강의 위주로" -> {{"lecture_types": ["원격수업"]}}
- "대면 수업만" -> {{"lecture_types": ["대면수업"]}}
- "전공필수 2개 넣어줘" -> {{"required_types": {{"전공필수": 2}}}}
사용자 입력: "{text}"
"""

    try:
        response = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=10
        )
        data = response.json()
        print(f"Gemini 전체 응답: {data}")  # 추가
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"Gemini 응답: {raw}") 
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"Gemini API 오류: {e}")
        return {}


@app.route("/api/parse", methods=["POST"])
def parse():
    """
    자연어 입력을 제약 조건으로 변환
    Request: {"text": "금공강이고 운영체제 넣어줘"}
    Response: {"constraints": {...}, "tags": [...]}
    """
    data = request.get_json(force=True)
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "\uc785\ub825\uc774 \ube44\uc5b4\uc788\uc2b5\ub2c8\ub2e4"}), 400

    # 1차: 키워드 매칭
    result = keyword_parse(text)
    print(f"키워드 파싱 결과: {result}")  # 추가

    # 1.5차: 교수명 패턴 매칭
    import re
    prof_match = re.search(r'([가-힣]{2,4})\s*교수\s*(수업으로|빼줘|제외|포함|넣어)', text)
    if prof_match:
        prof_name = prof_match.group(1)
        if '빼줘' in text or '제외' in text:
            result['excluded_professors'] = result.get('excluded_professors', []) + [prof_name]
        else:
            result['preferred_professors'] = result.get('preferred_professors', []) + [prof_name]

    # 과목명 패턴 매칭
    course_keywords = ['넣어줘', '포함해줘', '무조건', '필수로', '넣어', '추가해줘']
    if any(kw in text for kw in course_keywords):
        # "운영체제 넣어줘", "운영체제 무조건 넣어" 등
        course_match = re.search(r'(.+?)\s*(?:넣어줘|포함해줘|무조건 넣어|필수로 넣어|추가해줘)', text)
        if course_match:
            course_name = course_match.group(1).strip()
            # 제외할 일반 단어들
            exclude_words = ['수업', '과목', '강의', '전공', '교양', '학점']
            if course_name not in exclude_words:
                result['required_courses'] = result.get('required_courses', []) + [course_name]

    # 학점 패턴 매칭
    credit_match = re.search(r'(\d+)\s*학점', text)
    if credit_match:
        credit = int(credit_match.group(1))
        if 6 <= credit <= 24:
            result['target_credit'] = credit
            result['max_credit'] = credit + 1

    # 과목 제외 패턴 매칭
    exclude_match = re.search(r'(.+?)\s*(?:빼줘|제외해줘|빼|제외)', text)
    if exclude_match:
        course_name = exclude_match.group(1).strip()
        exclude_words = ['수업', '과목', '강의', '전공', '교양', '원격', '온라인', '대면', '아침', '야간']
        if course_name not in exclude_words and len(course_name) > 1:
            result['excluded_courses'] = result.get('excluded_courses', []) + [course_name]

    # 2차: 모호한 표현은 Gemini API 호출
    gemini_result = gemini_parse(text)
    print(f"Gemini 파싱 결과: {gemini_result}")  

    # 병합 (Gemini 결과로 업데이트)
    for k, v in gemini_result.items():
        if k in result and isinstance(result[k], list) and isinstance(v, list):
            result[k] = list(set(result[k] + v))
        else:
            result[k] = v

    # 태그 생성
    tags = build_tags(result)

    return jsonify({"constraints": result, "tags": tags})




@app.route("/api/generate", methods=["POST"])
def generate():
    """
    제약 조건으로 시간표 생성
    Request: {"constraints": {...}}
    Response: {"solutions": [...], "conflicts": [...], "total_found": N, "elapsed_ms": N}
    """
    data = request.get_json()
    constraints = data.get("constraints", {})
    # min_credit 자동 설정
    constraints.setdefault("target_credit", 18)
    constraints.setdefault("max_credit", 19)
    print(f"excluded_courses: {constraints.get('excluded_courses', [])}")
    constraints["min_credit"] = constraints["target_credit"] - 3
    print(f"min_credit: {constraints['min_credit']}, target: {constraints['target_credit']}")

    if not constraints:
        return jsonify({"error": "\uc870\uac74\uc774 \ube44\uc5b4\uc788\uc2b5\ub2c8\ub2e4"}), 400

    # 기본값 설정
    constraints.setdefault("target_credit", 18)
    constraints.setdefault("max_credit", 19)
    constraints.setdefault("min_credit", 12)
    constraints.setdefault("no_online", False)
    constraints.setdefault("required_courses", [])
    constraints.setdefault("no_class_days", [])
    constraints.setdefault("no_class_periods", [])

    result = generate_timetables(
        constraints=constraints,
        json_path=COURSES_JSON,
        max_results=100,
        timeout=3.0
    )
    return jsonify(result)

@app.route("/api/health", methods=["GET"])
def health():
    """서버 상태 확인"""
    return jsonify({"status": "ok"})


def build_tags(constraints: dict) -> list:
    """제약 조건을 태그 리스트로 변환"""
    tags = []
    day_map = {"MON": "\uc6d4", "TUE": "\ud654", "WED": "\uc218", "THU": "\ubaa9", "FRI": "\uae08"}

    for day in constraints.get("no_class_days", []):
        kor = day_map.get(day, day)
        tags.append({"label": f"{kor}\uacf5\uac15", "key": "no_class_days", "value": day})

    if constraints.get("no_class_periods"):
        periods = constraints["no_class_periods"]
        tags.append({"label": f"{min(periods)}~{max(periods)}\uad50\uc2dc \uc81c\uc678", "key": "no_class_periods"})

    for course in constraints.get("required_courses", []):
        tags.append({"label": f"{course} \ud544\uc218", "key": "required_courses", "value": course})

    for course in constraints.get("excluded_courses", []):
        tags.append({"label": f"{course} \uc81c\uc678", "key": "excluded_courses", "value": course})

    for prof in constraints.get("preferred_professors", []):
        tags.append({"label": f"{prof} \uc120\ud638", "key": "preferred_professors", "value": prof})

    for prof in constraints.get("excluded_professors", []):
        tags.append({"label": f"{prof} \uae30\ud53c", "key": "excluded_professors", "value": prof})

    if constraints.get("no_online"):
        tags.append({"label": "\uc6d0\uaca9 \uc81c\uc678", "key": "no_online"})

    if constraints.get("user_dept"):
        tags.append({"label": constraints["user_dept"], "key": "user_dept"})

    if constraints.get("target_credit"):
        tags.append({"label": f"{constraints['target_credit']}\ud559\uc810", "key": "target_credit"})

    for type_name, count in constraints.get("required_types", {}).items():
        tags.append({"label": f"{type_name} {count}\uac1c", "key": "required_types"})

    return tags


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)