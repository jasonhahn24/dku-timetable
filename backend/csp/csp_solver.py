# -*- coding: utf-8 -*-
import json, re, time
import os


DAY_MAP = {"\uc6d4":"MON","\ud654":"TUE","\uc218":"WED","\ubaa9":"THU","\uae08":"FRI","\ud1a0":"SAT"}

PERIOD_TO_TIME = {
    1:"09:00", 2:"09:30", 3:"10:00", 4:"10:30",
    5:"11:00", 6:"11:30", 7:"12:00", 8:"12:30",
    9:"13:00", 10:"13:30", 11:"14:00", 12:"14:30",
    13:"15:00", 14:"15:30", 15:"16:00", 16:"16:30",
    17:"17:00", 18:"17:30", 19:"18:00", 20:"18:55",
    21:"19:50", 22:"20:45", 23:"21:40", 24:"22:35",
}


def parse_time_and_room(raw: str) -> list:
    slots = []
    raw = re.sub(r'\n+', '/', raw)
    raw = re.sub(r'/+', '/', raw)
    for block in raw.split("/"):
        block = block.strip()
        if not block:
            continue
        room_match = re.search(r'\(([^)]+)\)$', block)
        room = room_match.group(1) if room_match else ""
        slot_str = re.sub(r'\([^)]+\)', '', block).strip()
        if not slot_str:
            continue
        day_kor = slot_str[0]
        day_eng = DAY_MAP.get(day_kor, day_kor)
        period_str = slot_str[1:].strip()
        periods = []
        if "~" in period_str:
            parts = period_str.split("~")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                periods = list(range(int(parts[0]), int(parts[1]) + 1))
        else:
            for p in re.split(r"[,\s]+", period_str):
                if p.isdigit():
                    periods.append(int(p))
        times = [PERIOD_TO_TIME.get(p, str(p)) for p in periods]
        slots.append({
            "day": day_eng, "day_kor": day_kor,
            "periods": periods, "room": room,
            "start": times[0] if times else "",
            "end": times[-1] if times else "",
        })
    return slots


def load_courses(json_path: str) -> list:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for c in data:
        # 과목명 정리 (줄바꿈 이후 제거)
        if "\n" in c.get("name", ""):
            c["name"] = c["name"].split("\n")[0].strip()
        if c.get("time_raw"):
            c["slots"] = parse_time_and_room(c["time_raw"])
        # 학점 재파싱
        if isinstance(c.get("credit"), str):
            m = re.match(r'(\d+)', c["credit"])
            c["credit"] = int(m.group(1)) if m else 0
    return data


def has_time_overlap(slots_a, slots_b) -> bool:
    for sa in slots_a:
        for sb in slots_b:
            if sa["day"] == sb["day"] and set(sa["periods"]) & set(sb["periods"]):
                return True
    return False


def is_consistent(course, assigned) -> bool:
    for a in assigned:
        if has_time_overlap(course["slots"], a["slots"]):
            return False
    return True


def pre_filter(courses, constraints) -> list:
    filtered = []
    no_days    = constraints.get("no_class_days", [])
    no_periods = constraints.get("no_class_periods", [])
    no_online  = constraints.get("no_online", False)
    excluded   = constraints.get("excluded_courses", [])
    for c in courses:
        if c["name"] in excluded:
            continue
        if no_online and c.get("is_online", False):
            continue
        if not c.get("slots"):
            continue
        skip = False
        required_courses = constraints.get("required_courses", [])
        is_required = c["name"] in required_courses
        if not is_required:
            for slot in c["slots"]:
                if slot["day"] in no_days:
                    skip = True
                    break
        if skip:
            continue
        for slot in c["slots"]:
            for p in slot["periods"]:
                if p in no_periods:
                    skip = True
                    break
            if skip:
                break
        if skip:
            continue
        grade_filter = constraints.get("grade", "")
        if grade_filter:
            course_type = c.get("type", "")
            is_major = course_type in ["전공필수", "전공선택", "SW선택", "전공기초", "POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]
            if is_major:
                if str(c.get("grade", "")).strip() != str(grade_filter):
                    continue
        excluded_profs = constraints.get("excluded_professors", [])
        if any(p in c.get("professor", "") for p in excluded_profs):
            continue
        preferred_profs = constraints.get("preferred_professors", [])
        if preferred_profs:
            if not any(p in c.get("professor", "") for p in preferred_profs):
                if c["name"] not in constraints.get("required_courses", []):
                    continue
        lecture_types = constraints.get("lecture_types", [])
        if lecture_types:
            if c.get("lecture_type", "") not in lecture_types:
                continue
        user_dept = constraints.get("user_dept", "")
        if user_dept:
            course_type = c.get("type", "")
            course_dept = c.get("dept", "")
            is_major = course_type in ["전공필수", "전공선택", "SW선택", "전공기초"]
            if is_major and user_dept not in course_dept:
                continue
        filtered.append(c)
    return filtered


def ac3(course_groups: list) -> list:
    return course_groups


def backtrack(groups, assigned, results, max_results, timeout, start_time,
              target_credit=18, max_credit=19, optional_pool=None,
              constraints_ref=None):
    if time.time() - start_time > timeout:
        return
    if len(results) >= max_results:
        return

    current_credit = sum(c.get("credit", 0) for c in assigned)

    if not groups:
        min_credit = constraints_ref.get("min_credit", 12) if constraints_ref else 12
        if min_credit <= current_credit <= max_credit:
            required_types = (constraints_ref or {}).get("required_types", {})
            if required_types:
                type_count = {}
                for c in assigned:
                    t = c.get("type", "")
                    type_count[t] = type_count.get(t, 0) + 1
                if all(type_count.get(rt, 0) >= rc
                       for rt, rc in required_types.items()):
                    results.append(list(assigned))
            else:
                results.append(list(assigned))
        return

    current_group = min(groups, key=lambda g: len(g))
    remaining = [g for g in groups if g is not current_group]

    for course in current_group:
        if is_consistent(course, assigned):
            assigned.append(course)
            backtrack(remaining, assigned, results, max_results,
                      timeout, start_time, target_credit, max_credit,
                      optional_pool, constraints_ref)
            assigned.pop()


def score_timetable(timetable, constraints):
    score = 0
    breakdown = {}
    days_with_class = set()
    for course in timetable:
        for slot in course.get("slots", []):
            days_with_class.add(slot["day"])
    all_days = {"MON","TUE","WED","THU","FRI"}
    free_days = all_days - days_with_class
    no_days = constraints.get("no_class_days", [])
    day_to_eng = {"\uc6d4":"MON","\ud654":"TUE","\uc218":"WED","\ubaa9":"THU","\uae08":"FRI"}
    requested_free = [day_to_eng.get(d, d) for d in no_days]
    if all(d in free_days for d in requested_free) and requested_free:
        breakdown["\uacf5\uac15 \uc694\uc77c \ucda9\uc871"] = 30
        score += 30
    no_periods = constraints.get("no_class_periods", [])
    has_morning = any(
        p in no_periods
        for course in timetable
        for slot in course.get("slots", [])
        for p in slot["periods"]
    )
    if not has_morning and no_periods:
        breakdown["\uc544\uce68 \uc218\uc5c5 \uc5c6\uc74c"] = 20
        score += 20
    daily_periods = {}
    for course in timetable:
        for slot in course.get("slots", []):
            d = slot["day"]
            daily_periods[d] = daily_periods.get(d, 0) + len(slot["periods"])
    max_daily = max(daily_periods.values()) if daily_periods else 0
    if max_daily <= 6:
        breakdown["\ud558\ub8e8 \uad50\uc2dc \uc801\uc808"] = 25
        score += 25
    total_credit = sum(c.get("credit", 0) for c in timetable)
    target = constraints.get("target_credit", 18)
    if abs(total_credit - target) <= 3:
        breakdown["\ud559\uc810 \ubaa9\ud45c \uadfc\uc811"] = 15
        score += 15
    if len(free_days) >= 1:
        breakdown["\uacf5\uac15\uc77c \ubcf4\ub108\uc2a4"] = 10
        score += 10
    return {"total": score, "breakdown": breakdown}


def find_conflicts(constraints, filtered_courses):
    conflicts = []
    required = constraints.get("required_courses", [])
    no_days = constraints.get("no_class_days", [])
    no_periods = constraints.get("no_class_periods", [])

    json_path = os.path.join(os.path.dirname(__file__), "dku_courses_csp.json")
    all_courses = load_courses(json_path)

    for req in required:
        matching = [c for c in filtered_courses if req in c["name"]]
        all_matching = [c for c in all_courses if req in c["name"]]

        if not all_matching:
            conflicts.append({
                "type": "과목 없음",
                "desc": f"{req} 과목을 강의 데이터에서 찾을 수 없습니다.",
                "fix": "과목명을 정확히 입력했는지 확인해주세요."
            })
            continue

        # matching이 없거나, 있어도 전부 공강 요일인 경우 체크
        matching_not_in_no_days = [
            c for c in matching
            if not all(slot["day"] in no_days for slot in c.get("slots", []))
        ]

        if not matching_not_in_no_days:
            all_in_no_days = (
                bool(no_days) and
                all(
                    all(slot["day"] in no_days for slot in c.get("slots", []))
                    for c in matching if c.get("slots")
                )
            )

            if all_in_no_days:
                day_names = {"MON": "월", "TUE": "화", "WED": "수", "THU": "목", "FRI": "금"}
                days_str = ", ".join([day_names.get(d, d) for d in no_days])
                conflicts.append({
                    "type": "공강 충돌",
                    "desc": f"{req} 과목의 모든 분반이 공강 요일({days_str}요일)에만 개설되어 있습니다.",
                    "fix": f"공강 조건에서 해당 요일을 제거하거나 {req} 필수 조건을 해제해보세요."
                })
                continue

            conflicts.append({
                "type": "충돌",
                "desc": f"{req} 과목을 조건에 맞는 분반을 찾을 수 없습니다.",
                "fix": f"조건을 완화하면 {req}을 포함할 수 있습니다."
            })

    return conflicts


def generate_timetables(constraints, json_path="dku_courses_csp.json",
                         max_results=100, timeout=3.0):
    start = time.time()
    # 필수 교양 과목이 있으면 max_credit 자동 증가
    required_liberal_credit = 0
    all_courses_check = load_courses(json_path)
    for req in constraints.get("required_courses", []):
        for c in all_courses_check:
            if req in c.get("name", ""):
                t = c.get("type", "")
                major_types_check = ["전공필수", "전공선택", "SW선택", "전공기초",
                                     "POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]
                if t not in major_types_check:
                    required_liberal_credit += c.get("credit", 0)
                    break

    if required_liberal_credit > 0:
        constraints["max_credit"] = constraints.get("max_credit", 19) + required_liberal_credit
        constraints["target_credit"] = constraints.get("target_credit", 18) + required_liberal_credit

    all_courses = load_courses(json_path)
    filtered = pre_filter(all_courses, constraints)
    conflicts = find_conflicts(constraints, filtered)
    if conflicts:
        return {"solutions":[], "conflicts":conflicts,
                "total_found":0, "elapsed_ms":int((time.time()-start)*1000)}
    required_names = constraints.get("required_courses", [])
    required_groups = {}
    for name in required_names:
        seen = set()
        group = []
        for c in filtered:
            if name in c["name"] and c["id"] not in seen:
                seen.add(c["id"])
                group.append(c)
        if group:
            required_groups[name] = group

    seen_ids = set()
    unique_filtered = []
    for c in filtered:
        if c["id"] not in seen_ids:
            seen_ids.add(c["id"])
            unique_filtered.append(c)

    optional = [c for c in unique_filtered
                if not any(req in c["name"] for req in required_names)]
    
    optional_by_name = {}
    for c in optional:
        n = c["name"]
        if n not in optional_by_name:
            optional_by_name[n] = []
        optional_by_name[n].append(c)

    # 6. 전체 과목 그룹화 (과목명 기준, 중복 분반 제거)
    all_by_name = {}
    seen_all = set()
    user_dept = constraints.get("user_dept", "")
    major_types = ["전공필수", "전공선택", "SW선택", "전공기초", "POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]

    # 전공 과목은 학과 필터만 적용된 전체 데이터에서 가져옴
    all_courses_raw = load_courses(json_path)
    for c in all_courses_raw:
        if c["id"] in seen_all:
            continue
        # 제외 과목 체크
        excluded = constraints.get("excluded_courses", [])
        if any(ex in c["name"] for ex in excluded):
            continue
        t = c.get("type", "")
        dept = c.get("dept", "")
        is_major = t in major_types
        if is_major:
            pose_types = ["POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]
            if t in pose_types:
                pass  # POSE 과목은 학과 필터 없이 포함
            else:
                if user_dept and user_dept not in dept:
                    continue

            # 학년 필터 추가
            grade_filter = constraints.get("grade", "")
            if grade_filter:
                if str(c.get("grade", "")).strip() != str(grade_filter):
                    continue
            if not c.get("slots"):
                continue
            skip = False
            for slot in c["slots"]:
                if slot["day"] in constraints.get("no_class_days", []):
                    skip = True
                    break
            if skip:
                continue
            for slot in c["slots"]:
                for p in slot["periods"]:
                    if p in constraints.get("no_class_periods", []):
                        skip = True
                        break
                if skip:
                    break
            if skip:
                continue
            seen_all.add(c["id"])
            n = c["name"]
            if n not in all_by_name:
                all_by_name[n] = []
            all_by_name[n].append(c)

    # 비전공 과목은 filtered에서 가져옴
    required_names_set = set(required_names)
    for c in filtered:
        if c["id"] in seen_all:
            continue
        t = c.get("type", "")
        is_major = t in major_types
        if is_major:
            continue
        # 필수 과목으로 지정된 교양은 항상 포함, 아니면 include_liberal일 때만
        is_required = any(req in c["name"] for req in required_names_set)
        if not is_required and not constraints.get("include_liberal", False):
            continue
        # 학년 필터 (필수 과목은 제외)
        grade_filter = constraints.get("grade", "")
        if grade_filter and not is_required:
            if str(c.get("grade", "")).strip() != str(grade_filter):
                continue
        seen_all.add(c["id"])
        n = c["name"]
        if n not in all_by_name:
            all_by_name[n] = []
        all_by_name[n].append(c)

    # 7. 필수 과목 그룹 먼저
    groups = []
    for name in required_names:
        group = [c for c in all_by_name.get(name, [])
                 if name in c["name"]]
        if group:
            groups.append(group)

    # 8. 선택 과목 그룹 추가 (학점 목표까지)
    target_credit = constraints.get("target_credit", 18)  

    current_credit = sum(
        min(c.get("credit", 0) for c in g) for g in groups
    )
    # 선택 과목을 분반 수 적은 순으로 정렬해서 추가
    user_dept = constraints.get("user_dept", "")

    major_types_check = ["전공필수", "전공선택", "SW선택", "전공기초", "POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]
    real_major = [(n, g) for n, g in all_by_name.items()
                  if g and g[0].get("type", "") in major_types_check]
    print(f"user_dept: {user_dept}")
    print(f"all_by_name 과목 수: {len(all_by_name)}")
    print(f"실제 전공 과목 그룹 수: {len(real_major)}")
    for n, g in real_major:
        print(f"  {n} | {g[0].get('type','')} | {g[0].get('dept','')[:20]}")

    # 전공 과목 먼저 추가
    excluded_courses = constraints.get("excluded_courses", [])
    for name, group in all_by_name.items():
        if any(req in name for req in required_names):
            continue
        if not group:
            continue
        t = group[0].get("type", "")
        dept = group[0].get("dept", "")
        is_major = t in ["전공필수", "전공선택", "SW선택", "전공기초", "POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]
        if not is_major:
            continue
        pose_types = ["POSE-AI(English)", "POSE-AI(AI)", "POSE-AI(Open Source)"]
        if t not in pose_types:
            if user_dept and user_dept not in dept:
                continue
        avg = group[0].get("credit", 3)
        if avg == 0:
            continue
        if current_credit + avg <= constraints.get("max_credit", 19):
            groups.append(group)
            current_credit += avg
        if current_credit >= constraints.get("max_credit", 19):
            break

    # 전공으로 부족하면 교양으로 보충
    include_liberal = constraints.get("include_liberal", False)
    if include_liberal and current_credit < target_credit - 3:
        for name, group in all_by_name.items():
            if any(req in name for req in required_names):
                continue
            if not group:
                continue
            t = group[0].get("type", "")
            is_major = t in ["전공필수", "전공선택", "SW선택", "전공기초"]
            if is_major:
                continue
            avg = group[0].get("credit", 3)
            if avg == 0:
                continue
            valid_group = []
            for c in group:
                conflict = False
                for req_group in groups:
                    for req_c in req_group:
                        if has_time_overlap(c["slots"], req_c["slots"]):
                            conflict = True
                            break
                    if conflict:
                        break
                if not conflict:
                    valid_group.append(c)
            if valid_group:
                if current_credit + avg <= constraints.get("max_credit", 19):
                    groups.append(valid_group)
                    current_credit += avg
            if current_credit >= target_credit:
                break

    print(f"선택 과목 추가 후: {len(groups)}개 그룹, {current_credit}학점")
    for i, g in enumerate(groups):  
        slots_str = ' '.join(str(s['day_kor'])+str(s['periods']) for s in g[0]['slots'])
        print(f"  그룹{i}: {g[0]['name']} | {slots_str}")

    # 학점 부족 체크
    if current_credit < constraints.get("min_credit", 12):
        return {
            "solutions": [],
            "conflicts": [{
                "type": "\ud559\uc810 \ubd80\uc871",
                "desc": f"\ud604\uc7ac \uc870\uac74\uc73c\ub85c\ub294 {current_credit}\ud559\uc810\ubc16\uc5d0 \ucc44\uc6b8 \uc218 \uc5c6\uc5b4\uc694.",
                "fix": "\ud559\ub144 \uc81c\ud55c\uc744 \uc5c6\uc560\uac70\ub098 \uad50\uc591\uc744 \ucd94\uac00\ud574\ubcfc\uae4c\uc694?"
            }],
            "total_found": 0,
            "elapsed_ms": int((time.time() - start) * 1000)
        }

    # 9. MRV 순서로 정렬
    groups = sorted(groups, key=lambda g: len(g))

    # 10. 백트래킹 탐색
    results = []
    optional_pool = {k: v for k, v in all_by_name.items()
                     if not any(req in k for req in required_names)}
    backtrack(groups, [], results, max_results, timeout, start,
              target_credit, constraints.get("max_credit", 19),
              optional_pool, constraints)

    solutions = []
    for i, timetable in enumerate(results):
        sd = score_timetable(timetable, constraints)
        solutions.append({
            "rank": i+1, "score": sd["total"],
            "breakdown": sd["breakdown"],
            "timetable": timetable,
            "total_credit": sum(c.get("credit",0) for c in timetable),
        })
    solutions.sort(key=lambda x: -x["score"])
    for i, s in enumerate(solutions):
        s["rank"] = i+1
    return {"solutions":solutions, "conflicts":[],
            "total_found":len(solutions),
            "elapsed_ms":int((time.time()-start)*1000)}


if __name__ == "__main__":
    constraints = {
        "required_courses": [],
        "no_class_days": [],
        "no_class_periods": [],
        "no_online": False,
        "target_credit": 18,
        "max_credit": 19,
        "min_credit": 12,
        "user_dept": "\ucef4\ud4e8\ud130\uacf5\ud559\uacfc",
        "grade": "3",
        "include_liberal": False,
    }
    print("\uc2dc\uac04\ud45c \uc0dd\uc131 \uc911...")
    result = generate_timetables(constraints, "dku_courses_csp.json")
    print(f"\uc5f0\uc0b0 \uc2dc\uac04: {result['elapsed_ms']}ms")
    print(f"\ud6c4\ubcf4 \uc218: {result['total_found']}\uac1c")
    if result["conflicts"]:
        print("\n[\ucda9\ub3cc \ubc1c\uc0dd]")
        for c in result["conflicts"]:
            print(f"  {c['desc']}")
            print(f"  \ud574\uacb0: {c['fix']}")
    else:
        for sol in result["solutions"]:
            print(f"\n\ud6c4\ubcf4 {sol['rank']} ({sol['score']}\uc810, {sol['total_credit']}\ud559\uc810)")
            for c in sol["timetable"]:
                slots_str = " | ".join(
                    f"{s['day_kor']}{s['periods'][0] if s['periods'] else '?'}~"
                    f"{s['periods'][-1] if s['periods'] else '?'}({s['room']}) "
                    f"{s['start']}~{s['end']}"
                    for s in c.get("slots", [])
                )
                print(f"  {c['name']} / {c['professor']} / {slots_str}")

     # 디버그 추가
    if result["solutions"]:
        sol = result["solutions"][0]
        print("\n--- 디버그 ---")
        for c in sol["timetable"]:
            print(f"  name={c['name']} credit={c.get('credit')} type={type(c.get('credit'))}")