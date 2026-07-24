import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_FILE = ROOT / "backend" / "data" / "form-templates.json"


def clear_group(field):
    field.pop("groupTitle", None)
    field.pop("groupDescription", None)
    field.pop("groupVariant", None)


def group(field, title, description=None, variant=None):
    field["groupTitle"] = title
    if description:
        field["groupDescription"] = description
    if variant:
        field["groupVariant"] = variant


def group_patient_visit(field):
    fid = field.get("id", "")
    label = field.get("label", "").lower()
    if fid in {"patient_name", "date_of_birth", "patient_first_name", "patient_last_name", "age", "patient_email", "account_number"}:
        group(field, "Patient")
    elif any(key in fid for key in ["completed_by", "relationship", "caregiver", "parent", "guardian", "proxy"]):
        group(field, "Caregiver / Proxy")
    elif any(key in fid for key in ["phone", "email", "address", "city", "state", "zip"]):
        group(field, "Contact")
    elif any(key in fid for key in ["visit", "clinic", "provider", "grade", "school", "teacher", "class", "evaluation", "medication", "followup"]):
        group(field, "Visit / Context")
    elif "signature" in fid or "date" in label:
        group(field, "Signature / Date")


def group_portal_authorization(field):
    fid = field.get("id", "")
    if "signature" in fid or fid in {"date", "witness"}:
        group(field, "Signature")
    elif any(key in fid for key in ["processed", "staff", "office"]):
        group(field, "Staff Processing", variant="warning")
    else:
        group(field, "Authorization")


def group_blood_lead(field):
    fid = field.get("id", "")
    if any(key in fid for key in ["last_name", "first_name", "middle", "birth", "gender", "race", "ethnicity", "guardian"]):
        group(field, "Patient")
    elif any(key in fid for key in ["address", "street", "city", "state", "zip", "county", "phone"]):
        group(field, "Contact")
    elif any(key in fid for key in ["test", "result", "sample", "lab"]):
        group(field, "Specimen / Lab")
    elif any(key in fid for key in ["physician", "provider"]):
        group(field, "Clinician")
    elif "notes" in fid:
        group(field, "Staff Notes", variant="warning")


def group_newborn_bright_futures(field):
    fid = field.get("id", "")
    if fid == "visit_concerns":
        group(field, "What would you like to talk about today?")
    elif fid.startswith("topics_"):
        group(field, "Topics You Would Like to Discuss Most Today")
    elif fid == "baby_vision_concerns":
        group(field, "Vision", None, "compact")
    elif fid in {"baby_growth_concerns", "baby_growth_concerns_description", "baby_tasks"}:
        group(field, "Your Growing and Developing Baby")
    elif fid.startswith("phq2_"):
        if fid == "phq2_total_score":
            group(field, "Calculated Score", None, "warning")
        else:
            group(field, "Over the past 2 weeks")
    elif any(key in fid for key in ["special_health", "tobacco", "family_changes", "family_major_changes"]):
        group(field, "Questions About Your Baby")
    else:
        clear_group(field)


def group_baby_questions(field):
    fid = field.get("id", "")
    if fid == "vision_concerns":
        group(field, "Vision")
    elif fid.startswith("tb_"):
        group(field, "Tuberculosis")


def group_sdoh(field):
    fid = field.get("id", "")
    if fid.startswith("sdoh_food_"):
        group(field, "Food")
    elif fid in {"sdoh_has_housing", "sdoh_losing_housing", "sdoh_unable_utilities", "sdoh_housing", "sdoh_housing_worry", "sdoh_housing_quality"}:
        group(field, "Housing / Utilities")
    elif fid in {"sdoh_transportation_barrier", "sdoh_transportation"}:
        group(field, "Transportation")
    elif fid in {"sdoh_safe_where_live", "sdoh_physically_hurt", "sdoh_emotionally_abused", "sdoh_safety", "sdoh_hurt", "sdoh_threatened"}:
        group(field, "Safety")
    elif fid in {"sdoh_urgent_needs", "sdoh_additional_information", "sdoh_help_wanted"}:
        group(field, "Help Now")


def group_mnvfc(field):
    fid = field.get("id", "")
    if fid in {"mnvfc_screening_date", "mnvfc_subsequent_visit_dates", "mnvfc_birth_date", "mnvfc_patient", "mnvfc_patient_name", "mnvfc_parent_guardian", "mnvfc_provider"}:
        group(field, "Patient and Visit")
    elif fid == "mnvfc_eligibility":
        group(field, "MnVFC Eligibility Criteria")
    elif fid == "mnvfc_notes":
        group(field, "Staff Review", None, "warning")


def group_asq(field):
    fid = field.get("id", "")
    if "_overall_" in fid:
        group(field, "Overall Questions")
    elif "_summary_" in fid and fid.endswith("_score"):
        group(field, "Calculated Total Scores")
    elif fid.endswith("_zone"):
        group(field, "Score Zones")
    elif any(key in fid for key in ["follow_up", "rescreen", "referral", "optional_item"]):
        group(field, "Follow-Up Plan")


def group_psc17(field):
    fid = field.get("id", "")
    if fid in {"psc17_caregiver_name", "psc17_date", "psc17_child_name"}:
        group(field, "Respondent Information")
    elif re.search(r"psc17_\d+_", fid):
        group(field, "Symptoms")
    elif fid == "psc17_staff_notes":
        group(field, "Staff Notes", variant="warning")
    elif fid.startswith("psc17_"):
        group(field, "Office Scoring")


def group_phq(field):
    fid = field.get("id", "")
    if fid in {"phqa_name", "phqa_clinician", "phqa_date"}:
        group(field, "Respondent Information")
    elif re.search(r"phqa_\d+_", fid) or re.search(r"phq9_\d+", fid):
        group(field, "Symptoms")
    elif fid.endswith("_total_score") or fid == "phq9_total_score":
        group(field, "Calculated Score")
    elif "suicide" in fid or "self_harm" in fid:
        group(field, "Safety Follow-Up", variant="warning")
    elif "difficulty" in fid or "depressed_past_year" in fid:
        group(field, "Functional Impact")
    elif fid.endswith("_staff_notes"):
        group(field, "Staff Notes", variant="warning")


def group_crafft(field):
    fid = field.get("id", "")
    if fid.startswith("crafft_a_"):
        group(field, "Part A - Substance Use")
    elif fid.startswith("crafft_b_"):
        group(field, "Part B - CRAFFT Questions")
    elif fid.endswith("_yes_count"):
        group(field, "Calculated Score")
    elif fid == "crafft_staff_notes":
        group(field, "Staff Notes", variant="warning")


def group_gad7(field):
    fid = field.get("id", "")
    if re.search(r"gad7_\d+$", fid):
        group(field, "Anxiety Symptoms")
    elif fid == "gad7_total_score":
        group(field, "Calculated Score")
    elif fid == "gad7_staff_notes":
        group(field, "Staff Notes", variant="warning")


VANDERBILT_PARENT_RANGES = [
    (1, 9, "Inattention"),
    (10, 18, "Hyperactivity / Impulsivity"),
    (19, 26, "Oppositional Defiant Symptoms"),
    (27, 41, "Conduct Disorder Symptoms"),
    (42, 48, "Anxiety / Depression Symptoms"),
]

VANDERBILT_TEACHER_RANGES = [
    (1, 9, "Inattention"),
    (10, 18, "Hyperactivity / Impulsivity"),
    (19, 28, "Oppositional / Conduct Symptoms"),
    (29, 35, "Anxiety / Depression Symptoms"),
]


def item_number(field_id):
    match = re.search(r"_(\d{2})$", field_id)
    return int(match.group(1)) if match else None


def group_vanderbilt(field, section_title):
    fid = field.get("id", "")
    n = item_number(fid)
    if n and ("Symptoms" in section_title or "Current Symptoms" in section_title):
        ranges = VANDERBILT_TEACHER_RANGES if "_teacher" in fid else VANDERBILT_PARENT_RANGES
        for start, end, title in ranges:
            if start <= n <= end:
                group(field, title)
                return
    if any(key in fid for key in ["inattention", "hyperactive", "oppositional", "conduct", "anxiety_depression"]):
        group(field, "Symptom Counts")
    elif any(key in fid for key in ["performance_4", "performance_5", "impairment"]):
        group(field, "Performance Impairment")
    elif "_performance_" in fid:
        if any(word in field.get("label", "").lower() for word in ["reading", "writing", "mathematics", "school"]):
            group(field, "Academic Performance")
        else:
            group(field, "Social / Classroom Performance")
    elif "side_effect" in fid:
        group(field, "Side Effects")
    elif fid.endswith("_staff_notes"):
        group(field, "Staff Notes", variant="warning")


SCARED_GROUPS = {
    "total": "Total Anxiety",
    "panic_somatic": "Panic / Somatic",
    "generalized_anxiety": "Generalized Anxiety",
    "separation_anxiety": "Separation Anxiety",
    "social_anxiety": "Social Anxiety",
    "school_avoidance": "School Avoidance",
}


def group_scared(field):
    fid = field.get("id", "")
    if re.search(r"_(scared)_\d{2}$", fid):
        group(field, "SCARED Questionnaire Items")
        return
    if fid.startswith("child_scared_") and fid.endswith("_cutoff_met"):
        group(field, "Child Cutoffs")
        return
    if fid.startswith("child_scared_") and fid.endswith("_score"):
        group(field, "Child Scores")
        return
    if fid.startswith("parent_scared_") and fid.endswith("_cutoff_met"):
        group(field, "Parent Cutoffs")
        return
    if fid.startswith("parent_scared_") and fid.endswith("_score"):
        group(field, "Parent Scores")
        return
    for key, title in SCARED_GROUPS.items():
        if key in fid:
            prefix = "Child" if fid.startswith("child_") else "Parent" if fid.startswith("parent_") else ""
            group(field, f"{prefix} {title}".strip())
            return
    if fid == "scared_staff_notes":
        group(field, "Staff Notes", variant="warning")


def group_common_symptom_checklist(field, section_title):
    fid = field.get("id", "")
    title = section_title.lower()
    if "epds" in title:
        if fid in {"epds_name", "epds_address", "epds_parent_dob", "epds_baby_dob", "epds_caregiver_date_of_birth", "epds_baby_date_of_birth", "epds_phone"}:
            group(field, "Respondent Information")
        elif fid.startswith("epds_") and fid.endswith("_score"):
            group(field, "Calculated Score")
        elif fid in {"epds_reviewed_by", "epds_administered_reviewed_by", "epds_review_date"}:
            group(field, "Administered / Reviewed By", variant="warning")
        elif fid.startswith("epds_"):
            group(field, "In the past 7 days")
    elif "bpsc" in title or "ppsc" in title:
        if any(key in fid for key in ["caregiver", "child_name", "today_date", "date"]):
            group(field, "Respondent Information")
        elif "irritability" in fid:
            group(field, "Irritability")
        elif "inflexibility" in fid:
            group(field, "Inflexibility")
        elif "routine" in fid:
            group(field, "Difficulty With Routines")
        elif fid.endswith("_score"):
            group(field, "Calculated Scores")
        elif fid.endswith("_notes"):
            group(field, "Staff Notes", variant="warning")
        else:
            group(field, "Symptom Questions")
    elif "m-chat" in title:
        if fid.endswith("_score") or fid.endswith("_risk"):
            group(field, "Calculated Score")
        else:
            group(field, "M-CHAT Questions")
    elif "peds response" in title:
        group(field, "Developmental Concerns")


def group_asrs(field, section_title):
    fid = field.get("id", "")
    if "Part A" in section_title:
        group(field, "Part A")
    elif "Part B" in section_title:
        group(field, "Part B")
    elif "positive_count" in fid or "screen_result" in fid:
        group(field, "Calculated Screening")
    elif "staff" in fid:
        group(field, "Staff Notes", variant="warning")


def group_acute_concussion(field, section_title):
    fid = field.get("id", "")
    if section_title == "Patient and Injury Information":
        if any(key in fid for key in ["patient", "birth", "age"]):
            group(field, "Patient")
        elif any(key in fid for key in ["evaluation", "injury", "reporter", "description"]):
            group(field, "Injury")
        else:
            group(field, "Mechanism / Setting")
    elif section_title == "Initial Signs":
        if "amnesia" in fid:
            group(field, "Amnesia")
        elif "loss_consciousness" in fid:
            group(field, "Loss of Consciousness")
        else:
            group(field, "Early Signs")
    elif "Symptoms" in section_title:
        group(field, section_title.replace(" Symptoms", ""))
    elif section_title == "Risk Factors and Red Flags":
        if any(key in fid for key in ["concussion", "duration"]):
            group(field, "Concussion History")
        elif any(key in fid for key in ["headache", "migraine", "developmental", "psychiatric", "medical"]):
            group(field, "Risk Factors")
        else:
            group(field, "Red Flags")
    elif section_title == "Diagnosis and Follow-Up":
        if "notes" in fid:
            group(field, "Staff Notes", variant="warning")
        else:
            group(field, "Plan")


def group_wart_consent(field, section_title):
    fid = field.get("id", "")
    if section_title == "Treatment Acknowledgements":
        if any(key in fid for key in ["diagnosis", "treatment", "guarantee"]):
            group(field, "Treatment")
        elif any(key in fid for key in ["cost", "insurance", "office_visit"]):
            group(field, "Billing")
        else:
            group(field, "Acknowledgements")
    elif section_title == "Signature":
        group(field, "Signature")


def group_asthma(field, section_title):
    fid = field.get("id", "")
    if "total" in fid or "control_status" in fid:
        group(field, "Calculated Score")
    elif "Utilization" in section_title:
        group(field, "Utilization")
    elif "Child Questions" in section_title:
        group(field, "Child Questions")
    elif "Caregiver Questions" in section_title:
        if "notes" in fid:
            group(field, "Staff Notes", variant="warning")
        else:
            group(field, "Caregiver Questions")


def update_section(section):
    title = section.get("title", "")
    changed = False
    for field in section.get("fields", []):
        before = json.dumps({k: field.get(k) for k in ("groupTitle", "groupDescription", "groupVariant")}, sort_keys=True)
        # Preserve Bright Futures groups from the previous migration.
        if "Bright Futures" not in title:
            clear_group(field)
        if title == "Social Determinants of Health Assessment":
            group_sdoh(field)
        elif "Patient and Visit Information" in title:
            pass
        elif title in {"Patient Information", "Child and Parent Information", "Child and Teacher Information", "Student and Teacher Information", "Child and Rater Information", "Patient", "Child"}:
            group_patient_visit(field)
        elif "Proxy Information" in title:
            group_patient_visit(field)
        elif "Authorization and Acknowledgement" in title:
            group_portal_authorization(field)
        elif "Blood Lead" in title:
            group_blood_lead(field)
        elif title == "Bright Futures 2 to 5 Day Visit":
            group_newborn_bright_futures(field)
        elif title == "Questions About Your Baby":
            group_baby_questions(field)
        elif title == "MnVFC Eligibility Screening":
            group_mnvfc(field)
        elif "ASQ-3" in title and ("Overall Questions" in title or "Score Summary" in title):
            group_asq(field)
        elif title == "Pediatric Symptom Checklist-17 (PSC-17)":
            group_psc17(field)
        elif "PHQ" in title:
            group_phq(field)
        elif title == "CRAFFT Screening Questions":
            group_crafft(field)
        elif title == "GAD-7":
            group_gad7(field)
        elif "Vanderbilt" in title or any(str(field.get("id", "")).startswith(prefix) for prefix in ["vanderbilt_parent", "vanderbilt_teacher"]):
            group_vanderbilt(field, title)
        elif "SCARED" in title:
            group_scared(field)
        elif "ADHD Self-Report" in title or "Part A" in title or "Part B" in title or "ASRS" in title:
            group_asrs(field, title)
        elif any(key in title for key in ["Patient and Injury Information", "Initial Signs", "Physical Symptoms", "Cognitive Symptoms", "Emotional Symptoms", "Sleep Symptoms", "Symptom Summary", "Risk Factors and Red Flags", "Diagnosis and Follow-Up"]):
            group_acute_concussion(field, title)
        elif "Wart" in title or title in {"Treatment Acknowledgements", "Signature"}:
            group_wart_consent(field, title)
        elif "Asthma" in title or title in {"Past 4 Weeks", "Utilization", "Child Questions", "Caregiver Questions"}:
            group_asthma(field, title)
        else:
            group_common_symptom_checklist(field, title)
        after = json.dumps({k: field.get(k) for k in ("groupTitle", "groupDescription", "groupVariant")}, sort_keys=True)
        changed = changed or before != after
    return changed


def main():
    templates = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8-sig"))
    changed = []
    for form in templates:
        form_changed = False
        for section in form.get("sections", []):
            form_changed = update_section(section) or form_changed
        if form_changed:
            changed.append(form.get("id"))
    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
    print("Added shared section group headers:")
    for form_id in changed:
        print(f"- {form_id}")


if __name__ == "__main__":
    main()
