from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from scoring import ASQ_SCORE_CONFIG, add_calculated_scores  # noqa: E402


TEMPLATES_FILE = BACKEND / "data" / "form-templates.json"
ALLOWED_FIELD_TYPES = {
    "text",
    "email",
    "tel",
    "date",
    "number",
    "datetime-local",
    "textarea",
    "select",
    "radio",
    "multicheck",
    "checkbox",
    "scale",
    "signature",
}


def load_templates() -> list[dict[str, Any]]:
    with TEMPLATES_FILE.open("r", encoding="utf-8-sig") as handle:
        templates = json.load(handle)
    return [template for template in templates if template.get("status", "active") == "active"]


def iter_fields(template: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for section in template.get("sections") or []:
        fields.extend(section.get("fields") or [])
    return fields


def check_templates(templates: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [template.get("id") for template in templates]
    duplicate_template_ids = sorted(item for item, count in Counter(ids).items() if item and count > 1)
    if duplicate_template_ids:
        errors.append(f"Duplicate active template ids: {', '.join(duplicate_template_ids[:10])}")

    for template in templates:
        form_id = template.get("id") or "<missing-id>"
        for key in ["id", "name", "category", "sections"]:
            if not template.get(key):
                errors.append(f"{form_id}: missing required template key {key}")
        if not isinstance(template.get("sections"), list):
            errors.append(f"{form_id}: sections must be a list")
            continue

        fields = iter_fields(template)
        field_ids = [str(field.get("id")) for field in fields if field.get("id")]
        duplicate_field_ids = sorted(item for item, count in Counter(field_ids).items() if count > 1)
        if duplicate_field_ids:
            errors.append(f"{form_id}: duplicate field ids: {', '.join(duplicate_field_ids[:10])}")

        for field in fields:
            field_id = field.get("id") or "<missing-id>"
            field_type = field.get("type")
            if not field.get("id") or not field.get("label") or not field_type:
                errors.append(f"{form_id}: field needs id, label, and type")
            if field_type not in ALLOWED_FIELD_TYPES:
                errors.append(f"{form_id}: field {field_id} uses unsupported type {field_type}")
            if field_type in {"radio", "select", "multicheck", "scale"} and not isinstance(field.get("options", []), list):
                errors.append(f"{form_id}: field {field_id} options must be a list")

        field_set = set(field_ids)
        detected_asq_prefixes = sorted({field_id.rsplit("_", 1)[0] for field_id in field_set if re.match(r"^.+_\d+$", field_id) and field_id.rsplit("_", 1)[1].isdigit()})
        for prefix in detected_asq_prefixes:
            asq_like = any(prefix.startswith(area["fieldPrefix"].rstrip("_")) for area in ASQ_SCORE_CONFIG.get(form_id, []))
            if not asq_like:
                continue
            expected = {f"{prefix}_{index}" for index in range(1, 7)}
            missing = sorted(expected - field_set)
            if missing:
                errors.append(f"{form_id}: ASQ group {prefix} is missing {', '.join(missing)}")

        for area in ASQ_SCORE_CONFIG.get(form_id, []):
            expected = {f"{area['fieldPrefix']}{index}" for index in range(1, 7)}
            missing = sorted(expected - field_set)
            if missing:
                errors.append(f"{form_id}: configured ASQ area {area['label']} missing {', '.join(missing)}")

    return errors


def assert_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def check_scoring() -> None:
    asq_yes = {f"asq_comm_{index}": "Yes" for index in range(1, 7)}
    scored_asq_yes = add_calculated_scores("2-months-visit", asq_yes)
    assert_equal("ASQ 2 month communication total", scored_asq_yes["asq_communication_total"], "60")
    assert_equal("ASQ 2 month communication zone", scored_asq_yes["asq_communication_zone"], "Above cutoff")

    asq_delayed = {f"asq_comm_{index}": "Not Yet" for index in range(1, 7)}
    scored_asq_delayed = add_calculated_scores("2-months-visit", asq_delayed)
    assert_equal("ASQ delayed label", scored_asq_delayed["asq_communication_zone"], "Delayed")

    epds_answers = {
        "epds_1": "As much as I always could",
        "epds_2": "As much as ever",
        "epds_3": "No, never",
        "epds_4": "No, not at all",
        "epds_5": "No, not at all",
        "epds_6": "No, I have been coping as well as ever",
        "epds_7": "No, not at all",
        "epds_8": "No, not at all",
        "epds_9": "No, never",
        "epds_10": "Never",
    }
    assert_equal("EPDS low score", add_calculated_scores("1-month-visit", epds_answers)["epds_total_score"], "0")

    act_answers = {
        "activity_limit": "None of the time",
        "shortness_breath": "Not at all",
        "night_symptoms": "Not at all",
        "rescue_inhaler": "Not at all",
        "control_rating": "Completely controlled",
    }
    scored_act = add_calculated_scores("act-mn-12-years-and-older", act_answers)
    assert_equal("ACT best score", scored_act["act_total_score"], "25")
    assert_equal("ACT status", scored_act["act_control_status"], "Likely controlled")

    asrs_answers = {
        "wrap_up": "Sometimes",
        "organization": "Often",
        "remembering": "Very often",
        "avoid_delay": "Often",
        "fidget": "Rarely",
        "driven": "Never",
    }
    scored_asrs = add_calculated_scores("adult-adhd-self-report-scale", asrs_answers)
    assert_equal("ASRS positive count", scored_asrs["asrs_part_a_positive_count"], "4")
    assert_equal("ASRS screen", scored_asrs["asrs_screen_result"], "Positive screen")


def main() -> int:
    templates = load_templates()
    errors = check_templates(templates)
    try:
        check_scoring()
    except AssertionError as exc:
        errors.append(str(exc))

    print(f"Checked {len(templates)} active form templates.")
    if errors:
        print("Deploy readiness failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Deploy readiness checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
