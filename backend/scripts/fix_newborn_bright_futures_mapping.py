from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "newborn-2-5-days"
SECTION_TITLE = "Bright Futures 2 to 5 Day Visit"

FIELD_UPDATES = {
    "visit_concerns": {
        "label": "Do you have any concerns, questions, or problems that you would like to discuss today?",
    },
    "topics_how_you_are_feeling": {
        "label": "How You Are Feeling",
    },
    "topics_getting_used_to_baby": {
        "label": "Getting Used to Your Baby",
    },
    "topics_feeding": {
        "label": "Feeding Your Baby",
        "options": ["Jaundice (skin is yellow)", "Burping", "Breastfeeding", "Formula"],
    },
    "topics_safety": {
        "label": "Safety",
    },
    "topics_baby_care": {
        "label": "Baby Care",
    },
    "family_major_changes": {
        "label": "Other than your baby's birth, have there been any major changes in your family lately?",
        "options": ["Move", "Job change", "Separation", "Divorce", "Death in the family", "Any other changes"],
    },
    "baby_special_health_needs_description": {
        "label": "If yes, describe",
    },
    "family_major_changes_description": {
        "label": "If any other changes, describe",
    },
    "baby_growth_concerns": {
        "label": "Do you have specific concerns about how your baby is growing, learning, or acting?",
    },
    "baby_growth_concerns_description": {
        "label": "If yes, describe",
    },
    "baby_tasks": {
        "label": "Check off each of the tasks that your baby is able to do.",
        "options": ["Eats well", "Follows your face", "Turns and calms to your voice", "Can suck, swallow, and breathe easily"],
    },
}


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    template = next(item for item in templates if item["id"] == FORM_ID)
    section = next(item for item in template["sections"] if item["title"] == SECTION_TITLE)
    updated: list[str] = []

    for field in section.get("fields", []):
        updates = FIELD_UPDATES.get(field.get("id"))
        if not updates:
            continue
        field.update(updates)
        updated.append(field["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Updated {len(updated)} newborn Bright Futures fields.")
    for field_id in updated:
        print(f"- {field_id}")


if __name__ == "__main__":
    main()
