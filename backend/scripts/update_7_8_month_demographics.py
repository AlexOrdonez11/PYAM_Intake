from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "7-8-months-visit"
SECTION_TITLE = "Patient and Visit Information"


def insert_after(fields: list[dict], after_id: str, field: dict) -> bool:
    if any(existing.get("id") == field["id"] for existing in fields):
        return False

    for index, existing in enumerate(fields):
        if existing.get("id") == after_id:
            fields.insert(index + 1, field)
            return True

    fields.append(field)
    return True


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    template = next(item for item in templates if item["id"] == FORM_ID)
    section = next(item for item in template["sections"] if item["title"] == SECTION_TITLE)
    fields = section["fields"]

    before = len(fields)
    section["fields"] = [
        field
        for field in fields
        if field.get("id") != "program_information_follow_up_needed"
    ]
    fields = section["fields"]
    removed = before - len(fields)

    email_added = insert_after(
        fields,
        "phone",
        {
            "id": "email",
            "label": "Email",
            "type": "email",
        },
    )
    helpers_added = insert_after(
        fields,
        "person_filling_out_questionnaire",
        {
            "id": "people_assisting_questionnaire",
            "label": "Names of people assisting with filling out this questionnaire",
            "type": "textarea",
        },
    )

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed follow-up needed fields: {removed}")
    print(f"Added email field: {email_added}")
    print(f"Added assisting names field: {helpers_added}")


if __name__ == "__main__":
    main()
