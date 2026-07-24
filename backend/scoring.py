from __future__ import annotations

import re
from typing import Any


def option_score(value: Any) -> int:
    if value == "Somewhat":
        return 1
    if value == "Very much":
        return 2
    text = str(value or "")
    match = re.search(r"\((\d+)\)", text)
    if match:
        return int(match.group(1))
    leading = re.match(r"^(\d+)\s*-", text)
    return int(leading.group(1)) if leading else 0


def option_score_nullable(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return option_score(value)


def yes_count(answers: dict[str, Any], keys: list[str]) -> int:
    return sum(1 for key in keys if answers.get(key) == "Yes")


def range_keys(prefix: str, start: int, end: int) -> list[str]:
    return [f"{prefix}_{item:02d}" for item in range(start, end + 1)]


def option_sum(answers: dict[str, Any], prefix: str, keys: list[str]) -> int:
    return sum(option_score(answers.get(f"{prefix}_{key}")) for key in keys)


def count_at_least(answers: dict[str, Any], keys: list[str], threshold: int) -> int:
    return sum(1 for key in keys if option_score(answers.get(key)) >= threshold)


def indexed_score(answers: dict[str, Any], key: str, options: list[str], base: int = 0) -> int | None:
    try:
        return options.index(answers.get(key)) + base
    except ValueError:
        return None


def reverse_indexed_score(answers: dict[str, Any], key: str, options: list[str], top_score: int) -> int | None:
    try:
        return top_score - options.index(answers.get(key))
    except ValueError:
        return None


def sum_nullable(scores: list[int | None]) -> int | None:
    return sum(score or 0 for score in scores) if any(score is not None for score in scores) else None


def build_asq_config(prefix: str, cutoffs: dict[str, float], zones: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
    areas = [
        ("communication", "Communication", "communication", "communication", "communication"),
        ("gross_motor", "Gross Motor", "gross", "gross", "gross_motor"),
        ("fine_motor", "Fine Motor", "fine", "fine", "fine_motor"),
        ("problem_solving", "Problem Solving", "problem", "problem", "problem_solving"),
        ("personal_social", "Personal-Social", "social", "social", "personal_social"),
    ]
    return [
        {
            "key": key,
            "label": label,
            "fieldPrefix": f"{prefix}_{answer_key}_",
            "totalFieldId": f"{prefix}_{total_key}_total",
            "summaryFieldId": f"{prefix}_summary_{summary_key}_score",
            "zoneFieldId": f"{prefix}_{summary_key}_zone",
            "cutoff": cutoffs[key],
            "zones": zones[key],
        }
        for key, label, answer_key, total_key, summary_key in areas
    ]


ASQ_SCORE_CONFIG: dict[str, list[dict[str, Any]]] = {
    "2-months-visit": [
        {"key": "communication", "label": "Communication", "fieldPrefix": "asq_comm_", "totalFieldId": "asq_communication_total", "summaryFieldId": "asq_summary_communication_score", "zoneFieldId": "asq_communication_zone", "cutoff": 22.77, "zones": {"belowMax": 20, "monitorMax": 35}},
        {"key": "gross_motor", "label": "Gross Motor", "fieldPrefix": "asq_gross_", "totalFieldId": "asq_gross_motor_total", "summaryFieldId": "asq_summary_gross_motor_score", "zoneFieldId": "asq_gross_motor_zone", "cutoff": 41.84, "zones": {"belowMax": 40, "monitorMax": 45}},
        {"key": "fine_motor", "label": "Fine Motor", "fieldPrefix": "asq_fine_", "totalFieldId": "asq_fine_motor_total", "summaryFieldId": "asq_summary_fine_motor_score", "zoneFieldId": "asq_fine_motor_zone", "cutoff": 30.16, "zones": {"belowMax": 30, "monitorMax": 40}},
        {"key": "problem_solving", "label": "Problem Solving", "fieldPrefix": "asq_problem_", "totalFieldId": "asq_problem_solving_total", "summaryFieldId": "asq_summary_problem_solving_score", "zoneFieldId": "asq_problem_solving_zone", "cutoff": 24.62, "zones": {"belowMax": 20, "monitorMax": 35}},
        {"key": "personal_social", "label": "Personal-Social", "fieldPrefix": "asq_social_", "totalFieldId": "asq_personal_social_total", "summaryFieldId": "asq_summary_personal_social_score", "zoneFieldId": "asq_personal_social_zone", "cutoff": 33.71, "zones": {"belowMax": 30, "monitorMax": 40}},
    ],
}

ASQ_SCORE_CONFIG["2-year-visit-maplewood"] = build_asq_config("asq24", {"communication": 25.17, "gross_motor": 38.07, "fine_motor": 35.16, "problem_solving": 29.78, "personal_social": 31.54}, {"communication": {"belowMax": 25, "monitorMax": 35}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 35, "monitorMax": 40}, "problem_solving": {"belowMax": 25, "monitorMax": 35}, "personal_social": {"belowMax": 30, "monitorMax": 40}})
ASQ_SCORE_CONFIG["2-year-visit-maplewood"][0]["fieldPrefix"] = "asq24_comm_"
ASQ_SCORE_CONFIG["2-year-visit-eagan"] = ASQ_SCORE_CONFIG["2-year-visit-maplewood"]
ASQ_SCORE_CONFIG["4-months-visit"] = build_asq_config("asq4", {"communication": 34.6, "gross_motor": 38.41, "fine_motor": 29.62, "problem_solving": 34.98, "personal_social": 33.16}, {"communication": {"belowMax": 30, "monitorMax": 40}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 25, "monitorMax": 40}, "problem_solving": {"belowMax": 30, "monitorMax": 45}, "personal_social": {"belowMax": 30, "monitorMax": 40}})
ASQ_SCORE_CONFIG["6-months-visit"] = build_asq_config("asq6", {"communication": 29.65, "gross_motor": 22.25, "fine_motor": 25.14, "problem_solving": 27.72, "personal_social": 25.34}, {"communication": {"belowMax": 25, "monitorMax": 40}, "gross_motor": {"belowMax": 20, "monitorMax": 35}, "fine_motor": {"belowMax": 25, "monitorMax": 40}, "problem_solving": {"belowMax": 25, "monitorMax": 35}, "personal_social": {"belowMax": 25, "monitorMax": 35}})
ASQ_SCORE_CONFIG["7-8-months-visit"] = build_asq_config("asq8", {"communication": 33.06, "gross_motor": 30.61, "fine_motor": 40.15, "problem_solving": 36.17, "personal_social": 35.84}, {"communication": {"belowMax": 30, "monitorMax": 40}, "gross_motor": {"belowMax": 30, "monitorMax": 35}, "fine_motor": {"belowMax": 40, "monitorMax": 45}, "problem_solving": {"belowMax": 35, "monitorMax": 40}, "personal_social": {"belowMax": 35, "monitorMax": 40}})
ASQ_SCORE_CONFIG["9-months-visit"] = build_asq_config("asq9", {"communication": 13.97, "gross_motor": 17.82, "fine_motor": 31.32, "problem_solving": 28.72, "personal_social": 18.91}, {"communication": {"belowMax": 10, "monitorMax": 30}, "gross_motor": {"belowMax": 15, "monitorMax": 30}, "fine_motor": {"belowMax": 30, "monitorMax": 40}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 15, "monitorMax": 30}})
ASQ_SCORE_CONFIG["10-months-visit"] = build_asq_config("asq10", {"communication": 22.87, "gross_motor": 30.07, "fine_motor": 37.97, "problem_solving": 32.51, "personal_social": 27.25}, {"communication": {"belowMax": 20, "monitorMax": 35}, "gross_motor": {"belowMax": 30, "monitorMax": 40}, "fine_motor": {"belowMax": 35, "monitorMax": 45}, "problem_solving": {"belowMax": 30, "monitorMax": 40}, "personal_social": {"belowMax": 25, "monitorMax": 35}})
ASQ_SCORE_CONFIG["12-months-visit-eagan"] = build_asq_config("asq12", {"communication": 15.64, "gross_motor": 21.49, "fine_motor": 34.5, "problem_solving": 27.32, "personal_social": 21.73}, {"communication": {"belowMax": 15, "monitorMax": 30}, "gross_motor": {"belowMax": 20, "monitorMax": 35}, "fine_motor": {"belowMax": 30, "monitorMax": 40}, "problem_solving": {"belowMax": 25, "monitorMax": 35}, "personal_social": {"belowMax": 20, "monitorMax": 35}})
ASQ_SCORE_CONFIG["12-months-visit-maplewood"] = ASQ_SCORE_CONFIG["12-months-visit-eagan"]
ASQ_SCORE_CONFIG["14-months-visit"] = build_asq_config("asq14", {"communication": 17.4, "gross_motor": 25.8, "fine_motor": 23.06, "problem_solving": 22.56, "personal_social": 23.18}, {"communication": {"belowMax": 15, "monitorMax": 30}, "gross_motor": {"belowMax": 25, "monitorMax": 40}, "fine_motor": {"belowMax": 20, "monitorMax": 35}, "problem_solving": {"belowMax": 20, "monitorMax": 35}, "personal_social": {"belowMax": 20, "monitorMax": 35}})
ASQ_SCORE_CONFIG["15-months-visit"] = build_asq_config("asq15", {"communication": 16.81, "gross_motor": 37.91, "fine_motor": 31.98, "problem_solving": 30.51, "personal_social": 26.43}, {"communication": {"belowMax": 15, "monitorMax": 30}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 30, "monitorMax": 40}, "problem_solving": {"belowMax": 30, "monitorMax": 40}, "personal_social": {"belowMax": 25, "monitorMax": 35}})
ASQ_SCORE_CONFIG["18-months-visit"] = build_asq_config("asq18", {"communication": 13.06, "gross_motor": 37.38, "fine_motor": 34.32, "problem_solving": 25.74, "personal_social": 27.19}, {"communication": {"belowMax": 10, "monitorMax": 30}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 30, "monitorMax": 40}, "problem_solving": {"belowMax": 25, "monitorMax": 35}, "personal_social": {"belowMax": 25, "monitorMax": 35}})
ASQ_SCORE_CONFIG["20-months-visit"] = build_asq_config("asq20", {"communication": 20.5, "gross_motor": 39.89, "fine_motor": 36.05, "problem_solving": 28.84, "personal_social": 33.36}, {"communication": {"belowMax": 20, "monitorMax": 35}, "gross_motor": {"belowMax": 35, "monitorMax": 50}, "fine_motor": {"belowMax": 35, "monitorMax": 45}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 30, "monitorMax": 45}})
ASQ_SCORE_CONFIG["22-months-visit"] = build_asq_config("asq22", {"communication": 13.04, "gross_motor": 27.75, "fine_motor": 29.61, "problem_solving": 29.3, "personal_social": 30.07}, {"communication": {"belowMax": 10, "monitorMax": 25}, "gross_motor": {"belowMax": 25, "monitorMax": 40}, "fine_motor": {"belowMax": 25, "monitorMax": 40}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 30, "monitorMax": 40}})
ASQ_SCORE_CONFIG["27-months-visit"] = build_asq_config("asq27", {"communication": 24.02, "gross_motor": 28.01, "fine_motor": 18.42, "problem_solving": 27.62, "personal_social": 25.31}, {"communication": {"belowMax": 20, "monitorMax": 35}, "gross_motor": {"belowMax": 25, "monitorMax": 40}, "fine_motor": {"belowMax": 15, "monitorMax": 30}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 25, "monitorMax": 35}})
ASQ_SCORE_CONFIG["30-months-visit"] = build_asq_config("asq30", {"communication": 33.3, "gross_motor": 36.14, "fine_motor": 19.25, "problem_solving": 27.08, "personal_social": 32.01}, {"communication": {"belowMax": 30, "monitorMax": 45}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 15, "monitorMax": 30}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 30, "monitorMax": 45}})
ASQ_SCORE_CONFIG["33-months-visit"] = build_asq_config("asq33", {"communication": 25.36, "gross_motor": 34.8, "fine_motor": 12.28, "problem_solving": 26.92, "personal_social": 28.96}, {"communication": {"belowMax": 25, "monitorMax": 40}, "gross_motor": {"belowMax": 30, "monitorMax": 45}, "fine_motor": {"belowMax": 10, "monitorMax": 25}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 25, "monitorMax": 40}})
ASQ_SCORE_CONFIG["3-year-visit"] = build_asq_config("asq36", {"communication": 30.99, "gross_motor": 36.99, "fine_motor": 18.07, "problem_solving": 30.29, "personal_social": 35.33}, {"communication": {"belowMax": 30, "monitorMax": 40}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 15, "monitorMax": 30}, "problem_solving": {"belowMax": 30, "monitorMax": 40}, "personal_social": {"belowMax": 35, "monitorMax": 45}})
ASQ_SCORE_CONFIG["42-months-visit"] = build_asq_config("asq42", {"communication": 27.06, "gross_motor": 36.27, "fine_motor": 19.82, "problem_solving": 28.11, "personal_social": 31.12}, {"communication": {"belowMax": 25, "monitorMax": 40}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 15, "monitorMax": 30}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 30, "monitorMax": 40}})
ASQ_SCORE_CONFIG["4-year-visit"] = build_asq_config("asq48", {"communication": 30.72, "gross_motor": 32.78, "fine_motor": 15.81, "problem_solving": 31.3, "personal_social": 26.6}, {"communication": {"belowMax": 30, "monitorMax": 40}, "gross_motor": {"belowMax": 30, "monitorMax": 40}, "fine_motor": {"belowMax": 15, "monitorMax": 30}, "problem_solving": {"belowMax": 30, "monitorMax": 40}, "personal_social": {"belowMax": 25, "monitorMax": 35}})
ASQ_SCORE_CONFIG["54-months-visit"] = build_asq_config("asq54", {"communication": 31.85, "gross_motor": 35.18, "fine_motor": 17.32, "problem_solving": 28.12, "personal_social": 32.33}, {"communication": {"belowMax": 30, "monitorMax": 40}, "gross_motor": {"belowMax": 35, "monitorMax": 45}, "fine_motor": {"belowMax": 15, "monitorMax": 30}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 30, "monitorMax": 45}})
ASQ_SCORE_CONFIG["5-year-visit"] = build_asq_config("asq60", {"communication": 33.19, "gross_motor": 31.28, "fine_motor": 26.54, "problem_solving": 29.99, "personal_social": 39.07}, {"communication": {"belowMax": 30, "monitorMax": 40}, "gross_motor": {"belowMax": 30, "monitorMax": 40}, "fine_motor": {"belowMax": 25, "monitorMax": 35}, "problem_solving": {"belowMax": 25, "monitorMax": 40}, "personal_social": {"belowMax": 35, "monitorMax": 45}})


def asq_answer_score(value: Any) -> int | None:
    return {"Yes": 10, "Sometimes": 5, "Not Yet": 0}.get(value)


def asq_zone(area: dict[str, Any], total: int | None) -> dict[str, str]:
    if total is None:
        return {"key": "incomplete", "label": "Incomplete", "value": ""}
    if total <= area["zones"]["belowMax"]:
        return {"key": "below", "label": "Delayed", "value": "Delayed"}
    if total <= area["zones"]["monitorMax"]:
        return {"key": "monitor", "label": "Close to cutoff", "value": "Close to cutoff"}
    return {"key": "above", "label": "On schedule", "value": "Above cutoff"}


def calculate_asq_scores(form_id: str, answers: dict[str, Any]) -> list[dict[str, Any]]:
    scores: list[dict[str, Any]] = []
    for area in ASQ_SCORE_CONFIG.get(form_id, []):
        item_scores = [asq_answer_score(answers.get(f"{area['fieldPrefix']}{index}")) for index in range(1, 7)]
        complete = all(score is not None for score in item_scores)
        total = sum(score or 0 for score in item_scores) if complete else None
        scores.append({**area, "itemScores": item_scores, "complete": complete, "total": total, "zone": asq_zone(area, total)})
    return scores


EPDS_LEGACY_KEYS = ["epds_laugh", "epds_enjoyment", "epds_blame", "epds_anxious", "epds_scared", "epds_coping", "epds_sleeping", "epds_sad", "epds_crying", "epds_self_harm"]


def epds_score_for(index: int, value: Any) -> int | None:
    if not value:
        return None
    text = str(value)
    scoring = {
        1: [("As much as", 0), ("Not quite so much", 1), ("Definitely not so much", 2), ("Not at all", 3)],
        2: [("As much as", 0), ("Rather less", 1), ("Definitely less", 2), ("Hardly at all", 3)],
        3: [("Yes, most of the time", 3), ("Yes, some of the time", 2), ("Not very often", 1), ("No, never", 0)],
        4: [("No, not at all", 0), ("Hardly ever", 1), ("Yes, sometimes", 2), ("Yes, very often", 3)],
        5: [("Yes, quite a lot", 3), ("Yes, sometimes", 2), ("No, not much", 1), ("No, not at all", 0)],
        6: [("Yes, most of the time", 3), ("Yes, sometimes", 2), ("No, most of the time", 1), ("No, I have been coping", 0)],
        7: [("Yes, most of the time", 3), ("Yes, sometimes", 2), ("Not very often", 1), ("No, not at all", 0)],
        8: [("Yes, most of the time", 3), ("Yes, quite often", 2), ("Not very often", 1), ("No, not at all", 0)],
        9: [("Yes, most of the time", 3), ("Yes, quite often", 2), ("Only occasionally", 1), ("No, never", 0)],
        10: [("Yes, quite often", 3), ("Sometimes", 2), ("Hardly ever", 1), ("Never", 0)],
    }
    for label, score in scoring.get(index, []):
        if text.startswith(label):
            return score
    return option_score(value)


def calculate_epds_total(answers: dict[str, Any]) -> int | None:
    numbered = [f"epds_{index}" for index in range(1, 11)]
    keys = numbered if any(answers.get(key) for key in numbered) else EPDS_LEGACY_KEYS
    scores = [epds_score_for(index, answers.get(key)) for index, key in enumerate(keys, start=1)]
    return sum(score or 0 for score in scores) if any(score is not None for score in scores) else None


def add_vanderbilt_scores(next_answers: dict[str, Any], answers: dict[str, Any], prefix: str, config: dict[str, Any]) -> None:
    if not any(answers.get(key) for key in range_keys(prefix, 1, config["symptomEnd"])):
        return
    for key, start, end in config["domains"]:
        next_answers[f"{prefix}_{key}"] = str(count_at_least(answers, range_keys(prefix, start, end), 2))
    performance_keys = [f"{prefix}_performance_{index:02d}" for index in range(1, config["performanceCount"] + 1)]
    performance4 = count_at_least(answers, performance_keys, 4)
    performance5 = sum(1 for key in performance_keys if option_score(answers.get(key)) == 5)
    next_answers[f"{prefix}_performance_4_count"] = str(performance4 - performance5)
    next_answers[f"{prefix}_performance_5_count"] = str(performance5)
    next_answers[f"{prefix}_impairment_present"] = "Yes" if performance4 > 0 else "No"


def add_scared_scores(next_answers: dict[str, Any], answers: dict[str, Any], prefix: str) -> None:
    if not any(answers.get(key) for key in range_keys(prefix, 1, 41)):
        return
    groups = {
        "panic_somatic": [1, 6, 9, 12, 15, 18, 19, 22, 24, 27, 30, 34, 38],
        "generalized_anxiety": [5, 7, 14, 21, 23, 28, 33, 35, 37],
        "separation_anxiety": [4, 8, 13, 16, 20, 25, 29, 31],
        "social_anxiety": [3, 10, 26, 32, 39, 40, 41],
        "school_avoidance": [2, 11, 17, 36],
    }
    totals = {
        key: sum(option_score(answers.get(f"{prefix}_{item:02d}")) for item in items)
        for key, items in groups.items()
    }
    total = sum(option_score(answers.get(key)) for key in range_keys(prefix, 1, 41))
    next_answers[f"{prefix}_total_score"] = str(total)
    for key, value in totals.items():
        next_answers[f"{prefix}_{key}_score"] = str(value)
    next_answers[f"{prefix}_total_cutoff_met"] = "Yes" if total >= 25 else "No"
    next_answers[f"{prefix}_panic_somatic_cutoff_met"] = "Yes" if totals["panic_somatic"] >= 7 else "No"
    next_answers[f"{prefix}_generalized_anxiety_cutoff_met"] = "Yes" if totals["generalized_anxiety"] >= 9 else "No"
    next_answers[f"{prefix}_separation_anxiety_cutoff_met"] = "Yes" if totals["separation_anxiety"] >= 5 else "No"
    next_answers[f"{prefix}_social_anxiety_cutoff_met"] = "Yes" if totals["social_anxiety"] >= 8 else "No"
    next_answers[f"{prefix}_school_avoidance_cutoff_met"] = "Yes" if totals["school_avoidance"] >= 3 else "No"


def asrs_positive(key: str, value: Any) -> bool:
    if not value:
        return False
    positive_from_sometimes = {"wrap_up", "organization", "remembering"}
    try:
        index = ["Never", "Rarely", "Sometimes", "Often", "Very often"].index(value)
    except ValueError:
        return False
    return index >= 2 if key in positive_from_sometimes else index >= 3


def add_calculated_scores(form_id: str, answers: dict[str, Any]) -> dict[str, Any]:
    next_answers = dict(answers or {})
    for score in calculate_asq_scores(form_id, next_answers):
        next_answers[score["totalFieldId"]] = "" if score["total"] is None else str(score["total"])
        next_answers[score["summaryFieldId"]] = "" if score["total"] is None else str(score["total"])
        next_answers[score["zoneFieldId"]] = score["zone"]["value"]

    epds = calculate_epds_total(next_answers)
    if epds is not None:
        next_answers["epds_total_score"] = str(epds)

    phq2_scores = [option_score_nullable(next_answers.get("phq2_interest")), option_score_nullable(next_answers.get("phq2_down_depressed"))]
    if all(score is not None for score in phq2_scores):
        next_answers["phq2_total_score"] = str(sum(score or 0 for score in phq2_scores))

    act = sum_nullable([
        indexed_score(next_answers, "activity_limit", ["All of the time", "Most of the time", "Some of the time", "A little of the time", "None of the time"], 1),
        indexed_score(next_answers, "shortness_breath", ["More than once a day", "Once a day", "3 to 6 times a week", "Once or twice a week", "Not at all"], 1),
        indexed_score(next_answers, "night_symptoms", ["4 or more nights a week", "2 or 3 nights a week", "Once a week", "Once or twice", "Not at all"], 1),
        indexed_score(next_answers, "rescue_inhaler", ["3 or more times per day", "1 or 2 times per day", "2 or 3 times per week", "Once a week or less", "Not at all"], 1),
        indexed_score(next_answers, "control_rating", ["Not controlled at all", "Poorly controlled", "Somewhat controlled", "Well controlled", "Completely controlled"], 1),
    ])
    if act is not None:
        next_answers["act_total_score"] = str(act)
        next_answers["act_control_status"] = "May not be controlled" if act <= 19 else "Likely controlled"

    cact = sum_nullable([
        indexed_score(next_answers, "asthma_today", ["Very bad", "Bad", "Good", "Very good"], 0),
        indexed_score(next_answers, "problem_when_active", ["It is a big problem", "It is a problem", "It is a little problem", "It is not a problem"], 0),
        indexed_score(next_answers, "cough", ["Yes, all of the time", "Yes, most of the time", "Yes, some of the time", "No, none of the time"], 0),
        indexed_score(next_answers, "wake_up", ["Yes, all of the time", "Yes, most of the time", "Yes, some of the time", "No, none of the time"], 0),
        reverse_indexed_score(next_answers, "daytime_symptoms", ["Not at all", "1-3 days", "4-10 days", "11-18 days", "19-24 days", "Every day"], 5),
        reverse_indexed_score(next_answers, "wheezing", ["Not at all", "1-3 days", "4-10 days", "11-18 days", "19-24 days", "Every day"], 5),
        reverse_indexed_score(next_answers, "night_waking", ["Not at all", "1-3 days", "4-10 days", "11-18 days", "19-24 days", "Every day"], 5),
    ])
    if cact is not None:
        next_answers["cact_total_score"] = str(cact)
        next_answers["cact_control_status"] = "May not be controlled" if cact <= 19 else "Likely controlled"

    add_vanderbilt_scores(next_answers, next_answers, "vanderbilt_parent", {"symptomEnd": 48, "performanceCount": 8, "domains": [("inattention", 1, 9), ("hyperactive_impulsive", 10, 18), ("oppositional", 19, 26), ("conduct", 27, 41), ("anxiety_depression", 42, 48)]})
    add_vanderbilt_scores(next_answers, next_answers, "vanderbilt_teacher", {"symptomEnd": 35, "performanceCount": 8, "domains": [("inattention", 1, 9), ("hyperactive_impulsive", 10, 18), ("oppositional_conduct", 19, 28), ("anxiety_depression", 29, 35)]})
    add_vanderbilt_scores(next_answers, next_answers, "vanderbilt_parent_followup", {"symptomEnd": 26, "performanceCount": 8, "domains": [("inattention", 1, 9), ("hyperactive_impulsive", 10, 18), ("oppositional", 19, 26)]})
    add_vanderbilt_scores(next_answers, next_answers, "vanderbilt_teacher_followup", {"symptomEnd": 28, "performanceCount": 8, "domains": [("inattention", 1, 9), ("hyperactive_impulsive", 10, 18), ("oppositional_conduct", 19, 28)]})
    add_scared_scores(next_answers, next_answers, "child_scared")
    add_scared_scores(next_answers, next_answers, "parent_scared")

    part_a = ["wrap_up", "organization", "remembering", "avoid_delay", "fidget", "driven"]
    part_b = ["careless_mistakes", "attention_boring_work", "concentrating_on_people", "misplace_things", "distracted_by_noise", "leave_seat", "restless", "difficulty_relaxing", "talking_too_much", "finish_sentences", "waiting_turn", "interrupt_busy"]
    if any(next_answers.get(key) for key in [*part_a, *part_b]):
        part_a_positive = sum(1 for key in part_a if asrs_positive(key, next_answers.get(key)))
        next_answers["asrs_part_a_positive_count"] = str(part_a_positive)
        next_answers["asrs_part_b_positive_count"] = str(sum(1 for key in part_b if asrs_positive(key, next_answers.get(key))))
        next_answers["asrs_screen_result"] = "Positive screen" if part_a_positive >= 4 else "Negative screen"

    if any(key.startswith(("ace_physical_", "ace_cognitive_", "ace_emotional_", "ace_sleep_")) for key in next_answers):
        physical = yes_count(next_answers, [f"ace_physical_{index:02d}" for index in range(1, 11)])
        cognitive = yes_count(next_answers, [f"ace_cognitive_{index:02d}" for index in range(1, 5)])
        emotional = yes_count(next_answers, [f"ace_emotional_{index:02d}" for index in range(1, 5)])
        sleep = yes_count(next_answers, [f"ace_sleep_{index:02d}" for index in range(1, 5)])
        next_answers["ace_physical_total"] = str(physical)
        next_answers["ace_cognitive_total"] = str(cognitive)
        next_answers["ace_emotional_total"] = str(emotional)
        next_answers["ace_sleep_total"] = str(sleep)
        next_answers["ace_total_symptom_score"] = str(physical + cognitive + emotional + sleep)
        next_answers["ace_red_flag_count"] = str(len(next_answers.get("ace_red_flags") or []))

    phqa_keys = ["1_depressed", "2_interest", "3_sleep", "4_appetite", "5_tired", "6_bad_self", "7_concentration", "8_moving", "9_self_harm"]
    if any(next_answers.get(f"phqa_{key}") for key in phqa_keys):
        next_answers["phqa_total_score"] = str(option_sum(next_answers, "phqa", phqa_keys))
    phq9_keys = ["1_interest", "2_depressed", "3_sleep", "4_tired", "5_appetite", "6_bad_self", "7_concentration", "8_moving", "9_self_harm"]
    if any(next_answers.get(f"phq9_{key}") for key in phq9_keys):
        next_answers["phq9_total_score"] = str(option_sum(next_answers, "phq9", phq9_keys))
    gad_keys = ["1", "2", "3", "4", "5", "6", "7"]
    if any(next_answers.get(f"gad7_{key}") for key in gad_keys):
        next_answers["gad7_total_score"] = str(option_sum(next_answers, "gad7", gad_keys))

    crafft_a = ["crafft_a_alcohol", "crafft_a_marijuana", "crafft_a_other_high"]
    crafft_b = ["crafft_b_car", "crafft_b_relax", "crafft_b_alone", "crafft_b_forget", "crafft_b_family_friends", "crafft_b_trouble"]
    if any(next_answers.get(key) for key in [*crafft_a, *crafft_b]):
        next_answers["crafft_part_a_yes_count"] = str(yes_count(next_answers, crafft_a))
        next_answers["crafft_part_b_yes_count"] = str(yes_count(next_answers, crafft_b))

    if any(key.startswith("psc17_") and re.match(r"^psc17_\d+_", key) for key in next_answers):
        internalizing = ["psc17_2_sad", "psc17_6_hopeless", "psc17_9_down_on_self", "psc17_11_less_fun", "psc17_15_worries"]
        attention = ["psc17_1_fidgety", "psc17_3_daydreams", "psc17_7_trouble_concentrating", "psc17_13_driven_by_motor", "psc17_17_distracted"]
        externalizing = ["psc17_4_refuses_share", "psc17_5_does_not_understand", "psc17_8_fights", "psc17_10_blames_others", "psc17_12_does_not_listen", "psc17_14_teases", "psc17_16_takes_things"]
        internalizing_score = sum(option_score(next_answers.get(key)) for key in internalizing)
        attention_score = sum(option_score(next_answers.get(key)) for key in attention)
        externalizing_score = sum(option_score(next_answers.get(key)) for key in externalizing)
        total = internalizing_score + attention_score + externalizing_score
        next_answers["psc17_internalizing_score"] = str(internalizing_score)
        next_answers["psc17_attention_score"] = str(attention_score)
        next_answers["psc17_externalizing_score"] = str(externalizing_score)
        next_answers["psc17_total_score"] = str(total)
        next_answers["psc17_internalizing_cutoff_met"] = "Yes" if internalizing_score >= 5 else "No"
        next_answers["psc17_attention_cutoff_met"] = "Yes" if attention_score >= 7 else "No"
        next_answers["psc17_externalizing_cutoff_met"] = "Yes" if externalizing_score >= 7 else "No"
        next_answers["psc17_total_cutoff_met"] = "Yes" if total >= 15 else "No"

    ppsc_exclusions = {"ppsc_child_name", "ppsc_birth_date", "ppsc_today_date", "ppsc_total_score", "ppsc_staff_notes"}
    ppsc_keys = [key for key in next_answers if key.startswith("ppsc_") and key not in ppsc_exclusions]
    if any(next_answers.get(key) for key in ppsc_keys):
        next_answers["ppsc_total_score"] = str(sum(option_score(next_answers.get(key)) for key in ppsc_keys))

    mchat_risk_yes = {"mchat_11", "mchat_18", "mchat_20", "mchat_22"}
    mchat_keys = [f"mchat_{index}" for index in range(1, 24)]
    if any(next_answers.get(key) for key in mchat_keys):
        risk = 0
        for key in mchat_keys:
            value = next_answers.get(key)
            if value:
                risk += 1 if (value == "Yes" if key in mchat_risk_yes else value == "No") else 0
        next_answers["mchat_risk_score"] = str(risk)
        next_answers["mchat_risk_level"] = "High risk" if risk >= 8 else "Medium risk" if risk >= 3 else "Low risk"

    return next_answers


def review_for_submission(submission: dict[str, Any]) -> dict[str, Any]:
    if submission.get("status") == "draft":
        return {"flags": [], "status": "draft", "label": "Draft"}
    answers = submission.get("answers") or {}
    flags: list[dict[str, str]] = []
    asq_scores = calculate_asq_scores(submission.get("formId", ""), answers)
    below_count = sum(1 for score in asq_scores if score["zone"]["key"] == "below")
    monitor_count = sum(1 for score in asq_scores if score["zone"]["key"] == "monitor")
    incomplete_count = sum(1 for score in asq_scores if score["zone"]["key"] == "incomplete")
    if below_count:
        flags.append({"key": "asq-below", "type": "asq", "severity": "high", "label": f"{below_count} ASQ delayed"})
    if monitor_count:
        flags.append({"key": "asq-monitor", "type": "asq", "severity": "medium", "label": f"{monitor_count} ASQ monitor"})
    if incomplete_count:
        flags.append({"key": "asq-incomplete", "type": "asq", "severity": "low", "label": "ASQ incomplete"})
    if any(str(answers.get(key) or "") and str(answers.get(key) or "") != "No" and not str(answers.get(key) or "").startswith("Not at all") for key in ["phqa_9_self_harm", "phqa_suicide_ever", "phqa_suicide_attempt"]):
        flags.append({"key": "self-harm", "type": "behavioral", "severity": "high", "label": "Self-harm review"})
    epds_total = calculate_epds_total(answers)
    if epds_total is not None and epds_total >= 10:
        flags.append({"key": "epds", "type": "behavioral", "severity": "medium", "label": "EPDS elevated"})
    if any(str(answers.get(key) or "") and not any(str(answers.get(key) or "").startswith(safe) for safe in ["Never", "No, never", "No, not at all"]) for key in ["epds_10", "epds_self_harm"]):
        flags.append({"key": "epds-self-harm", "type": "behavioral", "severity": "high", "label": "EPDS self-harm review"})
    if any(key.startswith("phqa_") and "(2)" in str(value) for key, value in answers.items()):
        flags.append({"key": "phqa", "type": "behavioral", "severity": "medium", "label": "PHQ-A symptom review"})
    if any(key.startswith("crafft_") and value == "Yes" for key, value in answers.items()):
        flags.append({"key": "crafft", "type": "behavioral", "severity": "medium", "label": "CRAFFT positive"})
    if int(answers.get("gad7_total_score") or 0) >= 10:
        flags.append({"key": "gad7", "type": "behavioral", "severity": "medium", "label": "GAD-7 elevated"})
    if int(answers.get("phq9_total_score") or 0) >= 10:
        flags.append({"key": "phq9", "type": "behavioral", "severity": "medium", "label": "PHQ-9 elevated"})
    if answers.get("phq9_9_self_harm") and not str(answers["phq9_9_self_harm"]).startswith("Not at all"):
        flags.append({"key": "phq9-self-harm", "type": "behavioral", "severity": "high", "label": "PHQ-9 self-harm review"})
    if int(answers.get("ppsc_total_score") or 0) >= 9:
        flags.append({"key": "ppsc", "type": "behavioral", "severity": "medium", "label": "PPSC elevated"})
    mchat_score = int(answers.get("mchat_risk_score") or 0)
    if mchat_score >= 8:
        flags.append({"key": "mchat-high", "type": "behavioral", "severity": "high", "label": "M-CHAT high risk"})
    elif mchat_score >= 3:
        flags.append({"key": "mchat-medium", "type": "behavioral", "severity": "medium", "label": "M-CHAT medium risk"})
    if answers.get("sdoh_help_wanted") == "Yes":
        flags.append({"key": "sdoh", "type": "social", "severity": "medium", "label": "SDOH help requested"})
    if submission.get("status") in {"needs-follow-up", "needs-patient-follow-up"}:
        flags.append({"key": "status-follow-up", "type": "status", "severity": "high", "label": "Needs patient follow-up"})
    has_review_flag = any(flag["severity"] in {"high", "medium"} for flag in flags)
    if has_review_flag:
        review_status = "needs-review"
        review_label = "Needs review"
    elif submission.get("status") == "ready-for-chart":
        review_status = "ready-for-chart"
        review_label = "Ready for chart"
    elif submission.get("status") == "complete":
        review_status = "complete"
        review_label = "Completed"
    else:
        review_status = "routine"
        review_label = "Routine"
    return {"flags": flags, "status": review_status, "label": review_label}
