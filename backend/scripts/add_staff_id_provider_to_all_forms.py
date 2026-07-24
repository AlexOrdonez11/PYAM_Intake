from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"

DEMOGRAPHIC_SECTION_TITLES = {
    "Patient and Visit Information",
    "Patient Information",
    "Patient",
    "Child",
    "Child and Parent Information",
    "Child and Rater Information",
    "Student and Teacher Information",
    "Patient and Injury Information",
}

BABY_ID_FIELD = {
    "id": "baby_id",
    "label": "Baby ID",
    "type": "text",
    "owner": "staff",
    "staffOnly": True,
}

PROVIDER_FIELD = {
    "id": "administering_program_provider",
    "label": "Administering program/provider",
    "type": "text",
    "owner": "staff",
    "staffOnly": True,
}


def demographic_section(template: dict) -> dict | None:
    for section in template.get("sections", []):
        if section.get("title") in DEMOGRAPHIC_SECTION_TITLES:
            return section
    sections = template.get("sections", [])
    return sections[0] if sections else None


def staff_field(field: dict, source: dict) -> dict:
    next_field = dict(field)
    next_field["id"] = source["id"]
    next_field["label"] = source["label"]
    next_field["type"] = source["type"]
    next_field["owner"] = "staff"
    next_field["staffOnly"] = True
    return next_field


def upsert_staff_field(fields: list[dict], field: dict, after_ids: tuple[str, ...]) -> bool:
    for index, existing in enumerate(fields):
        if existing.get("id") == field["id"]:
            fields[index] = staff_field(existing, field)
            return True

    insert_index = None
    for index, existing in enumerate(fields):
        if existing.get("id") in after_ids:
            insert_index = index + 1

    if insert_index is None:
        insert_index = len(fields)

    fields.insert(insert_index, dict(field))
    return True


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated: list[str] = []

    for template in templates:
        section = demographic_section(template)
        if not section:
            continue

        fields = section.setdefault("fields", [])

        for index, existing in enumerate(list(fields)):
            if existing.get("id") == "child_id":
                fields[index] = staff_field(existing, BABY_ID_FIELD)

        before = json.dumps(fields, sort_keys=True)
        upsert_staff_field(
            fields,
            BABY_ID_FIELD,
            ("clinic_location", "visit_date", "visit_age", "account_number", "phone", "patient_email"),
        )
        upsert_staff_field(
            fields,
            PROVIDER_FIELD,
            ("baby_id", "patient_id", "account_number"),
        )

        if json.dumps(fields, sort_keys=True) != before:
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Updated staff ID/provider fields in {len(updated)} templates.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
