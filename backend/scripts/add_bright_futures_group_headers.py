import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_FILE = ROOT / "backend" / "data" / "form-templates.json"


SCHOOL_AGE_FORM_IDS = {
    "6-year-visit",
    "7-year-visit",
    "8-year-visit",
    "9-year-visit",
    "10-year-visit",
}

ADOLESCENT_FORM_IDS = {
    "11-year-visit",
    "12-year-visit",
    "13-14-year-visit",
    "15-17-year-visit",
    "18-21-year-visit",
}


def clear_group(field):
    field.pop("groupTitle", None)
    field.pop("groupDescription", None)
    field.pop("groupVariant", None)


def set_group(field, title, description=None, variant=None):
    field["groupTitle"] = title
    if description:
        field["groupDescription"] = description
    if variant:
        field["groupVariant"] = variant


def group_school_age_field(field):
    field_id = field.get("id", "")
    clear_group(field)

    if field_id == "bf_family_new_medical_problems":
        set_group(field, "Questions About Your Child")
    elif field_id.startswith("bf_vision_") or field_id == "bf_squinting":
        set_group(field, "Vision", None, "compact")
    elif field_id.startswith("bf_hearing_") or field_id in {"bf_speech_concerns", "bf_conversation_following"}:
        set_group(field, "Hearing", None, "compact")
    elif field_id.startswith("bf_lead_"):
        set_group(field, "Lead", None, "compact")
    elif field_id.startswith("bf_tb_") or field_id == "bf_hiv_infected":
        set_group(field, "Tuberculosis", None, "compact")
    elif field_id.startswith("bf_dyslipidemia_"):
        set_group(field, "Dyslipidemia", None, "compact")
    elif field_id.startswith("bf_anemia_"):
        set_group(field, "Anemia", None, "compact")
    elif field_id.startswith("bf_oral_"):
        set_group(field, "Oral Health", None, "compact")
    elif field_id in {
        "bf_development_learning_behavior_concerns",
        "bf_development_learning_behavior_describe",
        "bf_growing_developing_child_tasks",
    }:
        set_group(field, "Your Growing and Developing Child")


def group_adolescent_parent_field(field):
    field_id = field.get("id", "")
    clear_group(field)

    if field_id.endswith("_parent_concerns"):
        set_group(field, "What would you like to talk about today?")
    elif "_parent_vision_" in field_id:
        set_group(field, "Vision", None, "compact")
    elif "_parent_hearing_" in field_id:
        set_group(field, "Hearing", None, "compact")
    elif "_parent_tb_" in field_id or field_id.endswith("_parent_hiv"):
        set_group(field, "Tuberculosis", None, "compact")
    elif "_parent_dyslipidemia_" in field_id:
        set_group(field, "Dyslipidemia", None, "compact")
    elif "_parent_anemia_" in field_id:
        set_group(field, "Anemia", None, "compact")
    elif "_parent_female_" in field_id:
        set_group(field, "For Females Only - Anemia", None, "warning")
    elif field_id.endswith("_parent_growing_developing"):
        set_group(field, "Your Growing and Developing Child")


def group_adolescent_patient_field(field):
    field_id = field.get("id", "")
    clear_group(field)

    if field_id.endswith("_patient_concerns"):
        set_group(field, "What would you like to talk about today?")
    elif "_topics_" in field_id:
        set_group(field, "Topics you would like to discuss most today")
    elif "_patient_vision_" in field_id:
        set_group(field, "Vision", None, "compact")
    elif "_patient_hearing_" in field_id:
        set_group(field, "Hearing", None, "compact")
    elif "_patient_tb_" in field_id or field_id.endswith("_patient_hiv"):
        set_group(field, "Tuberculosis", None, "compact")
    elif "_patient_dyslipidemia_" in field_id or field_id.endswith("_patient_smokes"):
        set_group(field, "Dyslipidemia", None, "compact")
    elif "_patient_alcohol_" in field_id or "_patient_drug_" in field_id or "_patient_injectable_drugs" in field_id:
        set_group(field, "Alcohol or Drug Use", None, "compact")
    elif field_id.endswith("_patient_sex_ever"):
        set_group(field, "STIs", None, "compact")
    elif "_patient_anemia_" in field_id:
        set_group(field, "Anemia", None, "compact")
    elif "_patient_female_menstrual_" in field_id or "_patient_female_period_" in field_id:
        set_group(field, "For Females Only - Anemia", None, "warning")
    elif "_patient_female_" in field_id:
        set_group(field, "For Females Only - STIs", None, "warning")
    elif "_patient_cervical_" in field_id:
        set_group(field, "For Females Only - Cervical Dysplasia", None, "warning")
    elif "_patient_pregnancy_" in field_id:
        set_group(field, "For Females Only - Pregnancy", None, "warning")
    elif "_patient_male_" in field_id:
        set_group(field, "For Males Only - STIs", None, "warning")
    elif field_id.endswith("_patient_growing_developing"):
        set_group(field, "Growing and Developing")


def update_form(form):
    form_id = form.get("id")
    changed = False
    for section in form.get("sections", []):
        title = section.get("title", "")
        if "Bright Futures" not in title:
            continue
        for field in section.get("fields", []):
            before = json.dumps({key: field.get(key) for key in ("groupTitle", "groupDescription", "groupVariant")}, sort_keys=True)
            if form_id in SCHOOL_AGE_FORM_IDS:
                group_school_age_field(field)
            elif "Older Child / Early Adolescent Visits (Parent)" in title:
                group_adolescent_parent_field(field)
            elif form_id in ADOLESCENT_FORM_IDS:
                group_adolescent_patient_field(field)
            after = json.dumps({key: field.get(key) for key in ("groupTitle", "groupDescription", "groupVariant")}, sort_keys=True)
            changed = changed or before != after
    return changed


def main():
    templates = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8-sig"))
    changed = [form.get("id") for form in templates if update_form(form)]
    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
    print("Added Bright Futures group headers:")
    for form_id in changed:
        print(f"- {form_id}")


if __name__ == "__main__":
    main()
