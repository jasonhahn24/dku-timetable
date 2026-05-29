import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from ac3 import ac3
from backtracking import backtrack

app = Flask(__name__)
CORS(app)  # 프론트엔드 컴포넌트와의 원활한 데이터 통신을 위한 CORS 허용

with open('./crawler/dku_courses_csp.json', 'r', encoding='utf-8') as f:
    ALL_COURSES = json.load(f)

@app.route('/')
def home():
    return "단국대 시간표 CSP 알고리즘 백엔드 서버 정상 가동 중!"

@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    req_data = request.json
    if not req_data:
        return jsonify({"status": "error", "message": "요청 데이터가 누락되었습니다."}), 400

    selected_courses = req_data.get('selected_courses', [])
    constraints = req_data.get('constraints', {})

    if len(selected_courses) > 10:
        return jsonify({
            "status": "error", 
            "message": "선택 과목이 너무 많습니다. 최대 10개까지만 선택하여 탐색 가능합니다."
        }), 400

    initial_domains = {}
    for course in selected_courses:
        if course in ALL_COURSES:
            # 전체 단국대 강의 데이터에서 해당 과목의 분반 리스트를 맵핑
            initial_domains[course] = ALL_COURSES[course]
        else:
            return jsonify({
                "status": "error", 
                "message": f"'{course}' 과목은 수집된 단국대 강의 데이터에 존재하지 않습니다."
            }), 400

    start_time = time.time()
    
    try:
        # [Step 1] AC-3 알고리즘 적용 (제약 조건을 위반하는 불가능한 분반 사전 제거)
        filtered_domains = ac3(initial_domains, constraints)
        
        # [Step 2] 백트래킹 알고리즘 적용 (최적의 조합 탐색 및 시간표 생성)
        # 제안서 위험 요인 대책 요구사항에 맞춰 최대 탐색 제한시간(timeout)은 5.0초로 설정
        result = backtrack({}, filtered_domains, constraints, start_time, timeout=5.0)
        
        # 탐색 성공 여부에 따른 응답 분기 처리
        if result:
            return jsonify({
                "status": "success",
                "timetable": result,
                "elapsed_time": f"{time.time() - start_time:.4f}초"
            }), 200
        else:
            return jsonify({
                "status": "fail",
                "message": "선택하신 과목들의 시간대가 충돌하거나 제약 조건을 만족하는 시간표 조합이 존재하지 않습니다."
            }), 404
            
    except TimeoutError as e:
        return jsonify({
            "status": "timeout",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"서버 내부 오류가 발생했습니다: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
