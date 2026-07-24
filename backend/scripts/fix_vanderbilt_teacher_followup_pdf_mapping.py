from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "vanderbilt-teacher-follow-up"


def field(field_id: str, label: str, field_type: str = "text", **extra: object) -> dict:
    output = {"id": field_id, "label": label, "type": field_type}
    output.update(extra)
    return output


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    template = next(item for item in templates if item["id"] == FORM_ID)

    template["description"] = "Vanderbilt teacher follow-up mapped from the AAP teacher-informant follow-up PDF."
    template["sections"][0] = {
        "title": "Child and Teacher Information",
        "fields": [
            field("patient_name", "Child's name", required=True),
            field("teacher_name", "Teacher's name", required=True),
            field("today_date", "Today's date", "date"),
            field("school", "School"),
            field("grade", "Grade"),
            field("teacher_fax", "Teacher's fax number"),
            field("class_period", "Time of day you work with child"),
            field("evaluation_period", "Weeks or months you have been able to evaluate the behaviors"),
            field(
                "medication_status",
                "This evaluation is based on a time when the child",
                "radio",
                options=["Was on medication", "Was not on medication", "Not sure"],
            ),
            field("baby_id", "Baby ID", owner="staff", staffOnly=True),
            field("administering_program_provider", "Administering program/provider", owner="staff", staffOnly=True),
        ],
    }

    labels = {
        "vanderbilt_teacher_followup_04": "4. Does not follow through on instructions and does not finish schoolwork (not because of oppositional behavior or lack of comprehension).",
        "vanderbilt_teacher_followup_17": "17. Has difficulty waiting in line.",
        "vanderbilt_teacher_followup_18": "18. Interrupts or intrudes in on others (e.g., butts into conversations or games or both).",
        "vanderbilt_teacher_followup_25": "25. Lies to obtain goods or favors or to avoid obligations (i.e., cons others).",
        "vanderbilt_teacher_followup_side_effect_03": "Change of appetite - explain below",
        "vanderbilt_teacher_followup_side_effect_05": "Irritability in the late morning, late afternoon, or evening - explain below",
        "vanderbilt_teacher_followup_side_effect_06": "Socially withdrawn - that is, decreased interaction with others",
        "vanderbilt_teacher_followup_side_effect_08": "Dull, tired, listless behavior",
        "vanderbilt_teacher_followup_side_effect_09": "Tremors or feeling shaky or both",
        "vanderbilt_teacher_followup_side_effect_10": "Repetitive movements, tics, jerking, twitching, or eye blinking - explain below",
        "vanderbilt_teacher_followup_side_effect_11": "Picking at skin or fingers, nail-biting, or lip or cheek chewing - explain below",
        "vanderbilt_teacher_followup_side_effect_12": "Sees or hears things that aren't there",
        "vanderbilt_teacher_followup_side_effect_notes": "Explanations and other comments",
        "vanderbilt_teacher_followup_performance_5_count": "Performance count scored 5 (questions 29-36)",
        "vanderbilt_teacher_followup_performance_4_count": "Performance count scored 4 (questions 29-36)",
    }

    updated = []
    for section in template.get("sections", []):
        for item in section.get("fields", []):
            if item.get("id") in labels:
                item["label"] = labels[item["id"]]
                updated.append(item["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Remapped {FORM_ID} header and updated {len(updated)} labels.")


if __name__ == "__main__":
    main()
