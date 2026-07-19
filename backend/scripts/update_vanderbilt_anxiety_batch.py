import json
from pathlib import Path


TEMPLATE_PATH = Path("backend/data/form-templates.json")

VANDERBILT_OPTIONS = ["Never (0)", "Occasionally (1)", "Often (2)", "Very Often (3)"]
PERFORMANCE_OPTIONS = ["Excellent (1)", "Above Average (2)", "Average (3)", "Somewhat of a Problem (4)", "Problematic (5)"]
SIDE_EFFECT_OPTIONS = ["Never", "Mild", "Moderate", "Severe"]
MEDICATION_OPTIONS = ["Was on medication", "Was not on medication", "Not sure"]

PATIENT_FIELDS = [
    {"id": "patient_name", "label": "Child full name", "type": "text", "required": True},
    {"id": "date_of_birth", "label": "Date of birth", "type": "date"},
    {"id": "completed_by", "label": "Completed by", "type": "text"},
    {"id": "relationship", "label": "Relationship to child", "type": "select", "options": ["Parent", "Guardian", "Teacher", "Other"]},
    {"id": "phone", "label": "Phone number", "type": "tel"},
    {"id": "grade", "label": "Grade", "type": "text"},
]

TEACHER_FIELDS = [
    {"id": "teacher_name", "label": "Teacher's name", "type": "text", "required": True},
    {"id": "school", "label": "School", "type": "text"},
    {"id": "class_period", "label": "Class period or time of day", "type": "text"},
    {"id": "teacher_fax", "label": "Teacher fax number", "type": "text"},
    {"id": "evaluation_period", "label": "Weeks or months able to evaluate behaviors", "type": "text"},
    {"id": "medication_status", "label": "This evaluation is based on a time when the child", "type": "radio", "options": MEDICATION_OPTIONS},
]

PARENT_INITIAL = [
    "Does not pay attention to details or makes careless mistakes.",
    "Has difficulty keeping attention on what needs to be done.",
    "Does not seem to listen when spoken to directly.",
    "Does not follow through on instructions and does not finish activities.",
    "Has difficulty organizing tasks and activities.",
    "Avoids, dislikes, or does not want to start tasks that require ongoing mental effort.",
    "Loses things necessary for tasks or activities.",
    "Is easily distracted by noises or other stimuli.",
    "Is forgetful in daily activities.",
    "Fidgets with or taps hands or feet or squirms in seat.",
    "Leaves seat when remaining seated is expected.",
    "Runs about or climbs too much when remaining seated is expected.",
    "Has difficulty playing or beginning quiet play games.",
    "Is on the go or often acts as if driven by a motor.",
    "Talks too much.",
    "Blurts out answers before questions have been completed.",
    "Has difficulty waiting his or her turn.",
    "Interrupts or intrudes into others' conversations or activities.",
    "Loses temper.",
    "Is touchy or easily annoyed.",
    "Is angry or resentful.",
    "Argues with authority figures or adults.",
    "Actively defies or refuses to adhere to requests or rules.",
    "Deliberately annoys people.",
    "Blames others for his or her mistakes or misbehaviors.",
    "Is spiteful and wants to get even.",
    "Bullies, threatens, or intimidates others.",
    "Starts physical fights.",
    "Has used a weapon that can cause serious harm.",
    "Has been physically cruel to people.",
    "Has been physically cruel to animals.",
    "Has stolen while confronting the person.",
    "Has forced someone into sexual activity.",
    "Has deliberately set fires to cause damage.",
    "Deliberately destroys others' property.",
    "Has broken into someone else's home, business, or car.",
    "Lies to get out of trouble, obtain goods or favors, or avoid obligations.",
    "Has stolen items of value.",
    "Has stayed out at night without permission beginning before age 13.",
    "Has run away from home twice or once for an extended period.",
    "Is often truant from school.",
    "Is fearful, anxious, or worried.",
    "Is afraid to try new things for fear of making mistakes.",
    "Feels worthless or inferior.",
    "Blames self for problems or feels guilty.",
    "Feels lonely, unwanted, or unloved.",
    "Is sad, unhappy, or depressed.",
    "Is self-conscious or easily embarrassed.",
]

TEACHER_INITIAL = [
    "Does not give attention to details or makes careless mistakes in schoolwork.",
    "Has difficulty sustaining attention on tasks or activities.",
    "Does not seem to listen when spoken to directly.",
    "Does not follow through on instructions and does not finish schoolwork.",
    "Has difficulty organizing tasks and activities.",
    "Avoids, dislikes, or does not want to start tasks that require sustained mental effort.",
    "Loses things necessary for tasks or activities.",
    "Is easily distracted by extraneous stimuli.",
    "Is forgetful in daily activities.",
    "Fidgets with hands or feet or squirms in seat.",
    "Leaves seat when remaining seated is expected.",
    "Runs about or climbs too much when remaining seated is expected.",
    "Has difficulty playing or engaging in leisure activities quietly.",
    "Is on the go or often acts as if driven by a motor.",
    "Talks excessively.",
    "Blurts out answers before questions have been completed.",
    "Has difficulty waiting his or her turn.",
    "Interrupts or intrudes on others' conversations or activities.",
    "Loses temper.",
    "Actively defies or refuses to adhere to adults' requests or rules.",
    "Is angry or resentful.",
    "Is spiteful and vindictive.",
    "Bullies, threatens, or intimidates others.",
    "Initiates physical fights.",
    "Lies to get out of trouble or avoid obligations.",
    "Is physically cruel to people.",
    "Has stolen things of nontrivial value.",
    "Deliberately destroys others' property.",
    "Is fearful, anxious, or worried.",
    "Is self-conscious or easily embarrassed.",
    "Is afraid to try new things for fear of making mistakes.",
    "Feels worthless or inferior.",
    "Blames self for problems or feels guilty.",
    "Feels lonely, unwanted, or unloved.",
    "Is sad, unhappy, or depressed.",
]

PARENT_FOLLOWUP = PARENT_INITIAL[:26]
TEACHER_FOLLOWUP = TEACHER_INITIAL[:28]

PARENT_PERFORMANCE = [
    "Overall school performance",
    "Reading",
    "Writing",
    "Mathematics",
    "Relationship with parents",
    "Relationship with siblings",
    "Relationship with peers",
    "Participation in organized activities",
]
TEACHER_PERFORMANCE = [
    "Reading",
    "Writing",
    "Mathematics",
    "Relationship with peers",
    "Following directions",
    "Disrupting class",
    "Assignment completion",
    "Organizational skills",
]
SIDE_EFFECTS = [
    "Headache",
    "Stomachache",
    "Change of appetite",
    "Trouble sleeping",
    "Irritability in the late morning, late afternoon, or evening",
    "Socially withdrawn",
    "Extreme sadness or unusual crying",
    "Dull, tired, or listless behavior",
    "Tremors or feeling shaky",
    "Repetitive movements, tics, or jerking",
    "Picking at skin or fingers, nail biting, lip or cheek chewing",
    "Sees or hears things that are not there",
]


def symptom_fields(prefix, labels):
    return [
        {"id": f"{prefix}_{index:02d}", "label": f"{index}. {label}", "type": "radio", "options": VANDERBILT_OPTIONS, "required": True}
        for index, label in enumerate(labels, start=1)
    ]


def performance_fields(prefix, start_number, labels):
    return [
        {"id": f"{prefix}_performance_{index:02d}", "label": f"{start_number + index - 1}. {label}", "type": "radio", "options": PERFORMANCE_OPTIONS}
        for index, label in enumerate(labels, start=1)
    ]


def side_effect_fields(prefix):
    return [
        {"id": f"{prefix}_side_effect_{index:02d}", "label": label, "type": "radio", "options": SIDE_EFFECT_OPTIONS}
        for index, label in enumerate(SIDE_EFFECTS, start=1)
    ] + [{"id": f"{prefix}_side_effect_notes", "label": "Side effect notes", "type": "textarea"}]


def summary_fields(prefix, kind):
    if kind == "parent_initial":
        rows = [
            ("inattention", "Inattention count (items 1-9 scored 2 or 3)"),
            ("hyperactive_impulsive", "Hyperactive/impulsive count (items 10-18 scored 2 or 3)"),
            ("oppositional", "Oppositional defiant count (items 19-26 scored 2 or 3)"),
            ("conduct", "Conduct disorder count (items 27-41 scored 2 or 3)"),
            ("anxiety_depression", "Anxiety/depression count (items 42-48 scored 2 or 3)"),
            ("performance_4_count", "Performance count scored 4"),
            ("performance_5_count", "Performance count scored 5"),
        ]
    elif kind == "teacher_initial":
        rows = [
            ("inattention", "Inattention count (items 1-9 scored 2 or 3)"),
            ("hyperactive_impulsive", "Hyperactive/impulsive count (items 10-18 scored 2 or 3)"),
            ("oppositional_conduct", "Oppositional/conduct count (items 19-28 scored 2 or 3)"),
            ("anxiety_depression", "Anxiety/depression count (items 29-35 scored 2 or 3)"),
            ("performance_4_count", "Performance count scored 4"),
            ("performance_5_count", "Performance count scored 5"),
        ]
    elif kind == "parent_followup":
        rows = [
            ("inattention", "Inattention count (items 1-9 scored 2 or 3)"),
            ("hyperactive_impulsive", "Hyperactive/impulsive count (items 10-18 scored 2 or 3)"),
            ("oppositional", "Oppositional defiant count (items 19-26 scored 2 or 3)"),
            ("performance_4_count", "Performance count scored 4"),
            ("performance_5_count", "Performance count scored 5"),
        ]
    else:
        rows = [
            ("inattention", "Inattention count (items 1-9 scored 2 or 3)"),
            ("hyperactive_impulsive", "Hyperactive/impulsive count (items 10-18 scored 2 or 3)"),
            ("oppositional_conduct", "Oppositional/conduct count (items 19-28 scored 2 or 3)"),
            ("performance_4_count", "Performance count scored 4"),
            ("performance_5_count", "Performance count scored 5"),
        ]
    fields = [{"id": f"{prefix}_{key}", "label": label, "type": "number", "staffOnly": True} for key, label in rows]
    fields.extend([
        {"id": f"{prefix}_impairment_present", "label": "Performance impairment present", "type": "text", "staffOnly": True},
        {"id": f"{prefix}_staff_notes", "label": "Staff notes", "type": "textarea", "staffOnly": True},
    ])
    return {"title": "Scoring Summary", "staffOnly": True, "fields": fields}


def original_section(source_file):
    return {
        "title": "Original Paper Form",
        "fields": [],
        "content": [{"type": "note", "title": "Source document", "text": f"Mapped from {source_file}.", "variant": "disclaimer"}],
    }


def vanderbilt_parent_initial():
    return {
        "id": "vanderbilt-parent",
        "name": "Vanderbilt Parent Assessment",
        "title": "Vanderbilt Parent Assessment",
        "category": "Behavioral Health",
        "description": "Parent initial Vanderbilt assessment for ADHD symptoms, comorbid symptoms, and performance.",
        "summary": "Parent initial Vanderbilt assessment with automatic domain counts and impairment indicators.",
        "estimatedMinutes": 18,
        "status": "active",
        "sourceFile": "Vanderbilt Parent Assessment.pdf",
        "sections": [
            {"title": "Child and Parent Information", "fields": PATIENT_FIELDS + [{"id": "medication_status", "label": "This evaluation is based on a time when your child", "type": "radio", "options": MEDICATION_OPTIONS}]},
            {"title": "Symptoms", "fields": symptom_fields("vanderbilt_parent", PARENT_INITIAL)},
            {"title": "Academic and Social Performance", "fields": performance_fields("vanderbilt_parent", 49, PARENT_PERFORMANCE) + [{"id": "vanderbilt_parent_comments", "label": "Comments", "type": "textarea"}]},
            {"title": "Previous Diagnosis and Treatment", "fields": [
                {"id": "vanderbilt_parent_previous_adhd", "label": "Has your child been diagnosed as having ADHD or ADD?", "type": "radio", "options": ["No", "Yes", "Not sure"]},
                {"id": "vanderbilt_parent_current_medications", "label": "Current medications or treatment notes", "type": "textarea"},
                {"id": "vanderbilt_parent_tics_motor", "label": "Motor tics", "type": "radio", "options": ["No", "Yes", "Not sure"]},
                {"id": "vanderbilt_parent_tics_vocal", "label": "Vocal tics", "type": "radio", "options": ["No", "Yes", "Not sure"]},
            ]},
            summary_fields("vanderbilt_parent", "parent_initial"),
            original_section("Vanderbilt Parent Assessment.pdf"),
        ],
    }


def vanderbilt_teacher_initial():
    return {
        "id": "vanderbilt-teacher",
        "name": "Vanderbilt Teacher Assessment",
        "title": "Vanderbilt Teacher Assessment",
        "category": "Behavioral Health",
        "description": "Teacher initial Vanderbilt assessment for ADHD symptoms, classroom performance, and tic observations.",
        "summary": "Teacher initial Vanderbilt assessment with automatic domain counts and impairment indicators.",
        "estimatedMinutes": 16,
        "status": "active",
        "sourceFile": "Vanderbilt Teacher Assessment.pdf",
        "sections": [
            {"title": "Student and Teacher Information", "fields": PATIENT_FIELDS[:2] + [{"id": "grade", "label": "Grade", "type": "text"}] + TEACHER_FIELDS},
            {"title": "Symptoms", "fields": symptom_fields("vanderbilt_teacher", TEACHER_INITIAL)},
            {"title": "Academic and Social Performance", "fields": performance_fields("vanderbilt_teacher", 36, TEACHER_PERFORMANCE) + [{"id": "vanderbilt_teacher_comments", "label": "Comments", "type": "textarea"}]},
            {"title": "Tic Behaviors", "fields": [
                {"id": "vanderbilt_teacher_tics_motor", "label": "Motor tics", "type": "radio", "options": ["No", "Yes", "Not sure"]},
                {"id": "vanderbilt_teacher_tics_vocal", "label": "Vocal tics", "type": "radio", "options": ["No", "Yes", "Not sure"]},
                {"id": "vanderbilt_teacher_tics_notes", "label": "Tic behavior notes", "type": "textarea"},
            ]},
            summary_fields("vanderbilt_teacher", "teacher_initial"),
            original_section("Vanderbilt Teacher Assessment.pdf"),
        ],
    }


def vanderbilt_followup(form_id, name, prefix, labels, perf_start, perf_labels, source_file, teacher=False):
    info_fields = PATIENT_FIELDS + ([{"id": "teacher_name", "label": "Teacher's name", "type": "text"}, {"id": "school", "label": "School", "type": "text"}] if teacher else [])
    info_fields.extend([
        {"id": f"{prefix}_medication", "label": "Medication", "type": "text"},
        {"id": "medication_status", "label": "This evaluation is based on a time when the child", "type": "radio", "options": MEDICATION_OPTIONS},
        {"id": f"{prefix}_followup_reason", "label": "Reason for follow up", "type": "textarea"},
    ])
    kind = "teacher_followup" if teacher else "parent_followup"
    return {
        "id": form_id,
        "name": name,
        "title": name,
        "category": "Behavioral Health",
        "description": "Vanderbilt follow-up rating for ADHD symptoms, performance, and medication side effects.",
        "summary": "Vanderbilt follow-up with automatic symptom counts, impairment counts, and side effect tracking.",
        "estimatedMinutes": 14,
        "status": "active",
        "sourceFile": source_file,
        "sections": [
            {"title": "Child and Rater Information", "fields": info_fields},
            {"title": "Current Symptoms", "fields": symptom_fields(prefix, labels)},
            {"title": "Academic and Social Performance", "fields": performance_fields(prefix, perf_start, perf_labels)},
            {"title": "Side Effects", "fields": side_effect_fields(prefix)},
            summary_fields(prefix, kind),
            original_section(source_file),
        ],
    }


def add_scared_summary(form):
    form["estimatedMinutes"] = max(form.get("estimatedMinutes", 10), 18)
    form["summary"] = "Initial anxiety intake with child and parent SCARED questionnaires and automatic subscale scoring."
    form["sourceFile"] = "6-12 Year Initial Anxiety.pdf"
    form["sections"] = [section for section in form["sections"] if section.get("title") != "SCARED Scoring Summary"]
    fields = []
    for prefix, label in [("child_scared", "Child"), ("parent_scared", "Parent")]:
        fields.extend([
            {"id": f"{prefix}_total_score", "label": f"{label} total anxiety score", "type": "number", "staffOnly": True},
            {"id": f"{prefix}_panic_somatic_score", "label": f"{label} panic/somatic score", "type": "number", "staffOnly": True},
            {"id": f"{prefix}_generalized_anxiety_score", "label": f"{label} generalized anxiety score", "type": "number", "staffOnly": True},
            {"id": f"{prefix}_separation_anxiety_score", "label": f"{label} separation anxiety score", "type": "number", "staffOnly": True},
            {"id": f"{prefix}_social_anxiety_score", "label": f"{label} social anxiety score", "type": "number", "staffOnly": True},
            {"id": f"{prefix}_school_avoidance_score", "label": f"{label} school avoidance score", "type": "number", "staffOnly": True},
            {"id": f"{prefix}_total_cutoff_met", "label": f"{label} total anxiety cutoff met", "type": "text", "staffOnly": True},
            {"id": f"{prefix}_panic_somatic_cutoff_met", "label": f"{label} panic/somatic cutoff met", "type": "text", "staffOnly": True},
            {"id": f"{prefix}_generalized_anxiety_cutoff_met", "label": f"{label} generalized anxiety cutoff met", "type": "text", "staffOnly": True},
            {"id": f"{prefix}_separation_anxiety_cutoff_met", "label": f"{label} separation anxiety cutoff met", "type": "text", "staffOnly": True},
            {"id": f"{prefix}_social_anxiety_cutoff_met", "label": f"{label} social anxiety cutoff met", "type": "text", "staffOnly": True},
            {"id": f"{prefix}_school_avoidance_cutoff_met", "label": f"{label} school avoidance cutoff met", "type": "text", "staffOnly": True},
        ])
    fields.append({"id": "scared_staff_notes", "label": "Staff notes", "type": "textarea", "staffOnly": True})
    form["sections"].insert(-1, {
        "title": "SCARED Scoring Summary",
        "staffOnly": True,
        "fields": fields,
        "content": [{"type": "note", "title": "Cutoffs", "text": "Total anxiety cutoff is 25. Subscale cutoffs: panic/somatic 7, generalized anxiety 9, separation anxiety 5, social anxiety 8, school avoidance 3.", "variant": "disclaimer"}],
    })


def main():
    forms = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    replacements = {
        "vanderbilt-parent": vanderbilt_parent_initial(),
        "vanderbilt-teacher": vanderbilt_teacher_initial(),
        "vanderbilt-parent-follow-up": vanderbilt_followup("vanderbilt-parent-follow-up", "Vanderbilt Parent Follow Up", "vanderbilt_parent_followup", PARENT_FOLLOWUP, 27, PARENT_PERFORMANCE, "Vanderbilt Assessment-Parent-Follow Up.pdf"),
        "vanderbilt-teacher-follow-up": vanderbilt_followup("vanderbilt-teacher-follow-up", "Vanderbilt Teacher Follow Up", "vanderbilt_teacher_followup", TEACHER_FOLLOWUP, 29, TEACHER_PERFORMANCE, "Vanderbilt Assessment-Teacher- Follow UP.pdf", teacher=True),
    }
    updated = [replacements.get(form.get("id"), form) for form in forms]
    add_scared_summary(next(form for form in updated if form["id"] == "initial-anxiety-6-12"))
    TEMPLATE_PATH.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    for form_id in [*replacements, "initial-anxiety-6-12"]:
        form = next(item for item in updated if item["id"] == form_id)
        field_count = sum(len(section.get("fields", [])) for section in form["sections"])
        print(f"Updated {form_id}: {len(form['sections'])} sections, {field_count} fields")


if __name__ == "__main__":
    main()
