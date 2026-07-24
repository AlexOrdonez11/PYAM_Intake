from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "newborn-2-5-days"
BRIGHT_FUTURES_TITLE = "Bright Futures 2 to 5 Day Visit"
PHQ2_TITLE = "Caregiver Mood - PHQ-2"


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    template = next(item for item in templates if item["id"] == FORM_ID)
    sections = template["sections"]
    bright_futures = next(section for section in sections if section["title"] == BRIGHT_FUTURES_TITLE)
    phq2 = next((section for section in sections if section["title"] == PHQ2_TITLE), None)

    if not phq2:
        print("No separate PHQ-2 section found.")
        return

    fields = bright_futures.setdefault("fields", [])
    existing_ids = {field.get("id") for field in fields}
    phq2_fields = []
    for field in phq2.get("fields", []):
        if field.get("id") in existing_ids:
            continue
        next_field = dict(field)
        next_field["groupTitle"] = "Over the past 2 weeks"
        if next_field.get("id") == "phq2_total_score":
            next_field["owner"] = "staff"
            next_field["staffOnly"] = True
            next_field["groupTitle"] = "Calculated Score"
        phq2_fields.append(next_field)

    insert_after = "family_major_changes_description"
    insert_index = len(fields)
    for index, field in enumerate(fields):
        if field.get("id") == insert_after:
            insert_index = index + 1
            break
    fields[insert_index:insert_index] = phq2_fields

    template["sections"] = [
        section for section in sections if section.get("title") != PHQ2_TITLE
    ]

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Moved {len(phq2_fields)} PHQ-2 fields into Bright Futures.")
    print(f"Removed section: {PHQ2_TITLE}")


if __name__ == "__main__":
    main()
