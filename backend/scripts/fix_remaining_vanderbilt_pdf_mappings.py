from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
MEDICATION_OPTIONS = ["Was on medication", "Was not on medication", "Not sure"]
YES_NO = ["No", "Yes"]
TIC_OPTIONS = [
    "No tics present",
    "Yes, they occur nearly every day but go unnoticed by most people",
    "Yes, noticeable tics occur nearly every day",
]


def field(field_id: str, label: str, field_type: str = "text", **extra: object) -> dict:
    output = {"id": field_id, "label": label, "type": field_type}
    output.update(extra)
    return output


def get_form(templates: list[dict], form_id: str) -> dict:
    return next(item for item in templates if item["id"] == form_id)


def replace_section(form: dict, title: str, section: dict) -> None:
    for index, existing in enumerate(form["sections"]):
        if existing["title"] == title:
            form["sections"][index] = section
            return
    raise ValueError(f"Section {title!r} not found in {form['id']}")


def replace_first_existing_section(form: dict, titles: set[str], section: dict) -> None:
    for index, existing in enumerate(form["sections"]):
        if existing["title"] in titles:
            form["sections"][index] = section
            return
    raise ValueError(f"None of sections {sorted(titles)!r} found in {form['id']}")


def remove_section(form: dict, title: str) -> None:
    form["sections"] = [section for section in form["sections"] if section.get("title") != title]


def fix_parent_initial(form: dict) -> None:
    replace_section(
        form,
        "Child and Parent Information",
        {
            "title": "Child and Parent Information",
            "fields": [
                field("patient_name", "Child's name", required=True),
                field("parent_name", "Parent's name"),
                field("today_date", "Date", "date"),
                field("date_of_birth", "DOB", "date"),
                field("age", "Age", "number"),
                field("medication_status", "This evaluation is based on a time when your child", "radio", options=MEDICATION_OPTIONS),
                field("baby_id", "Baby ID", owner="staff", staffOnly=True),
                field("administering_program_provider", "Administering program/provider", owner="staff", staffOnly=True),
            ],
        },
    )
    remove_section(form, "Tic Behaviors")
    remove_section(form, "Previous Diagnosis and Treatment")
    insert_index = next(
        (index for index, section in enumerate(form["sections"]) if section["title"] == "Scoring Summary"),
        len(form["sections"]),
    )
    form["sections"][insert_index:insert_index] = [
        {
            "title": "Tic Behaviors",
            "fields": [
                field("vanderbilt_parent_behavior_first_noticed_age", "How old was your child when you first noticed the behaviors?"),
                field("vanderbilt_parent_tics_motor", "Motor tics", "radio", options=TIC_OPTIONS),
                field("vanderbilt_parent_tics_vocal", "Phonic (vocal) tics", "radio", options=TIC_OPTIONS),
                field("vanderbilt_parent_tics_interfere", "If yes to 1 or 2, do these tics interfere with your child's activities?", "radio", options=YES_NO),
            ],
        },
        {
            "title": "Previous Diagnosis and Treatment",
            "fields": [
                field("vanderbilt_parent_previous_adhd", "Has your child been diagnosed as having ADHD or ADD?", "radio", options=YES_NO),
                field("vanderbilt_parent_adhd_medication", "Is he or she on medication for ADHD or ADD?", "radio", options=YES_NO),
                field("vanderbilt_parent_previous_tic_disorder", "Has your child been diagnosed as having a tic disorder or Tourette syndrome?", "radio", options=YES_NO),
                field("vanderbilt_parent_tic_medication", "Is he or she on medication for a tic disorder or Tourette disorder?", "radio", options=YES_NO),
            ],
        },
    ]


def fix_teacher_initial(form: dict) -> None:
    replace_section(
        form,
        "Student and Teacher Information",
        {
            "title": "Student and Teacher Information",
            "fields": [
                field("patient_name", "Child's name", required=True),
                field("teacher_name", "Teacher's name", required=True),
                field("today_date", "Today's date", "date"),
                field("school", "School"),
                field("grade", "Grade"),
                field("teacher_fax", "Teacher's fax number"),
                field("class_period", "Time of day you work with child"),
                field("evaluation_period", "Weeks or months you have been able to evaluate the behaviors"),
                field("medication_status", "This evaluation is based on a time when the child", "radio", options=MEDICATION_OPTIONS),
                field("baby_id", "Baby ID", owner="staff", staffOnly=True),
                field("administering_program_provider", "Administering program/provider", owner="staff", staffOnly=True),
            ],
        },
    )
    replace_first_existing_section(
        form,
        {"Tic Behaviors", "Tic Behaviors and Previous Diagnosis"},
        {
            "title": "Tic Behaviors and Previous Diagnosis",
            "fields": [
                field("vanderbilt_teacher_tics_motor", "Motor tics", "radio", options=["No tics present", "Yes, noticeable tics occur nearly every day"]),
                field("vanderbilt_teacher_tics_vocal", "Phonic (vocal) tics", "radio", options=["No tics present", "Yes, noticeable tics occur nearly every day"]),
                field("vanderbilt_teacher_previous_adhd", "Has the child been diagnosed as having ADHD or ADD?", "radio", options=YES_NO),
                field("vanderbilt_teacher_adhd_medication", "Is he or she on medication for ADHD or ADD?", "radio", options=YES_NO),
                field("vanderbilt_teacher_previous_tic_disorder", "Has the child been diagnosed as having a tic disorder or Tourette syndrome?", "radio", options=YES_NO),
                field("vanderbilt_teacher_tic_medication", "Is he or she on medication for a tic disorder or Tourette disorder?", "radio", options=YES_NO),
            ],
        },
    )


def fix_parent_followup(form: dict) -> None:
    replace_first_existing_section(
        form,
        {"Child and Rater Information", "Child and Parent Information"},
        {
            "title": "Child and Parent Information",
            "fields": [
                field("patient_name", "Child's name", required=True),
                field("parent_name", "Parent's name"),
                field("today_date", "Date", "date"),
                field("date_of_birth", "DOB", "date"),
                field("age", "Age", "number"),
                field("medication_status", "This evaluation is based on a time when your child", "radio", options=MEDICATION_OPTIONS),
                field("baby_id", "Baby ID", owner="staff", staffOnly=True),
                field("administering_program_provider", "Administering program/provider", owner="staff", staffOnly=True),
            ],
        },
    )
    labels = {
        "vanderbilt_parent_followup_01": "1. Does not pay attention to details or makes mistakes that seem careless with, for example, homework.",
        "vanderbilt_parent_followup_04": "4. Does not follow through on instructions and does not finish activities (not because of refusal or lack of comprehension).",
        "vanderbilt_parent_followup_18": "18. Interrupts or intrudes into others' conversations or activities or both.",
        "vanderbilt_parent_followup_25": "25. Blames others for his or her mistakes or behaviors.",
        "vanderbilt_parent_followup_side_effect_03": "Change of appetite - explain on the next page",
        "vanderbilt_parent_followup_side_effect_05": "Irritability in the late morning, late afternoon, or evening - explain on the next page",
        "vanderbilt_parent_followup_side_effect_06": "Socially withdrawn - that is, decreased interaction with others",
        "vanderbilt_parent_followup_side_effect_08": "Dull, tired, listless behavior",
        "vanderbilt_parent_followup_side_effect_09": "Tremors or feeling shaky or both",
        "vanderbilt_parent_followup_side_effect_10": "Repetitive movements, tics, jerking, twitching, or eye blinking - explain on the next page",
        "vanderbilt_parent_followup_side_effect_11": "Picking at skin or fingers, nail-biting, lip or cheek chewing - explain on the next page",
        "vanderbilt_parent_followup_side_effect_12": "Sees or hears things that aren't there",
        "vanderbilt_parent_followup_side_effect_notes": "Explanations and other comments",
        "vanderbilt_parent_followup_performance_4_count": "Performance count scored 4 (questions 27-34)",
        "vanderbilt_parent_followup_performance_5_count": "Performance count scored 5 (questions 27-34)",
    }
    for section in form.get("sections", []):
        for item in section.get("fields", []):
            if item.get("id") in labels:
                item["label"] = labels[item["id"]]


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    fix_parent_initial(get_form(templates, "vanderbilt-parent"))
    fix_teacher_initial(get_form(templates, "vanderbilt-teacher"))
    fix_parent_followup(get_form(templates, "vanderbilt-parent-follow-up"))

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Fixed remaining Vanderbilt PDF mappings.")


if __name__ == "__main__":
    main()
