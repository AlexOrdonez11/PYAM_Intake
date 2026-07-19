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

ASQ_OVERALL_FIELDS = [
    ("hears_well", "Do you think your child hears well?"),
    ("talks_like_peers", "Do you think your child talks like other children this age?"),
    ("understand_speech", "Can you understand most of what your child says?"),
    ("walks_runs_climbs", "Do you think your child walks, runs, and climbs like other children this age?"),
    ("family_hearing_history", "Does either parent have a family history of childhood deafness or hearing impairment?"),
    ("vision_concerns", "Do you have any concerns about your child's vision?"),
    ("recent_medical_problems", "Has your child had any medical problems in the last several months?"),
    ("behavior_concerns", "Do you have any concerns about your child's behavior?"),
    ("other_concerns", "Does anything else about your child concern you?"),
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

ASQ_QUESTIONS = {
    "20": {
        "communication": [
            "Does your child imitate a two-word sentence?",
            "Does your child say eight or more words in addition to Mama and Dada?",
            "Without your showing, does your child point to the correct picture when asked?",
            "When you point to a picture and ask what it is, does your child name at least one picture?",
            "Without clues, can your child follow at least three simple directions?",
            "Does your child say two or three words that represent different ideas together?",
        ],
        "gross": [
            "Does your child walk down stairs with help, holding onto a railing or wall?",
            "When shown how to kick a large ball, does your child try to kick it?",
            "Does your child walk either up or down at least two steps by themself?",
            "Does your child run fairly well, stopping without bumping into things or falling often?",
            "Does your child jump with both feet leaving the floor at the same time?",
            "Does your child kick a ball forward without holding onto support?",
        ],
        "fine": [
            "Does your child get a spoon into the mouth right side up so food usually does not spill?",
            "Does your child stack three small blocks or toys on top of each other?",
            "Does your child turn pages of a book by themself?",
            "Does your child make a mark on paper with the tip of a crayon, pencil, or pen?",
            "Does your child stack five small blocks or toys on top of each other?",
            "Does your child use a turning motion with the hand while trying to turn knobs, wind toys, or twist lids?",
        ],
        "problem": [
            "Without showing, does your child scribble back and forth when given a crayon?",
            "After watching you draw a line, does your child copy by drawing a single line?",
            "After a crumb or small cereal is dropped into a clear bottle, does your child turn the bottle over to dump it out?",
            "Does your child copy a circle after watching you draw one?",
            "Does your child line up objects after watching you do it?",
            "Does your child use objects to solve simple problems, such as getting something out of reach?",
        ],
        "social": [
            "Does your child copy activities you do, such as wiping a spill or combing hair?",
            "Does your child drink from a cup or glass and put it down with little spilling?",
            "Does your child use a spoon to feed themself with little spilling?",
            "Does your child help undress by removing clothing items such as socks, shoes, or a hat?",
            "Does your child pretend to take care of a doll or stuffed animal?",
            "Does your child get your attention to show you something interesting?",
        ],
    },
    "22": {
        "communication": [
            "Does your child point to the correct picture when you name common objects?",
            "Does your child imitate a two-word sentence?",
            "Does your child say eight or more words in addition to Mama and Dada?",
            "Does your child correctly name at least one picture when asked?",
            "Can your child follow simple directions without gestures?",
            "Does your child put two or three words together to express different ideas?",
        ],
        "gross": [
            "Does your child walk down stairs with help or while holding onto support?",
            "Does your child kick a large ball by moving the leg forward?",
            "Does your child walk up or down at least two steps by themself?",
            "Does your child run fairly well without falling often?",
            "Does your child jump with both feet leaving the floor?",
            "Does your child kick a ball forward without holding onto anything?",
        ],
        "fine": [
            "Does your child stack small blocks or toys?",
            "Does your child turn book pages by themself?",
            "Does your child make marks on paper with a crayon, pencil, or pen?",
            "Does your child stack five or more small blocks or toys?",
            "Does your child use a turning motion with the hand?",
            "Does your child copy simple marks after watching you draw them?",
        ],
        "problem": [
            "Does your child scribble back and forth without being shown?",
            "Does your child copy a line after watching you draw one?",
            "Does your child dump a small object out of a clear bottle after watching you?",
            "Does your child solve simple problems using a tool or object?",
            "Does your child line up objects after watching you do it?",
            "Does your child use pretend play or objects to represent something else?",
        ],
        "social": [
            "Does your child copy household activities you do?",
            "Does your child feed themself with a spoon with little spilling?",
            "Does your child help undress by removing clothing items?",
            "Does your child drink from a cup and put it down again with little spilling?",
            "Does your child pretend with a doll, stuffed animal, or other toy?",
            "Does your child seek help or attention when needed?",
        ],
    },
    "27": {
        "communication": [
            "Does your child correctly name at least two pictures when asked?",
            "Does your child say two or three words together to express different ideas?",
            "Does your child follow at least two directions without gestures?",
            "Does your child use words such as me, mine, I, or you?",
            "Does your child name common objects or actions when asked?",
            "Does your child make short sentences that include a noun and verb?",
        ],
        "gross": [
            "Does your child walk up or down stairs with help or while holding onto a railing?",
            "Does your child run fairly well without falling often?",
            "Does your child jump with both feet leaving the floor?",
            "Does your child kick a ball forward without support?",
            "Does your child walk on tiptoes when shown how?",
            "Does your child jump forward or off a low step with both feet?",
        ],
        "fine": [
            "Does your child use a turning motion with the hand to twist knobs, wind toys, or unscrew lids?",
            "Does your child stack small blocks or toys into a tower?",
            "Does your child copy a line after watching you draw one?",
            "Does your child string small items or place small objects into openings?",
            "Does your child turn pages one at a time?",
            "Does your child copy simple shapes or strokes?",
        ],
        "problem": [
            "Does your child copy a line after watching you draw one?",
            "Does your child line up objects after watching you do it?",
            "Does your child use a chair, stool, or tool to reach something?",
            "Does your child repeat a sequence after watching you do it?",
            "Does your child match objects by shape, color, or category?",
            "Does your child complete a simple puzzle or fitting task?",
        ],
        "social": [
            "Does your child use a spoon or fork with little spilling?",
            "Does your child help with dressing or undressing?",
            "Does your child pretend with toys in a way that represents real activities?",
            "Does your child get your attention to show you something interesting?",
            "Does your child wash and dry hands with help?",
            "Does your child play near or with other children?",
        ],
    },
    "30": {
        "communication": [
            "Does your child follow two-step directions without gestures?",
            "Does your child name familiar pictures or objects?",
            "Does your child use short sentences of three or more words?",
            "Does your child correctly use words such as me, I, mine, or you?",
            "Does your child tell you what they want using words?",
            "Does your child describe what is happening in a picture or during play?",
        ],
        "gross": [
            "Does your child run well without falling often?",
            "Does your child walk up or down stairs with one foot on each step when helped?",
            "Does your child jump with both feet leaving the floor?",
            "Does your child kick a ball forward without support?",
            "Does your child stand on one foot briefly when shown?",
            "Does your child jump forward or off a low step with both feet?",
        ],
        "fine": [
            "Does your child stack small blocks or toys into a tower?",
            "Does your child copy a line after watching you draw one?",
            "Does your child use a turning motion with the hand?",
            "Does your child string items or place small objects accurately?",
            "Does your child copy simple shapes or strokes?",
            "Does your child turn pages one at a time?",
        ],
        "problem": [
            "Does your child line up objects after watching you do it?",
            "Does your child complete a simple puzzle or fitting task?",
            "Does your child use a tool or object to get something out of reach?",
            "Does your child repeat simple sequences in play?",
            "Does your child sort or match objects by category?",
            "Does your child solve simple problems without help?",
        ],
        "social": [
            "Does your child use a spoon or fork with little spilling?",
            "Does your child help with dressing or undressing?",
            "Does your child pretend with toys in a way that represents real activities?",
            "Does your child wash and dry hands with help?",
            "Does your child play near or with other children?",
            "Does your child use words to ask for help or attention?",
        ],
    },
    "33": {
        "communication": [
            "Does your child make sentences of three or four words?",
            "Does your child follow directions that include two actions?",
            "Does your child name familiar pictures, objects, or actions?",
            "Does your child use words such as me, I, mine, and you correctly?",
            "Does your child describe what is happening in a picture or during play?",
            "Can most people understand what your child says?",
        ],
        "gross": [
            "Does your child run well, stopping and starting without falling often?",
            "Does your child walk up stairs using alternating feet with help or support?",
            "Does your child jump with both feet leaving the floor?",
            "Does your child kick a ball forward without holding onto support?",
            "Does your child stand on one foot briefly when shown?",
            "Does your child jump forward or off a low step with both feet?",
        ],
        "fine": [
            "Does your child copy a line after watching you draw one?",
            "Does your child stack small blocks or toys into a tower?",
            "Does your child string small items or place small objects accurately?",
            "Does your child use a turning motion to open or close objects?",
            "Does your child copy simple shapes or strokes?",
            "Does your child turn book pages one at a time?",
        ],
        "problem": [
            "Does your child complete a simple puzzle or fitting task?",
            "Does your child match objects by shape, color, or category?",
            "Does your child repeat simple sequences in play?",
            "Does your child use a tool or object to solve a problem?",
            "Does your child understand simple concepts such as one, two, or another?",
            "Does your child solve simple problems without help?",
        ],
        "social": [
            "Does your child dress or undress with help?",
            "Does your child use a spoon or fork with little spilling?",
            "Does your child play near or with other children?",
            "Does your child pretend with toys in a way that represents real activities?",
            "Does your child wash and dry hands with help?",
            "Does your child separate from caregivers for short periods when supported?",
        ],
    },
}

FORM_META = {
    "20-months-visit": {"month": "20", "ageRange": "19 months 0 days through 20 months 30 days", "minutes": 22, "pdf": "20 Months Visit.pdf", "summary": "ASQ-3 20 month questionnaire with patient responses and staff scoring summary."},
    "22-months-visit": {"month": "22", "ageRange": "21 months 0 days through 22 months 30 days", "minutes": 22, "pdf": "22-Months Visit.pdf", "summary": "ASQ-3 22 month questionnaire with patient responses and staff scoring summary."},
    "27-months-visit": {"month": "27", "ageRange": "25 months 16 days through 28 months 15 days", "minutes": 24, "pdf": "27 Months Visit.pdf", "summary": "ASQ-3 27 month questionnaire with patient responses and staff scoring summary."},
    "30-months-visit": {"month": "30", "ageRange": "28 months 16 days through 31 months 15 days", "minutes": 32, "pdf": "30 Months Visit.pdf", "summary": "ASQ-3 30 month questionnaire with PEDS, PPSC, and social needs screening."},
    "33-months-visit": {"month": "33", "ageRange": "31 months 16 days through 34 months 15 days", "minutes": 24, "pdf": "33 Months visit.pdf", "summary": "ASQ-3 33 month questionnaire with patient responses and staff scoring summary."},
}


def radio_field(field_id, label, options=None, required=False, staff_only=False):
    field = {"id": field_id, "label": label, "type": "radio", "options": options or ASQ_OPTIONS}
    if required:
        field["required"] = True
    if staff_only:
        field["staffOnly"] = True
    return field


def asq_section(prefix, month, area_key, questions):
    fields = [
        radio_field(f"{prefix}_{area_key}_{index}", label, ASQ_OPTIONS, required=True)
        for index, label in enumerate(questions, start=1)
    ]
    total_key = TOTAL_KEYS[area_key]
    summary_key = SUMMARY_KEYS[area_key]
    fields.append({"id": f"{prefix}_{total_key}_total", "label": f"{AREA_LABELS[area_key]} total", "type": "number", "staffOnly": True})
    return {
        "title": f"ASQ-3 {month} Month {AREA_LABELS[area_key]}",
        "fields": fields,
        "content": [
            {
                "type": "note",
                "title": "Scoring",
                "text": "Patient answers are scored automatically as Yes = 10, Sometimes = 5, and Not Yet = 0.",
                "variant": "disclaimer",
            }
        ],
    }


def asq_overall_section(prefix, month):
    fields = []
    for key, label in ASQ_OVERALL_FIELDS:
        fields.append(radio_field(f"{prefix}_overall_{key}", label, YES_NO))
        fields.append({"id": f"{prefix}_overall_{key}_comments", "label": "Comments", "type": "textarea"})
    return {"title": f"ASQ-3 {month} Month Overall Questions", "fields": fields}


def asq_summary_section(prefix, month, age_range):
    fields = []
    for area_key in ["communication", "gross", "fine", "problem", "social"]:
        summary_key = SUMMARY_KEYS[area_key]
        fields.append({"id": f"{prefix}_summary_{summary_key}_score", "label": f"{AREA_LABELS[area_key]} total score", "type": "number", "staffOnly": True})
    for area_key in ["communication", "gross", "fine", "problem", "social"]:
        summary_key = SUMMARY_KEYS[area_key]
        fields.append({"id": f"{prefix}_{summary_key}_zone", "label": f"{AREA_LABELS[area_key]} score zone", "type": "select", "options": ZONE_OPTIONS, "staffOnly": True})
    fields.extend(
        [
            {"id": f"{prefix}_follow_up_provide_activities", "label": "Provide activities and monitor", "type": "checkbox", "staffOnly": True},
            {"id": f"{prefix}_follow_up_rescreen", "label": "Provide activities and rescreen", "type": "checkbox", "staffOnly": True},
            {"id": f"{prefix}_follow_up_primary_care_referral", "label": "Refer to primary health care provider or community agency", "type": "checkbox", "staffOnly": True},
            {"id": f"{prefix}_follow_up_early_intervention", "label": "Refer to early intervention or early childhood special education", "type": "checkbox", "staffOnly": True},
            {"id": f"{prefix}_follow_up_no_action", "label": "No further action at this time", "type": "checkbox", "staffOnly": True},
            {"id": f"{prefix}_follow_up_notes", "label": "Staff follow-up notes", "type": "textarea", "staffOnly": True},
        ]
    )
    return {
        "title": f"ASQ-3 {month} Month Score Summary and Follow-Up",
        "staffOnly": True,
        "fields": fields,
        "content": [
            {
                "type": "note",
                "title": "Age range",
                "text": age_range,
                "variant": "disclaimer",
            }
        ],
    }


def original_form_section(pdf_name):
    return {
        "title": "Original Paper Form",
        "fields": [],
        "content": [
            {
                "type": "note",
                "title": "Source document",
                "text": f"Mapped from {pdf_name}. Keep the source PDF available for exact paper-form wording and visual verification.",
                "variant": "disclaimer",
            }
        ],
    }


def clone_section(source_forms, source_form_id, title):
    source_form = next(form for form in source_forms if form["id"] == source_form_id)
    section = next(section for section in source_form["sections"] if section["title"] == title)
    return deepcopy(section)


def build_form(form_id, source_forms):
    meta = FORM_META[form_id]
    month = meta["month"]
    prefix = f"asq{month}"
    sections = [
        {
            "title": "Patient and Visit Information",
            "fields": deepcopy(COMMON_PATIENT_FIELDS)
            + [
                {"id": f"{prefix}_completed_date", "label": "Date ASQ completed", "type": "date"},
                {"id": f"{prefix}_return_by", "label": "Please return this questionnaire by", "type": "date"},
                {"id": f"{prefix}_prematurity_adjusted", "label": "Was age adjusted for prematurity when selecting this questionnaire?", "type": "radio", "options": YES_NO},
                {"id": f"{prefix}_notes", "label": "Notes", "type": "textarea"},
            ],
        }
    ]
    for area_key in ["communication", "gross", "fine", "problem", "social"]:
        sections.append(asq_section(prefix, month, area_key, ASQ_QUESTIONS[month][area_key]))
    sections.append(asq_overall_section(prefix, month))
    sections.append(asq_summary_section(prefix, month, meta["ageRange"]))
    if form_id == "30-months-visit":
        sections.append(clone_section(source_forms, "3-year-visit", "PEDS Response Form"))
        sections.append(clone_section(source_forms, "3-year-visit", "Preschool Pediatric Symptom Checklist (PPSC)"))
        sections.append(clone_section(source_forms, "3-year-visit", "Social Determinants of Health Assessment"))
    sections.append(original_form_section(meta["pdf"]))

    return {
        "id": form_id,
        "name": f"{month} Months Visit",
        "title": f"{month} Months Visit",
        "category": "Well Visits",
        "summary": meta["summary"],
        "estimatedMinutes": meta["minutes"],
        "status": "active",
        "sections": sections,
    }


def main():
    forms = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    replacements = {form_id: build_form(form_id, forms) for form_id in FORM_META}
    updated = [replacements.get(form.get("id"), form) for form in forms]
    TEMPLATE_PATH.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    for form_id, form in replacements.items():
        field_count = sum(len(section.get("fields", [])) for section in form["sections"])
        print(f"Updated {form_id}: {len(form['sections'])} sections, {field_count} fields")


if __name__ == "__main__":
    main()
