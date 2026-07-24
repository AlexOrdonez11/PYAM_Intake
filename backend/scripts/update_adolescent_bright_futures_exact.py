import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_FILE = ROOT / "backend" / "data" / "form-templates.json"


YES_NO_UNSURE = ["Yes", "No", "Unsure"]
NO_YES_UNSURE = ["No", "Yes", "Unsure"]
NO_YES = ["No", "Yes"]


def note(title, text, variant="info"):
    return {"type": "note", "title": title, "text": text, "variant": variant}


def field(field_id, label, field_type="text", options=None, required=False, owner=None, staff_only=None):
    item = {"id": field_id, "label": label, "type": field_type}
    if options is not None:
        item["options"] = options
    if required:
        item["required"] = True
    if owner is not None:
        item["owner"] = owner
    if staff_only is not None:
        item["staffOnly"] = staff_only
    return item


def radio(field_id, label, options=YES_NO_UNSURE):
    return field(field_id, label, "radio", options)


def topics(field_id, label, options):
    return field(field_id, label, "multicheck", options)


PARENT_GROWING = [
    "My child engages in behavior that supports a healthy lifestyle, such as eating healthy foods, being active, and keeping herself safe.",
    "My child has at least one responsible adult in his life who cares about him and to whom he can go to if he needs help.",
    "My child has at least one friend or a group of friends with whom she is comfortable.",
    "My child helps others individually or by working with a group in school, a faith-based organization, or the community.",
    "My child is able to bounce back from life's disappointments.",
    "My child has a sense of hopefulness and self-confidence.",
    "My child has become more independent and made more of his own decisions as he has become older.",
    "My child is particularly good at doing a certain thing like math, soccer, theater, cooking, or hunting.",
]


PATIENT_GROWING = [
    "I engage in behavior that supports a healthy lifestyle, such as eating healthy foods, being active, and keeping myself safe.",
    "I feel I have at least one responsible adult in my life who cares about me and who I can go to if I need help.",
    "I feel like I have at least one friend or a group of friends with whom I am comfortable.",
    "I help others on my own or by working with a group in school, a faith-based organization, or the community.",
    "I am able to bounce back from life's disappointments.",
    "I have a sense of hopefulness and self-confidence.",
    "I have become more independent and made more of my own decisions as I have become older.",
    "I feel that I am particularly good at doing a certain thing like math, soccer, theater, cooking, or hunting.",
]


def parent_bright_futures_fields(prefix):
    return [
        field(f"{prefix}_parent_concerns", "Do you have any concerns, questions, or problems that you would like to discuss today?", "textarea"),
        field(f"{prefix}_parent_home_changes", "What changes or challenges have there been at home since last year?", "textarea"),
        radio(f"{prefix}_parent_special_health_care_needs", "Does your child have any special health care needs?", NO_YES),
        field(f"{prefix}_parent_special_health_care_needs_describe", "If yes, describe", "textarea"),
        radio(f"{prefix}_parent_tobacco_exposure", "Does your child live with anyone who uses tobacco or spend time in any place where people smoke?", NO_YES),
        field(f"{prefix}_parent_tobacco_exposure_describe", "If yes, describe", "textarea"),
        field(f"{prefix}_parent_screen_time_hours", "How many hours per day does your child watch TV, play video games, and use the computer (not for schoolwork)?", "text"),
        radio(f"{prefix}_parent_vision_blackboard", "Does your child complain that the blackboard has become difficult to see?"),
        radio(f"{prefix}_parent_vision_failed_screen", "Has your child ever failed a school vision screening test?"),
        radio(f"{prefix}_parent_vision_books_close", "Does your child hold books close to read?"),
        radio(f"{prefix}_parent_vision_faces_distance", "Does your child have trouble recognizing faces at a distance?"),
        radio(f"{prefix}_parent_vision_squint", "Does your child tend to squint?"),
        radio(f"{prefix}_parent_hearing_phone", "Does your child have a problem hearing over the telephone?"),
        radio(f"{prefix}_parent_hearing_conversation", "Does your child have trouble following the conversation when 2 or more people are talking at the same time?"),
        radio(f"{prefix}_parent_hearing_noise", "Does your child have trouble hearing with a noisy background?"),
        radio(f"{prefix}_parent_hearing_repeat", "Does your child ask people to repeat themselves?"),
        radio(f"{prefix}_parent_hearing_misunderstand", "Does your child misunderstand what others are saying and respond inappropriately?"),
        radio(f"{prefix}_parent_tb_birth_country", "Was your child born in a country at high risk for tuberculosis (countries other than the United States, Canada, Australia, New Zealand, or Western Europe)?"),
        radio(f"{prefix}_parent_tb_travel", "Has your child traveled (had contact with resident populations) for longer than 1 week to a country at high risk for tuberculosis?"),
        radio(f"{prefix}_parent_tb_contact", "Has a family member or contact had tuberculosis or a positive tuberculin skin test?"),
        radio(f"{prefix}_parent_hiv", "Is your child infected with HIV?"),
        radio(f"{prefix}_parent_dyslipidemia_family", "Does your child have parents or grandparents who have had a stroke or heart problem before age 55?"),
        radio(f"{prefix}_parent_dyslipidemia_parent_cholesterol", "Does your child have a parent with an elevated blood cholesterol (240 mg/dL or higher) or who is taking cholesterol medication?"),
        radio(f"{prefix}_parent_anemia_iron_foods", "Does your child's diet include iron-rich foods such as meat, eggs, iron-fortified cereals, or beans?", NO_YES_UNSURE),
        radio(f"{prefix}_parent_anemia_iron_deficiency", "Has your child ever been diagnosed with iron deficiency anemia?"),
        radio(f"{prefix}_parent_female_menstrual_bleeding", "For females only: Does your child have excessive menstrual bleeding or other blood loss?"),
        radio(f"{prefix}_parent_female_period_over_5_days", "For females only: Does your child's period last more than 5 days?"),
        topics(f"{prefix}_parent_growing_developing", "Check off all of the items that you feel are true for your child.", PARENT_GROWING),
        field(f"{prefix}_parent_strengths_describe", "Describe what your child is particularly good at, if applicable", "textarea"),
    ]


EARLY_ADOLESCENT_TOPICS = [
    ("body", "Your Growing and Changing Body", [
        "Teeth",
        "Appearance or body image",
        "How you feel about yourself",
        "Healthy eating",
        "Good ways to be active",
        "How your body is changing",
        "Your weight",
    ]),
    ("school_friends", "School and Friends", [
        "Your relationship with your family",
        "Your friends",
        "How you are doing in school",
        "Girlfriend or boyfriend",
        "Organizing your time to get things done",
    ]),
    ("feelings", "How You Are Feeling", [
        "Dealing with stress",
        "Keeping under control",
        "Sexuality",
        "Feeling sad",
        "Feeling anxious",
        "Feeling irritable",
    ]),
    ("behavior_choices", "Healthy Behavior Choices", [
        "Smoking cigarettes",
        "Drinking alcohol",
        "Using drugs",
        "Pregnancy",
        "Sexually transmitted infections (STIs)",
        "Decisions about sex and drugs",
    ]),
    ("violence_injuries", "Violence and Injuries", [
        "Car safety",
        "Using a helmet or protective gear",
        "Keeping yourself safe in a risky situation",
        "Gun safety",
        "Bullying or trouble with other kids",
        "Not riding in a car with a drinking driver",
    ]),
]


OLDER_ADOLESCENT_TOPICS = [
    ("body", "Your Growing and Changing Body", [
        "How your body is changing",
        "Teeth",
        "Appearance or body image",
        "How you feel about yourself",
        "Healthy eating",
        "Good ways to keep active",
        "Protecting your ears from loud noise",
    ]),
    ("school_friends", "School and Friends", [
        "Your relationship with your family",
        "Your friends",
        "Girlfriend or boyfriend",
        "How you are doing in school",
        "Organizing your time to get things done",
        "Plans after high school",
    ]),
    ("feelings", "How You Are Feeling", [
        "Dealing with stress",
        "Keeping under control",
        "Sexuality",
        "Feeling sad",
        "Feeling anxious",
        "Feeling irritable",
        "Keeping a positive attitude",
    ]),
    ("behavior_choices", "Healthy Behavior Choices", [
        "Pregnancy",
        "Sexually transmitted infections (STIs)",
        "Smoking cigarettes",
        "Drinking alcohol",
        "Using drugs",
        "How to avoid risky situations",
        "Decisions about sex, alcohol, and drugs",
        "How to support friends who don't use alcohol and drugs",
        "How to follow through with decisions you have made about sex, alcohol, and drugs",
    ]),
    ("violence_injuries", "Violence and Injuries", [
        "Car safety",
        "Using a helmet",
        "Driving rules for new teen drivers",
        "Gun safety",
        "Dating violence or abuse",
        "Bullying or trouble with other kids",
        "Keeping yourself and your friends safe in risky situations",
    ]),
]


def patient_bright_futures_fields(prefix, older=False):
    topic_rows = OLDER_ADOLESCENT_TOPICS if older else EARLY_ADOLESCENT_TOPICS
    items = [
        field(f"{prefix}_patient_concerns", "Do you have any concerns, questions, or problems that you would like to discuss today?", "textarea"),
        field(f"{prefix}_patient_home_changes", "What changes or challenges have there been at home since last year?", "textarea"),
    ]
    if older:
        items.extend([
            radio(f"{prefix}_patient_special_health_care_needs", "Do you have any special health care needs?"),
            field(f"{prefix}_patient_special_health_care_needs_describe", "If yes or unsure, describe", "textarea"),
        ])
    items.extend([
        radio(f"{prefix}_patient_tobacco_exposure", "Do you live with anyone who uses tobacco or spend time in any place where people smoke?", NO_YES),
        field(f"{prefix}_patient_tobacco_exposure_describe", "If yes, describe", "textarea"),
    ])
    if older:
        items.append(field(f"{prefix}_patient_screen_time_hours", "How many hours per day do you watch TV, play video games, and use the computer (not for schoolwork)?", "text"))
    items.extend([topics(f"{prefix}_topics_{row_id}", label, options) for row_id, label, options in topic_rows])
    if older:
        items.extend([
            radio(f"{prefix}_patient_vision_blackboard", "Do you complain that the blackboard has become difficult to see?"),
            radio(f"{prefix}_patient_vision_failed_screen", "Have you ever failed a school vision screening test?"),
            radio(f"{prefix}_patient_vision_books_close", "Do you hold books close to your eyes to read?"),
            radio(f"{prefix}_patient_vision_faces_distance", "Do you have trouble recognizing faces at a distance?"),
            radio(f"{prefix}_patient_vision_squint", "Do you tend to squint?"),
            radio(f"{prefix}_patient_hearing_phone", "Do you have a problem hearing over the telephone?"),
            radio(f"{prefix}_patient_hearing_conversation", "Do you have trouble following the conversation when 2 or more people are talking at the same time?"),
            radio(f"{prefix}_patient_hearing_noise", "Do you have trouble hearing with a noisy background?"),
            radio(f"{prefix}_patient_hearing_repeat", "Do you find yourself asking people to repeat themselves?"),
            radio(f"{prefix}_patient_hearing_misunderstand", "Do you misunderstand what others are saying and respond inappropriately?"),
            radio(f"{prefix}_patient_tb_birth_country", "Were you born in a country at high risk for tuberculosis (countries other than the United States, Canada, Australia, New Zealand, or Western Europe)?"),
            radio(f"{prefix}_patient_tb_travel", "Have you traveled (had contact with resident populations) for longer than 1 week to a country at high risk for tuberculosis?"),
            radio(f"{prefix}_patient_tb_contact", "Has a family member or contact had tuberculosis or a positive tuberculin skin test?"),
            radio(f"{prefix}_patient_tb_incarcerated", "Have you ever been incarcerated (in jail)?"),
            radio(f"{prefix}_patient_hiv", "Are you infected with HIV?"),
            radio(f"{prefix}_patient_dyslipidemia_family", "Do you have parents or grandparents who have had a stroke or heart problem before age 55?"),
            radio(f"{prefix}_patient_dyslipidemia_parent_cholesterol", "Do you have a parent with an elevated blood cholesterol (240 mg/dL or higher) or who is taking cholesterol medication?"),
        ])
    items.extend([
        radio(f"{prefix}_patient_smokes", "Do you smoke cigarettes?"),
        radio(f"{prefix}_patient_alcohol_ever", "Have you ever had an alcoholic drink?"),
        radio(f"{prefix}_patient_drug_ever", "Have you ever used marijuana or any other drug to get high?"),
    ])
    if older:
        items.append(radio(f"{prefix}_patient_injectable_drugs", "Do you now use or have you ever used injectable drugs?"))
    items.extend([
        radio(f"{prefix}_patient_sex_ever", "Have you ever had sex (including intercourse or oral sex)?"),
        radio(f"{prefix}_patient_anemia_iron_foods", "Does your diet include iron-rich foods such as meat, eggs, iron-fortified cereals, or beans?", NO_YES_UNSURE),
        radio(f"{prefix}_patient_anemia_iron_deficiency", "Have you ever been diagnosed with iron deficiency anemia?"),
        radio(f"{prefix}_patient_female_menstrual_bleeding", "For females only: Do you have excessive menstrual bleeding or other blood loss?"),
        radio(f"{prefix}_patient_female_period_over_5_days", "For females only: Does your period last more than 5 days?"),
    ])
    if older:
        items.extend([
            radio(f"{prefix}_patient_female_sex_ever", "For females only: Have you ever had sex (including intercourse or oral sex)? If no, skip to Growing and Developing."),
            radio(f"{prefix}_patient_female_partner_hiv_idu", "For females only: Have any of your past or current sex partners been infected with HIV, bisexual, or injection drug users?"),
            radio(f"{prefix}_patient_female_sti_treated", "For females only: Have you ever been treated for a sexually transmitted infection?"),
            radio(f"{prefix}_patient_female_unprotected_multiple", "For females only: Are you having unprotected sex with multiple partners?"),
            radio(f"{prefix}_patient_female_trade_sex", "For females only: Do you trade sex for money or drugs or have sex partners who do?"),
            radio(f"{prefix}_patient_cervical_dysplasia_first_sex_gt_3_years", "For females only: Was your first time having sexual intercourse more than 3 years ago?"),
            radio(f"{prefix}_patient_pregnancy_no_birth_control", "For females only: Have you been sexually active without using birth control?"),
            radio(f"{prefix}_patient_pregnancy_late_missed_period", "For females only: Have you been sexually active and had a late or missed period within the last 2 months?"),
            radio(f"{prefix}_patient_male_sex_ever", "For males only: Have you ever had sex (including intercourse or oral sex)? If no, skip to Growing and Developing."),
            radio(f"{prefix}_patient_male_sti_treated", "For males only: Have you ever been treated for a sexually transmitted infection?"),
            radio(f"{prefix}_patient_male_unprotected_multiple", "For males only: Are you having unprotected sex with multiple partners?"),
            radio(f"{prefix}_patient_male_sex_with_men", "For males only: Have you ever had sex with other men?"),
            radio(f"{prefix}_patient_male_trade_sex", "For males only: Do you trade sex for money or drugs or have sex partners who do?"),
            radio(f"{prefix}_patient_male_partner_hiv_idu", "For males only: Have any of your past or current sex partners been infected with HIV, bisexual, or injection drug users?"),
        ])
    items.extend([
        topics(f"{prefix}_patient_growing_developing", "Check off all of the items that you feel are true for you.", PATIENT_GROWING),
        field(f"{prefix}_patient_strengths_describe", "Describe what you are particularly good at, if applicable", "textarea"),
    ])
    return items


def update_adolescent_form(form, prefix):
    changed = False
    for section in form.get("sections", []):
        title = section.get("title", "")
        if "Older Child / Early Adolescent Visits (Parent)" in title:
            section["content"] = [
                note(
                    "What would you like to talk about today?",
                    "For us to provide your child with the best possible health care, please tell us how things are going and answer the screening questions below.",
                )
            ]
            section["fields"] = parent_bright_futures_fields(prefix)
            changed = True
        elif "Early Adolescent Visits" in title:
            section["content"] = [
                note(
                    "What would you like to talk about today?",
                    "Our discussions with you are private unless we are concerned that someone is in danger.",
                )
            ]
            section["fields"] = patient_bright_futures_fields(prefix, older=False)
            changed = True
    return changed


def update_older_form(form, prefix):
    for section in form.get("sections", []):
        if section.get("title", "").startswith("Bright Futures Previsit Questionnaire"):
            section["content"] = [
                note(
                    "What would you like to talk about today?",
                    "Our discussions with you are private unless we are concerned that someone is in danger. Please check the topics you would like to discuss and answer the questions below.",
                )
            ]
            section["fields"] = patient_bright_futures_fields(prefix, older=True)
            return True
    return False


def loosen_mnvfc_fields(form):
    changed = False
    patient_ids = {"mnvfc_screening_date", "mnvfc_birth_date", "mnvfc_patient", "mnvfc_patient_name", "mnvfc_parent_guardian", "mnvfc_eligibility", "mnvfc_subsequent_visit_dates"}
    for section in form.get("sections", []):
        if "MnVFC" not in section.get("title", ""):
            continue
        for item in section.get("fields", []):
            if item.get("id") in patient_ids:
                item["owner"] = "patient"
                item["staffOnly"] = False
                changed = True
    return changed


def polish_blood_lead_section(form):
    changed = False
    for section in form.get("sections", []):
        if section.get("title") != "Blood Lead Report Form":
            continue
        section["content"] = [
            note(
                "Minnesota blood lead report",
                "Complete the patient, specimen, lab, and clinician details needed for blood lead reporting.",
                "info",
            )
        ]
        changed = True
    return changed


def main():
    templates = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8-sig"))
    changed = []
    for form in templates:
        form_id = form.get("id")
        if form_id in {"11-year-visit", "12-year-visit", "13-14-year-visit"}:
            if update_adolescent_form(form, form_id.replace("-visit", "").replace("-", "_")):
                changed.append(form_id)
        elif form_id in {"15-17-year-visit", "18-21-year-visit"}:
            if update_older_form(form, form_id.replace("-visit", "").replace("-", "_")):
                changed.append(form_id)
        if loosen_mnvfc_fields(form) and form_id not in changed:
            changed.append(form_id)
        if polish_blood_lead_section(form) and form_id not in changed:
            changed.append(form_id)

    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
    print("Updated adolescent Bright Futures / MnVFC mappings:")
    for form_id in changed:
        print(f"- {form_id}")


if __name__ == "__main__":
    main()
