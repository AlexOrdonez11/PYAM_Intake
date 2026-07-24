import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_FILE = ROOT / "backend" / "data" / "form-templates.json"


YES_NO_UNSURE = ["Yes", "No", "Unsure"]
NO_YES_UNSURE = ["No", "Yes", "Unsure"]
NO_YES = ["No", "Yes"]
FAMILY_CHANGES = ["Move", "Job change", "Separation", "Divorce", "Death in the family", "Any other changes"]


def note(title, text, variant="info"):
    return {"type": "note", "title": title, "text": text, "variant": variant}


def field(field_id, label, field_type="text", options=None, required=False):
    item = {"id": field_id, "label": label, "type": field_type}
    if options is not None:
        item["options"] = options
    if required:
        item["required"] = True
    return item


def topic_field(row_id, label, options):
    return field(f"bf_topics_{row_id}", label, "multicheck", options)


def yes_no_field(field_id, label, options=YES_NO_UNSURE):
    return field(field_id, label, "radio", options)


TOPIC_GRIDS = {
    6: [
        ("ready_for_school", "Ready for School", [
            "Your child's fears about school",
            "After-school care",
            "Talking with your child's teacher",
            "Your child's friends",
            "Bullying",
            "Your child feeling sad",
        ]),
        ("child_and_family", "Your Child and Family", [
            "Family time together",
            "Your child's chores",
            "Your child handling his feelings",
            "Your child being angry",
        ]),
        ("staying_healthy", "Staying Healthy", [
            "Your child's weight",
            "Eating fruits",
            "Eating vegetables",
            "Eating whole grains",
            "Getting enough calcium",
            "1 hour of physical activity per day",
        ]),
        ("healthy_teeth", "Healthy Teeth", [
            "Regular dentist visits",
            "Brushing teeth twice daily",
            "Flossing daily",
        ]),
        ("safety", "Safety", [
            "Street safety",
            "Booster seats",
            "Always wearing safety helmets",
            "Swimming safety",
            "Sunscreen",
            "Preventing sexual abuse",
            "Fire escape and fire drill plan",
            "Carbon monoxide alarms in your home",
            "Gun safety",
        ]),
    ],
    7: [
        ("school", "School", [
            "How your child is learning and doing in school",
            "Bullying",
            "After-school activities and care",
            "Special education needs",
            "How your child acts",
            "Talking with your child's school",
        ]),
        ("growing_child", "Your Growing Child", [
            "How your child feels about herself",
            "Following rules",
            "Getting ready for puberty",
            "Being angry",
            "Your child dealing with his problems",
            "Becoming more independent",
        ]),
        ("staying_healthy", "Staying Healthy", [
            "Your child's weight",
            "1 hour of physical activity daily",
            "Playing sports",
            "TV time",
            "Getting enough calcium",
            "Drinking enough water",
            "How much your child should eat at one time",
        ]),
        ("healthy_teeth", "Healthy Teeth", [
            "Regular dentist visits",
            "Brushing teeth twice daily",
            "Flossing daily",
        ]),
        ("safety", "Safety", [
            "Booster seats",
            "Helmets and sports safety",
            "Swimming safety",
            "Wearing sunscreen",
            "Knowing your child's computer use",
            "Knowing your child's friends and their families",
            "Gun safety",
            "Smoke-free house and cars",
            "Preventing sexual abuse",
        ]),
    ],
    8: [
        ("school", "School", [
            "How your child is learning and doing in school",
            "Bullying",
            "After-school activities and care",
            "Special education needs",
            "How your child acts",
            "Talking with your child's school",
        ]),
        ("growing_child", "Your Growing Child", [
            "How your child feels about herself",
            "Following rules",
            "Getting ready for puberty",
            "Being angry",
            "Your child dealing with his problems",
            "Becoming more independent",
        ]),
        ("staying_healthy", "Staying Healthy", [
            "Your child's weight",
            "1 hour of physical activity daily",
            "Playing sports",
            "TV time",
            "Getting enough calcium",
            "Drinking enough water",
            "How much your child should eat at one time",
        ]),
        ("healthy_teeth", "Healthy Teeth", [
            "Regular dentist visits",
            "Brushing teeth twice daily",
            "Flossing daily",
        ]),
        ("safety", "Safety", [
            "Booster seats",
            "Helmets and sports safety",
            "Swimming safety",
            "Wearing sunscreen",
            "Knowing your child's computer use",
            "Knowing your child's friends and their families",
            "Gun safety",
            "Smoke-free house and cars",
            "Preventing sexual abuse",
        ]),
    ],
    9: [
        ("school", "School", [
            "How your child is doing in school",
            "Homework",
            "Bullying",
        ]),
        ("growing_child", "Your Growing Child", [
            "How your child feels about herself",
            "Dealing with your child's anger",
            "Setting limits for your child",
            "Your child's friends",
            "Readiness for middle school",
            "Your child's sexuality",
            "Puberty",
        ]),
        ("staying_healthy", "Staying Healthy", [
            "Your child's weight",
            "Your child's body image",
            "Eating breakfast",
            "Limiting soft drinks",
            "Eating together as a family",
            "Drinking enough water",
            "Limiting high-fat food",
            "1 hour of physical activity daily",
        ]),
        ("healthy_teeth", "Healthy Teeth", [
            "Regular dentist visits",
            "Brushing teeth twice daily",
            "Flossing daily",
        ]),
        ("safety", "Safety", [
            "Bicycle and sports safety and helmets",
            "Car safety",
            "Swimming safety",
            "Sunscreen",
            "Knowing your child's friends and their families",
            "Preventing cigarette, alcohol, and drug use",
            "Gun safety",
        ]),
    ],
    10: [
        ("school", "School", [
            "How your child is doing in school",
            "Homework",
            "Bullying",
        ]),
        ("growing_child", "Your Growing Child", [
            "How your child feels about herself",
            "Dealing with your child's anger",
            "Setting limits for your child",
            "Your child's friends",
            "Readiness for middle school",
            "Your child's sexuality",
            "Puberty",
        ]),
        ("staying_healthy", "Staying Healthy", [
            "Your child's weight",
            "Your child's body image",
            "Eating breakfast",
            "Limiting soft drinks",
            "Eating together as a family",
            "Drinking enough water",
            "Limiting high-fat food",
            "1 hour of physical activity daily",
        ]),
        ("healthy_teeth", "Healthy Teeth", [
            "Regular dentist visits",
            "Brushing teeth twice daily",
            "Flossing daily",
        ]),
        ("safety", "Safety", [
            "Bicycle and sports safety and helmets",
            "Car safety",
            "Swimming safety",
            "Sunscreen",
            "Knowing your child's friends and their families",
            "Preventing cigarette, alcohol, and drug use",
            "Gun safety",
        ]),
    ],
}


GROWING_CHILD_TASKS = {
    6: [
        "Listens well and follows simple instructions",
        "Names at least 4 colors",
        "Balances on 1 foot",
        "Draws a person with 6 body parts",
        "Counts to 10",
        "Copies squares, triangles",
        "Can tell a story with full sentences",
        "Writes some letters and numbers",
        "Hops, skips, climbs",
        "Ties a knot",
    ],
    7: [
        "Eats healthy meals and snacks",
        "Has friends",
        "Gets along with family",
        "Is doing well in school",
        "Participates in an after-school activity",
        "Is vigorously active for 1 hour a day",
        "Does chores when asked",
    ],
    8: [
        "Eats healthy meals and snacks",
        "Has friends",
        "Is doing well in school",
        "Participates in an after-school activity",
        "Is vigorously active for 1 hour a day",
        "Does chores when asked",
        "Gets along with friends",
    ],
    9: [
        "Eats healthy meals and snacks",
        "Has friends",
        "Is doing well in school",
        "Feels good about himself",
        "Participates in an after-school activity",
        "Is vigorously active for 1 hour a day",
        "Gets along with family",
        "Getting chances to make own decisions",
        "Does an activity really well; describe",
    ],
    10: [
        "Eats healthy meals and snacks",
        "Has friends",
        "Is doing well in school",
        "Feels good about himself",
        "Gets along with family",
        "Participates in an after-school activity",
        "Vigorously exercises for 1 hour a day",
        "Does chores when asked",
        "Getting chances to make own decisions",
        "Does an activity really well; describe",
    ],
}


def vision_hearing_questions(year):
    if year not in {7, 9}:
        return []
    return [
        yes_no_field("bf_vision_concerns", "Do you have concerns about how your child sees?"),
        yes_no_field("bf_vision_screen_failed", "Has your child ever failed a school vision screening test?"),
        yes_no_field("bf_squinting", "Does your child tend to squint?"),
        yes_no_field("bf_speech_concerns", "Do you have concerns about how your child speaks?"),
        yes_no_field("bf_hearing_concerns", "Do you have concerns about how your child hears?"),
        yes_no_field("bf_hearing_noise_phone", "Does your child have trouble hearing with a noisy background or over the telephone?"),
        yes_no_field("bf_conversation_following", "Does your child have trouble following the conversation when 2 or more people are talking at the same time?"),
    ]


def risk_questions(year):
    questions = [
        yes_no_field("bf_family_new_medical_problems", "Have any of your child's relatives developed new medical problems since your last visit? If yes, please describe:"),
    ]
    if year == 6:
        questions.extend([
            yes_no_field("bf_lead_sibling_playmate", "Does your child have a sibling or playmate who has or had lead poisoning?"),
            yes_no_field("bf_lead_pre_1978_home", "Does your child live in or regularly visit a house or child care facility built before 1978 that is being or has recently been renovated or remodeled?"),
            yes_no_field("bf_lead_pre_1950_home", "Does your child live in or regularly visit a house or child care facility built before 1950?"),
        ])
    questions.extend(vision_hearing_questions(year))
    questions.extend([
        yes_no_field("bf_tb_high_risk_birth_country", "Was your child born in a country at high risk for tuberculosis (countries other than the United States, Canada, Australia, New Zealand, or Western Europe)?"),
        yes_no_field("bf_tb_travel_contact", "Has your child traveled (had contact with resident populations) for longer than 1 week to a country at high risk for tuberculosis?"),
        yes_no_field("bf_tb_family_contact", "Has a family member or contact had tuberculosis or a positive tuberculin skin test?"),
        yes_no_field("bf_hiv_infected", "Is your child infected with HIV?"),
        yes_no_field("bf_dyslipidemia_stroke_heart", "Does your child have parents or grandparents who have had a stroke or heart problem before age 55?"),
        yes_no_field("bf_dyslipidemia_parent_cholesterol", "Does your child have a parent with an elevated blood cholesterol (240 mg/dL or higher) or who is taking cholesterol medication?"),
        yes_no_field("bf_anemia_strict_vegetarian", "Does your child eat a strict vegetarian diet?"),
        yes_no_field("bf_anemia_iron_supplement", "If your child is a vegetarian, does your child take an iron supplement?", NO_YES_UNSURE),
        yes_no_field("bf_anemia_iron_rich_foods", "Does your child's diet include iron-rich foods such as meat, eggs, iron-fortified cereals, or beans?", NO_YES_UNSURE),
    ])
    if year == 6:
        questions.extend([
            yes_no_field("bf_oral_cavities", "Does your child have a dentist?", NO_YES_UNSURE),
            yes_no_field("bf_oral_fluoride_water", "Does your child's primary water source contain fluoride?", NO_YES_UNSURE),
        ])
    questions.extend([
        yes_no_field("bf_special_health_care_needs", "Does your child have any special health care needs?", NO_YES),
        field("bf_special_health_care_needs_describe", "If yes, describe", "textarea"),
        field("bf_family_changes", "Have there been any major changes in your family lately?", "multicheck", FAMILY_CHANGES),
        yes_no_field("bf_tobacco_smoke_exposure", "Does your child live with anyone who uses tobacco or spend time in any place where people smoke?", NO_YES),
        yes_no_field("bf_development_learning_behavior_concerns", "Do you have specific concerns about your child's development, learning, or behavior?", NO_YES),
        field("bf_development_learning_behavior_describe", "If yes, describe", "textarea"),
        field("bf_growing_developing_child_tasks", "Check off each of the following that are true for your child.", "multicheck", GROWING_CHILD_TASKS[year]),
    ])
    return questions


def bright_futures_fields(year):
    return [
        field("bf_concerns_today", "Do you have any concerns, questions, or problems that you would like to discuss today?", "textarea"),
        *[topic_field(row_id, label, options) for row_id, label, options in TOPIC_GRIDS[year]],
        *risk_questions(year),
    ]


def update_form(form, year):
    for section in form.get("sections", []):
        if section.get("title", "").startswith("Bright Futures Previsit Questionnaire"):
            section["content"] = [
                note(
                    "What would you like to talk about today?",
                    "We are interested in answering your questions. Please check off the boxes for the topics you would like to discuss the most today.",
                )
            ]
            section["fields"] = bright_futures_fields(year)
            return True
    return False


def main():
    templates = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8"))
    changed = []
    for year in [6, 7, 8, 9, 10]:
        form_id = f"{year}-year-visit"
        for form in templates:
            if form.get("id") == form_id:
                if update_form(form, year):
                    changed.append(form_id)
                break
    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
    print(f"Updated Bright Futures mappings: {', '.join(changed)}")


if __name__ == "__main__":
    main()
