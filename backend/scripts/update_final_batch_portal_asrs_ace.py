import json
from pathlib import Path


TEMPLATE_PATH = Path("backend/data/form-templates.json")

FREQUENCY_OPTIONS = ["Never", "Rarely", "Sometimes", "Often", "Very often"]
YES_NO = ["Yes", "No"]
YES_NO_UNKNOWN = ["Yes", "No", "Unknown"]

ASRS_ITEMS = [
    ("wrap_up", "How often do you have trouble wrapping up the final details of a project once the challenging parts have been done?"),
    ("organization", "How often do you have difficulty getting things in order when you have to do a task that requires organization?"),
    ("remembering", "How often do you have problems remembering appointments or obligations?"),
    ("avoid_delay", "When you have a task that requires a lot of thought, how often do you avoid or delay getting started?"),
    ("fidget", "How often do you fidget or squirm with your hands or feet when you have to sit down for a long time?"),
    ("driven", "How often do you feel overly active and compelled to do things, like you were driven by a motor?"),
    ("careless_mistakes", "How often do you make careless mistakes when you have to work on a boring or difficult project?"),
    ("attention_boring_work", "How often do you have difficulty keeping your attention when you are doing boring or repetitive work?"),
    ("concentrating_on_people", "How often do you have difficulty concentrating on what people say to you, even when they are speaking to you directly?"),
    ("misplace_things", "How often do you misplace or have difficulty finding things at home or at work?"),
    ("distracted_by_noise", "How often are you distracted by activity or noise around you?"),
    ("leave_seat", "How often do you leave your seat in meetings or other situations in which you are expected to remain seated?"),
    ("restless", "How often do you feel restless or fidgety?"),
    ("difficulty_relaxing", "How often do you have difficulty unwinding and relaxing when you have time to yourself?"),
    ("talking_too_much", "How often do you find yourself talking too much when you are in social situations?"),
    ("finish_sentences", "How often do you finish the sentences of people you are talking to before they can finish them themselves?"),
    ("waiting_turn", "How often do you have difficulty waiting your turn in situations when turn taking is required?"),
    ("interrupt_busy", "How often do you interrupt others when they are busy?"),
]

ACE_PHYSICAL = ["Headache", "Nausea", "Vomiting", "Balance problems", "Dizziness", "Visual problems", "Fatigue", "Sensitivity to light", "Sensitivity to noise", "Numbness or tingling"]
ACE_COGNITIVE = ["Feeling mentally foggy", "Feeling slowed down", "Difficulty concentrating", "Difficulty remembering"]
ACE_SLEEP = ["Drowsiness", "Sleeping less than usual", "Sleeping more than usual", "Trouble falling asleep"]
ACE_EMOTIONAL = ["Irritability", "Sadness", "More emotional", "Nervousness"]
ACE_RED_FLAGS = [
    "Headaches that worsen",
    "Looks very drowsy or cannot be awakened",
    "Cannot recognize people or places",
    "Neck pain",
    "Seizures",
    "Repeated vomiting",
    "Increasing confusion or irritability",
    "Unusual behavior change",
    "Focal neurologic signs",
    "Slurred speech",
    "Weakness or numbness in arms or legs",
    "Change in state of consciousness",
]


def field(field_id, label, field_type="text", **extra):
    data = {"id": field_id, "label": label, "type": field_type}
    data.update(extra)
    return data


def radio(field_id, label, options=None, **extra):
    return field(field_id, label, "radio", options=options or YES_NO, **extra)


def original_section(source_file):
    return {
        "title": "Original Paper Form",
        "fields": [],
        "content": [{"type": "note", "title": "Source document", "text": f"Mapped from {source_file}.", "variant": "disclaimer"}],
    }


def portal_patient_fields(adult=False):
    return [
        field("patient_first_name", "Patient first name", required=True),
        field("patient_last_name", "Patient last name", required=True),
        field("date_of_birth", "Date of birth", "date", required=True),
        field("phone", "Phone", "tel"),
        field("patient_email", "Patient email", "email" if adult else "text"),
        field("account_number", "Account number", staffOnly=True),
    ]


def proxy_fields():
    return [
        field("proxy_name", "Proxy name", required=True),
        field("proxy_address", "Proxy address", "textarea"),
        field("proxy_city", "City"),
        field("proxy_state", "State"),
        field("proxy_zip", "ZIP code"),
        field("proxy_phone", "Proxy phone", "tel"),
        field("proxy_email", "Proxy email", "email"),
        field("relationship", "Relationship to patient", "select", options=["Mother", "Father", "Step Mother", "Step Father", "Guardian", "Spouse", "Power of Attorney", "Other"]),
        field("relationship_other", "Other relationship", "text"),
    ]


def portal_form(form_id, name, source_file, adult=False, adolescent=False):
    sections = [{"title": "Patient Information", "fields": portal_patient_fields(adult=adult)}]
    if not adult:
        sections.append({"title": "Proxy Information", "fields": proxy_fields()})
    auth_fields = []
    if adult:
        auth_fields.extend([
            radio("portal_accept_service", "Accept free FollowMyHealth patient portal service?", ["Accept", "Decline"], required=True),
            field("authorize_portal", "I authorize creation or update of my patient portal account.", "checkbox", required=True),
        ])
    else:
        auth_fields.extend([
            field("authorize_release_to_proxy", "I authorize release of medical information through FollowMyHealth to the proxy named above.", "checkbox", required=True),
            field("revocation_acknowledged", "I understand that I have the right to revoke this authorization at any time.", "checkbox", required=True),
            field("redisclosure_acknowledged", "I understand disclosed information may be re-disclosed and may no longer be protected by privacy rules.", "checkbox", required=True),
            field("voluntary_acknowledged", "I understand this authorization is voluntary and treatment is not conditioned on signing.", "checkbox", required=True),
            field("activation_window_acknowledged", "I understand proxy access activation must occur within 30 days from the authorization date.", "checkbox", required=True),
        ])
        if adolescent:
            auth_fields.append(field("adolescent_privacy_acknowledged", "I understand adolescent portal access may be limited by privacy rules.", "checkbox", required=True))
    auth_fields.extend([
        field("signature", "Signature", "signature", required=True),
        field("signature_date", "Date", "date", required=True),
        field("staff_processed_by", "Processed by", "text", staffOnly=True),
        field("staff_processed_date", "Processed date", "date", staffOnly=True),
    ])
    sections.append({"title": "Authorization and Acknowledgement", "fields": auth_fields})
    sections.append(original_section(source_file))
    return {
        "id": form_id,
        "name": name,
        "title": name,
        "category": "Administrative",
        "description": "FollowMyHealth patient portal access request.",
        "summary": "Portal access authorization with patient, proxy, privacy, and staff processing fields.",
        "estimatedMinutes": 6 if adult else 8,
        "status": "active",
        "sourceFile": source_file,
        "sections": sections,
    }


def adult_asrs():
    part_a = [
        {**field(item_id, f"{index}. {label}", "scale", options=FREQUENCY_OPTIONS, required=True)}
        for index, (item_id, label) in enumerate(ASRS_ITEMS[:6], start=1)
    ]
    part_b = [
        {**field(item_id, f"{index}. {label}", "scale", options=FREQUENCY_OPTIONS, required=True)}
        for index, (item_id, label) in enumerate(ASRS_ITEMS[6:], start=7)
    ]
    return {
        "id": "adult-adhd-asrs",
        "name": "Adult ADHD Self-Report Scale",
        "title": "Adult ADHD Self-Report Scale",
        "category": "Behavioral Health",
        "description": "Adult ADHD Self-Report Scale (ASRS-v1.1) symptom checklist.",
        "summary": "ASRS-v1.1 adult ADHD screener with automatic Part A positive count and screening result.",
        "estimatedMinutes": 8,
        "status": "active",
        "sourceFile": "Adult ADHD Self-Reports Scale(ASRS-v.1).pdf",
        "sections": [
            {"title": "Patient Information", "fields": [field("patient_name", "Patient full name", required=True), field("date_of_birth", "Date of birth", "date"), field("today_date", "Today's date", "date")]},
            {"title": "Part A Symptoms", "fields": part_a},
            {"title": "Part B Symptoms", "fields": part_b},
            {"title": "ASRS Scoring Summary", "staffOnly": True, "fields": [
                field("asrs_part_a_positive_count", "Part A positive count", "number", staffOnly=True),
                field("asrs_part_b_positive_count", "Part B positive count", "number", staffOnly=True),
                field("asrs_screen_result", "ASRS screening result", "text", staffOnly=True),
                field("asrs_staff_notes", "Staff notes", "textarea", staffOnly=True),
            ]},
            original_section("Adult ADHD Self-Reports Scale(ASRS-v.1).pdf"),
        ],
    }


def wart_consent():
    return {
        "id": "wart-consent",
        "name": "Wart Treatment Consent",
        "title": "Wart Treatment Consent",
        "category": "Procedure Consent",
        "description": "Consent for wart or molluscum contagiosum treatment.",
        "summary": "Wart treatment consent with treatment, cost, recurrence, scarring, and signature acknowledgements.",
        "estimatedMinutes": 5,
        "status": "active",
        "sourceFile": "WART CONSENT.pdf",
        "sections": [
            {"title": "Patient Information", "fields": [field("patient_name", "Patient full name", required=True), field("date_of_birth", "Date of birth", "date"), field("treatment_site", "Treatment area or site", "textarea")]},
            {"title": "Treatment Acknowledgements", "fields": [
                field("wart_diagnosis_acknowledged", "The patient has been diagnosed with a wart or molluscum contagiosum.", "checkbox", required=True),
                field("wart_no_guarantee_acknowledged", "I understand there is no single treatment that can guarantee successful treatment.", "checkbox", required=True),
                field("wart_multiple_treatments_acknowledged", "I understand treatment may require one or more methods, combinations, and multiple visits.", "checkbox", required=True),
                field("wart_cost_acknowledged", "I understand in-office treatment is a surgical procedure and may be expensive.", "checkbox", required=True),
                field("wart_insurance_acknowledged", "I understand charges not covered by insurance are the responsibility of the guarantor.", "checkbox", required=True),
                field("wart_office_visit_acknowledged", "I understand an office visit is charged only if care beyond wart treatment is evaluated or managed.", "checkbox", required=True),
                field("wart_recurrence_acknowledged", "I understand treated areas may develop new lesions or recurrences.", "checkbox", required=True),
                field("wart_scar_acknowledged", "I understand the treated area may develop a scar.", "checkbox", required=True),
                field("questions_answered", "Questions were answered before signing.", "checkbox"),
            ]},
            {"title": "Signature", "fields": [field("signature", "Signature", "signature", required=True), field("relationship", "Relationship", "text"), field("signature_date", "Date", "date", required=True), field("witness", "Witness", "text", staffOnly=True)]},
            original_section("WART CONSENT.pdf"),
        ],
    }


def symptom_fields(prefix, labels):
    return [radio(f"{prefix}_{index:02d}", label, YES_NO) for index, label in enumerate(labels, start=1)]


def ace_form():
    sections = [
        {"title": "Patient and Injury Information", "fields": [
            field("patient_name", "Patient name", required=True),
            field("date_of_birth", "Date of birth", "date"),
            field("age", "Age", "number"),
            field("evaluation_date", "Evaluation date", "date"),
            field("injury_datetime", "Date/time of injury", "datetime-local"),
            field("reporter", "Reporter", "select", options=["Patient", "Parent", "Spouse", "Other"]),
            field("injury_description", "Injury description", "textarea"),
            radio("forcible_blow", "Evidence of forcible blow to the head, direct or indirect?", YES_NO_UNKNOWN),
            radio("intracranial_injury", "Evidence of intracranial injury or skull fracture?", YES_NO_UNKNOWN),
            field("impact_location", "Location of impact", "checkbox-group", options=["Frontal", "Left temporal", "Right temporal", "Left parietal", "Right parietal", "Occipital", "Neck", "Indirect force"]),
            field("cause", "Cause", "select", options=["MVC", "Pedestrian-MVC", "Fall", "Assault", "Sports", "Other"]),
            field("cause_other", "Sports or other cause details", "text"),
        ]},
        {"title": "Initial Signs", "fields": [
            radio("amnesia_before", "Amnesia before injury?", YES_NO),
            field("amnesia_before_duration", "Amnesia before duration", "text"),
            radio("amnesia_after", "Amnesia after injury?", YES_NO),
            field("amnesia_after_duration", "Amnesia after duration", "text"),
            radio("loss_consciousness", "Loss of consciousness?", YES_NO),
            field("loss_consciousness_duration", "Loss of consciousness duration", "text"),
            field("early_signs", "Early signs", "checkbox-group", options=["Appears dazed or stunned", "Confused about events", "Answers questions slowly", "Repeats questions", "Forgetful"]),
            radio("seizures", "Were seizures observed?", YES_NO),
            field("seizure_detail", "Seizure detail", "textarea"),
        ]},
        {"title": "Physical Symptoms", "fields": symptom_fields("ace_physical", ACE_PHYSICAL) + [field("ace_physical_total", "Physical total", "number", staffOnly=True)]},
        {"title": "Cognitive Symptoms", "fields": symptom_fields("ace_cognitive", ACE_COGNITIVE) + [field("ace_cognitive_total", "Cognitive total", "number", staffOnly=True)]},
        {"title": "Emotional Symptoms", "fields": symptom_fields("ace_emotional", ACE_EMOTIONAL) + [field("ace_emotional_total", "Emotional total", "number", staffOnly=True)]},
        {"title": "Sleep Symptoms", "fields": symptom_fields("ace_sleep", ACE_SLEEP) + [field("ace_sleep_total", "Sleep total", "number", staffOnly=True)]},
        {"title": "Symptom Summary", "staffOnly": True, "fields": [
            field("ace_total_symptom_score", "Total symptom score", "number", staffOnly=True),
            radio("ace_physical_activity_worse", "Symptoms worsen with physical activity?", ["Yes", "No", "N/A"]),
            radio("ace_cognitive_activity_worse", "Symptoms worsen with cognitive activity?", ["Yes", "No", "N/A"]),
            field("ace_overall_rating", "Overall rating compared to usual self (0 normal to 6 very different)", "select", options=["0", "1", "2", "3", "4", "5", "6"]),
        ]},
        {"title": "Risk Factors and Red Flags", "fields": [
            radio("concussion_history", "Concussion history?", YES_NO),
            field("previous_concussion_count", "Previous concussion count", "select", options=["0", "1", "2", "3", "4", "5", "6+"]),
            field("longest_symptom_duration", "Longest symptom duration", "text"),
            radio("headache_history", "Headache history?", YES_NO),
            field("migraine_history", "Migraine history", "checkbox-group", options=["Personal", "Family"]),
            field("developmental_history", "Developmental history", "checkbox-group", options=["Learning disabilities", "ADHD", "Other developmental disorder"]),
            field("psychiatric_history", "Psychiatric history", "checkbox-group", options=["Anxiety", "Depression", "Sleep disorder", "Other psychiatric disorder"]),
            field("medical_disorders_or_medications", "Other comorbid medical disorders or medication usage", "textarea"),
            field("ace_red_flags", "Red flags for acute emergency management", "checkbox-group", options=ACE_RED_FLAGS),
            field("ace_red_flag_count", "Red flag count", "number", staffOnly=True),
        ]},
        {"title": "Diagnosis and Follow-Up", "staffOnly": True, "fields": [
            field("ace_diagnosis", "Diagnosis", "select", options=["Concussion without LOC", "Concussion with LOC", "Concussion unspecified", "Other", "No diagnosis"], staffOnly=True),
            field("ace_follow_up_action", "Follow-up action", "checkbox-group", options=["No follow-up needed", "Office monitoring", "Neuropsychological testing", "Neurosurgery", "Neurology", "Sports medicine", "Physiatrist", "Psychiatrist", "Emergency department", "Other"], staffOnly=True),
            field("ace_next_follow_up_date", "Next follow-up date", "date", staffOnly=True),
            field("ace_completed_by", "ACE completed by", "text", staffOnly=True),
            field("ace_staff_notes", "Staff notes", "textarea", staffOnly=True),
        ]},
        original_section("AcuteConcussionEvaluation_ACETest.pdf"),
    ]
    return {
        "id": "acute-concussion-evaluation",
        "name": "Acute Concussion Evaluation",
        "title": "Acute Concussion Evaluation",
        "category": "Injury",
        "description": "ACE physician/clinician office version for suspected concussion.",
        "summary": "Acute concussion evaluation with symptom category totals, red flags, risk factors, diagnosis, and follow-up plan.",
        "estimatedMinutes": 16,
        "status": "active",
        "sourceFile": "AcuteConcussionEvaluation_ACETest.pdf",
        "sections": sections,
    }


def main():
    forms = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    replacements = {
        "patient-portal-18-plus": portal_form("patient-portal-18-plus", "Patient Portal Access - 18 and Up", "Patient Portal 18 and Up.pdf", adult=True),
        "patient-portal-12-17": portal_form("patient-portal-12-17", "Patient Portal Access - Ages 12-17", "Patient Portal 12-17.pdf", adolescent=True),
        "patient-portal-under-11": portal_form("patient-portal-under-11", "Patient Portal Access - Under 11", "Patient Portal Under 11.pdf"),
        "adult-adhd-asrs": adult_asrs(),
        "wart-consent": wart_consent(),
        "acute-concussion-evaluation": ace_form(),
    }
    updated = [replacements.get(form.get("id"), form) for form in forms]
    TEMPLATE_PATH.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    for form_id, form in replacements.items():
        field_count = sum(len(section.get("fields", [])) for section in form["sections"])
        print(f"Updated {form_id}: {len(form['sections'])} sections, {field_count} fields")


if __name__ == "__main__":
    main()
