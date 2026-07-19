import json
from copy import deepcopy
from pathlib import Path


TEMPLATE_PATH = Path("backend/data/form-templates.json")

ASQ_OPTIONS = ["Yes", "Sometimes", "Not Yet"]
YES_NO = ["Yes", "No"]
ZONE_OPTIONS = ["On schedule", "Close to cutoff", "Delayed"]

COMMON_PATIENT_FIELDS = [
    {"id": "patient_name", "label": "Child full name", "type": "text", "required": True},
    {"id": "date_of_birth", "label": "Child's date of birth", "type": "date", "required": True},
    {"id": "completed_by", "label": "Completed by", "type": "text", "required": True},
    {"id": "relationship", "label": "Relationship to child", "type": "select", "required": True, "options": ["Mother", "Father", "Parent", "Guardian", "Grandparent", "Other caregiver"]},
    {"id": "phone", "label": "Phone number", "type": "tel"},
    {"id": "caregiver_date_of_birth", "label": "Caregiver's date of birth", "type": "date"},
    {"id": "address", "label": "Address", "type": "textarea"},
    {"id": "visit_date", "label": "Visit date", "type": "date"},
]

AREA_LABELS = {
    "communication": "Communication",
    "gross": "Gross Motor",
    "fine": "Fine Motor",
    "problem": "Problem Solving",
    "social": "Personal-Social",
}
SUMMARY_KEYS = {
    "communication": "communication",
    "gross": "gross_motor",
    "fine": "fine_motor",
    "problem": "problem_solving",
    "social": "personal_social",
}
TOTAL_KEYS = {
    "communication": "communication",
    "gross": "gross",
    "fine": "fine",
    "problem": "problem",
    "social": "social",
}

ASQ_OVERALL_FIELDS = [
    ("hears", "Do you think your child hears well?"),
    ("talks", "Do you think your child talks like other children this age?"),
    ("understand_speech", "Can you understand most of what your child says?"),
    ("walks_runs_climbs", "Do you think your child walks, runs, and climbs like other children this age?"),
    ("family_hearing_history", "Does either parent have a family history of childhood deafness or hearing impairment?"),
    ("vision_concerns", "Do you have any concerns about your child's vision?"),
    ("recent_medical_problems", "Has your child had any medical problems in the last several months?"),
    ("behavior_concerns", "Do you have any concerns about your child's behavior?"),
    ("other_concerns", "Does anything else about your child concern you?"),
]

ASQ_QUESTIONS = {
    "42": {
        "communication": [
            "Without pointing or gestures, can your child follow two location directions such as put the book on the table and the shoe under the chair?",
            "When looking at a picture book, does your child tell you what action is happening in the picture?",
            "Does your child consistently move a zipper up and down when you ask using the words up and down?",
            "When you ask, what is your name, does your child say both first and last names?",
            "Without pointing or repeating directions, does your child follow three unrelated directions?",
            "Does your child use all of the words in a sentence, such as a, the, am, is, or are?",
        ],
        "gross": [
            "Does your child walk up stairs using only one foot on each stair?",
            "Does your child stand on one foot for about 1 second without holding onto anything?",
            "While standing, does your child throw a ball overhand by raising the arm to shoulder height and throwing forward?",
            "Does your child jump forward at least 6 inches with both feet leaving the ground at the same time?",
            "Does your child catch a large ball with both hands?",
            "Does your child climb playground ladder rungs and slide down without help?",
        ],
        "fine": [
            "After watching you draw a single circle, does your child copy you by drawing a circle?",
            "After watching you draw a horizontal line, does your child copy you by drawing a single horizontal line?",
            "Does your child try to cut paper with child-safe scissors?",
            "When drawing, does your child hold a pencil, crayon, or pen between fingers and thumb like an adult?",
            "Does your child put together a five- to seven-piece interlocking puzzle?",
            "Using a shape to look at, does your child copy the shape without tracing?",
        ],
        "problem": [
            "When you point to a figure and ask what it is, does your child say a word that means a person?",
            "Does your child repeat three numbers in the same order after you say them?",
            "Does your child copy a bridge made with blocks, boxes, or cans?",
            "Does your child repeat a different series of three numbers in the same order?",
            "When asked which circle is the smallest, does your child point to the smallest circle?",
            "Does your child dress up and play-act, pretending to be someone or something else?",
        ],
        "social": [
            "When looking in a mirror and asked who is in the mirror, does your child say me or their own name?",
            "Does your child put on a coat, jacket, or shirt by themself?",
            "When asked whether they are a girl or a boy, does your child answer correctly?",
            "Does your child take turns by waiting while another child or adult takes a turn?",
            "Does your child serve themself by moving food from one container to another using utensils?",
            "Does your child wash hands with soap and water and dry with a towel without help?",
        ],
    },
    "54": {
        "communication": [
            "Does your child tell you at least two things about common objects?",
            "Does your child use all of the words in a sentence, such as a, the, am, is, or are?",
            "Does your child use word endings such as -s, -ed, and -ing?",
            "Without pointing or repeating directions, does your child follow three unrelated directions?",
            "Does your child use four- and five-word sentences?",
            "When talking about something that already happened, does your child use words ending in -ed?",
        ],
        "gross": [
            "Does your child hop up and down on either foot at least one time without losing balance?",
            "While standing, does your child throw a ball overhand toward a person at least 6 feet away?",
            "Does your child jump forward 20 inches from a standing position with feet together?",
            "Does your child catch a large ball with both hands?",
            "Without holding onto anything, does your child stand on one foot for at least 5 seconds?",
            "Does your child walk on tiptoes for about 15 feet?",
        ],
        "fine": [
            "Using shapes to look at, does your child copy at least three shapes without tracing?",
            "Does your child unbutton one or more buttons?",
            "Does your child color mostly within the lines in a coloring book or a 2-inch circle?",
            "Does your child trace on a line without going off the line more than two times?",
            "Does your child draw a person with at least four body parts?",
            "Using child-safe scissors, does your child cut paper in half on a more or less straight line?",
        ],
        "problem": [
            "When shown objects and asked what color this is, does your child name five different colors?",
            "Does your child dress up and play-act, pretending to be someone or something else?",
            "Can your child count five objects in order without help?",
            "When asked which circle is smallest, does your child point to the smallest circle?",
            "Does your child count up to 15 without making mistakes?",
            "Does your child know the names of numbers?",
        ],
        "social": [
            "Does your child wash hands with soap and water and dry off with a towel without help?",
            "Does your child tell you the names of two or more playmates, excluding siblings?",
            "Does your child brush teeth with toothpaste without help?",
            "Does your child serve themself by moving food from one container to another using utensils?",
            "Does your child tell you at least four personal facts such as first name, age, city, last name, gender, or phone number?",
            "Does your child dress and undress themself, including buttons and front zippers?",
        ],
    },
}


def field(field_id, label, field_type="text", **extra):
    data = {"id": field_id, "label": label, "type": field_type}
    data.update(extra)
    return data


def radio(field_id, label, options=None, **extra):
    return field(field_id, label, "radio", options=options or YES_NO, **extra)


def clone_section(forms, form_id, title):
    source = next(form for form in forms if form["id"] == form_id)
    return deepcopy(next(section for section in source["sections"] if section["title"] == title))


def asq_section(prefix, month, area_key, questions):
    fields = [
        radio(f"{prefix}_{area_key}_{index}", label, ASQ_OPTIONS, required=True)
        for index, label in enumerate(questions, start=1)
    ]
    fields.append(field(f"{prefix}_{TOTAL_KEYS[area_key]}_total", f"{AREA_LABELS[area_key]} total", "number", staffOnly=True))
    return {"title": f"ASQ-3 {month} Month {AREA_LABELS[area_key]}", "fields": fields}


def asq_overall_section(prefix, month):
    fields = []
    for key, label in ASQ_OVERALL_FIELDS:
        fields.append(radio(f"{prefix}_overall_{key}", label, YES_NO))
        fields.append(field(f"{prefix}_overall_{key}_comments", "Comments", "textarea"))
    return {"title": f"ASQ-3 {month} Month Overall Questions", "fields": fields}


def asq_summary_section(prefix, month, age_range):
    fields = []
    for area_key in ["communication", "gross", "fine", "problem", "social"]:
        fields.append(field(f"{prefix}_summary_{SUMMARY_KEYS[area_key]}_score", f"{AREA_LABELS[area_key]} total score", "number", staffOnly=True))
    for area_key in ["communication", "gross", "fine", "problem", "social"]:
        fields.append(field(f"{prefix}_{SUMMARY_KEYS[area_key]}_zone", f"{AREA_LABELS[area_key]} score zone", "select", options=ZONE_OPTIONS, staffOnly=True))
    fields.extend([
        field(f"{prefix}_follow_up_provide_activities", "Provide activities and monitor", "checkbox", staffOnly=True),
        field(f"{prefix}_follow_up_rescreen", "Provide activities and rescreen", "checkbox", staffOnly=True),
        field(f"{prefix}_follow_up_primary_care_referral", "Refer to primary health care provider or community agency", "checkbox", staffOnly=True),
        field(f"{prefix}_follow_up_early_intervention", "Refer to early intervention or early childhood special education", "checkbox", staffOnly=True),
        field(f"{prefix}_follow_up_no_action", "No further action at this time", "checkbox", staffOnly=True),
        field(f"{prefix}_follow_up_notes", "Staff follow-up notes", "textarea", staffOnly=True),
    ])
    return {
        "title": f"ASQ-3 {month} Month Score Summary and Follow-Up",
        "staffOnly": True,
        "fields": fields,
        "content": [{"type": "note", "title": "Age range", "text": age_range, "variant": "disclaimer"}],
    }


def original_section(source_file, source_url=None):
    content = [{"type": "note", "title": "Source document", "text": f"Mapped from {source_file}.", "variant": "disclaimer"}]
    if source_url:
        content.append({"type": "link", "label": "Open original form", "url": source_url})
    return {"title": "Original Paper Form", "fields": [], "content": content}


def build_asq_visit(form_id, month, age_range, source_file):
    prefix = f"asq{month}"
    sections = [
        {
            "title": "Patient and Visit Information",
            "fields": deepcopy(COMMON_PATIENT_FIELDS)
            + [
                field(f"{prefix}_completed_date", "Date ASQ completed", "date"),
                field(f"{prefix}_return_by", "Please return this questionnaire by", "date"),
                field(f"{prefix}_notes", "Notes", "textarea"),
            ],
        }
    ]
    for area_key in ["communication", "gross", "fine", "problem", "social"]:
        sections.append(asq_section(prefix, month, area_key, ASQ_QUESTIONS[month][area_key]))
    sections.append(asq_overall_section(prefix, month))
    sections.append(asq_summary_section(prefix, month, age_range))
    sections.append(original_section(source_file))
    return {
        "id": form_id,
        "name": f"{month} Months Visit",
        "title": f"{month} Months Visit",
        "category": "Well Visits",
        "summary": f"ASQ-3 {month} month questionnaire with patient responses and staff scoring summary.",
        "estimatedMinutes": 24,
        "status": "active",
        "sourceFile": source_file,
        "sections": sections,
    }


def build_newborn(forms):
    sections = [
        {
            "title": "Patient and Visit Information",
            "fields": deepcopy(COMMON_PATIENT_FIELDS)
            + [
                field("birth_weight", "Birth weight", "text"),
                field("discharge_weight", "Discharge weight", "text"),
                field("feeding_type", "Feeding type", "select", options=["Breastfeeding", "Formula", "Both breast milk and formula", "Other"]),
            ],
        },
        {
            "title": "Bright Futures 2 to 5 Day Visit",
            "fields": [
                field("visit_concerns", "Concerns, questions, or problems to discuss today", "textarea"),
                field("topics_how_you_are_feeling", "Topics: how you are feeling", "checkbox-group", options=["Your health", "Feeling sad", "Family stress", "Unwanted advice", "Starting a daily routine", "How you are doing with your baby", "Calming your baby", "Crib safety and where your baby sleeps"]),
                field("topics_getting_used_to_baby", "Topics: getting used to your baby", "checkbox-group", options=["How your baby sleeps", "Placing baby on back to sleep", "Drinking enough"]),
                field("topics_feeding", "Topics: feeding your baby", "checkbox-group", options=["Jaundice", "Burping", "Breastfeeding", "Formula"]),
                field("topics_safety", "Topics: safety", "checkbox-group", options=["Car safety seat", "Cigarette smoke", "Water heater temperature", "When to call the doctor's office", "Taking your baby's temperature", "Not getting sick", "Hand washing"]),
                field("topics_baby_care", "Topics: baby care", "checkbox-group", options=["Emergency situations", "Leaving the house", "Skin care", "Sunburns"]),
                radio("baby_vision_concerns", "Do you have concerns about how your child sees?", ["Yes", "No", "Unsure"]),
                radio("baby_special_health_needs", "Does your child have any special health care needs?", YES_NO),
                field("baby_special_health_needs_description", "Special health care needs description", "textarea"),
                field("family_major_changes", "Major changes in your family lately", "checkbox-group", options=["Move", "Job change", "Separation", "Divorce", "Death in the family", "Other"]),
                field("family_major_changes_description", "Describe family changes", "textarea"),
                radio("tobacco_exposure", "Does your child live with anyone who uses tobacco or spend time where people smoke?", YES_NO),
                radio("baby_growth_concerns", "Do you have concerns about how your baby is growing, learning, or acting?", YES_NO),
                field("baby_growth_concerns_description", "Describe growth, learning, or behavior concerns", "textarea"),
                field("baby_tasks", "Tasks your baby is able to do", "checkbox-group", options=["Eats well", "Follows your face", "Turns and calms to your voice", "Can suck, swallow, and breathe easily"]),
            ],
        },
        {
            "title": "Caregiver Mood - PHQ-2",
            "fields": [
                radio("phq2_interest", "Over the past 2 weeks, how often have you had little interest or pleasure in doing things?", ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]),
                radio("phq2_down_depressed", "Over the past 2 weeks, how often have you felt down, depressed, or hopeless?", ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]),
                field("phq2_total_score", "PHQ-2 total score", "number", staffOnly=True),
            ],
        },
        clone_section(forms, "2-months-visit", "Edinburgh Postnatal Depression Scale (EPDS)"),
        clone_section(forms, "3-year-visit", "Social Determinants of Health Assessment"),
        original_section("Newborn 2 to 5 Days.pdf"),
    ]
    return {
        "id": "newborn-2-5-days",
        "name": "Newborn 2 to 5 Days",
        "title": "Newborn 2 to 5 Days",
        "category": "Well Visits",
        "summary": "Bright Futures newborn previsit questionnaire with caregiver mood, EPDS, and social needs screening.",
        "estimatedMinutes": 18,
        "status": "active",
        "sourceFile": "Newborn 2 to 5 Days.pdf",
        "sections": sections,
    }


def update_asthma_templates(forms):
    act = next(form for form in forms if form["id"] == "asthma-act-12-plus")
    past_4_weeks = act["sections"][1]["fields"]
    past_4_weeks[:] = [item for item in past_4_weeks if item["id"] not in {"act_total_score", "act_control_status"}]
    past_4_weeks.extend([
        field("act_total_score", "ACT total score", "number", staffOnly=True),
        field("act_control_status", "ACT control status", "text", staffOnly=True),
    ])
    util = next(section for section in act["sections"] if section["title"] == "Utilization")
    if not any(item["id"] == "hospitalizations" for item in util["fields"]):
        util["fields"].insert(1, field("hospitalizations", "Inpatient hospitalizations for asthma in past 12 months", "number"))
    if any(item["id"] == "oral_steroids" for item in util["fields"]):
        util["fields"] = [item for item in util["fields"] if item["id"] != "oral_steroids"]

    cact = next(form for form in forms if form["id"] == "child-act-4-11")
    caregiver = next(section for section in cact["sections"] if section["title"] == "Caregiver Questions")
    caregiver["fields"] = [item for item in caregiver["fields"] if item["id"] not in {"cact_total_score", "cact_control_status"}]
    caregiver["fields"].extend([
        field("cact_total_score", "C-ACT total score", "number", staffOnly=True),
        field("cact_control_status", "C-ACT control status", "text", staffOnly=True),
    ])
    original = next(section for section in cact["sections"] if section["title"] == "Original Paper Form")
    original["content"] = [
        {"type": "note", "title": "Source document", "text": "Mapped from C-ACT_MN 4-11 yrs.pdf.", "variant": "disclaimer"},
        {"type": "link", "label": "Open original form", "url": "/source-forms/C-ACT_MN-4-11-yrs.pdf"},
    ]


def main():
    forms = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    replacements = {
        "42-months-visit": build_asq_visit("42-months-visit", "42", "39 months 0 days through 44 months 30 days", "42 Months Visit.pdf"),
        "54-months-visit": build_asq_visit("54-months-visit", "54", "51 months 0 days through 56 months 30 days", "54 Months Visit.pdf"),
        "newborn-2-5-days": build_newborn(forms),
    }
    updated = [replacements.get(form.get("id"), form) for form in forms]
    update_asthma_templates(updated)
    TEMPLATE_PATH.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    for form_id in [*replacements, "asthma-act-12-plus", "child-act-4-11"]:
        form = next(item for item in updated if item["id"] == form_id)
        field_count = sum(len(section.get("fields", [])) for section in form["sections"])
        print(f"Updated {form_id}: {len(form['sections'])} sections, {field_count} fields")


if __name__ == "__main__":
    main()
