# ac3.py

def parse_time_slots(time_str):
    """'월3,월4,수5' 문자열을 {'월3', '월4', '수5'} 세트로 변환"""
    if not time_str or time_str == "지정되지 않음":
        return set()
    return set(time_str.split(','))

def ac3(domains, constraints):
    """
    domains: { "국어": [{"time": "월1,월2"}, ...], "수학": [...] }
    constraints: { "no_class_days": ["금"], "no_morning": True } 등
    """
    if not constraints:
        return domains

    filtered_domains = {}
    no_class_days = constraints.get("no_class_days", [])
    no_morning = constraints.get("no_morning", False)

    for course, classes in domains.items():
        valid_classes = []
        for cls in classes:
            slots = parse_time_slots(cls.get("time", ""))
            is_valid = True

            for slot in slots:
                if len(slot) < 2:
                    continue
                
                day = slot[0]         # '월', '화', '수' 등 요일 추출
                try:
                    period = int(slot[1:]) # '3', '4' 등 교시 숫자 추출
                except ValueError:
                    continue

                # 1. 특정 요일 공강 제약 조건 체크
                if day in no_class_days:
                    is_valid = False
                    break

                # 2. 아침 수업 회피 제약 조건 체크 (1, 2교시 제외)
                if no_morning and period in [1, 2]:
                    is_valid = False
                    break

            if is_valid:
                valid_classes.append(cls)
        
        # 필터링된 분반 리스트를 저장
        filtered_domains[course] = valid_classes

    return filtered_domains
