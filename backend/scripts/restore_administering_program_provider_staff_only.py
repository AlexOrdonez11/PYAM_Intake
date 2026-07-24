from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_IDS = {
    "7-8-months-visit",
    "10-months-visit",
    "12-months-visit-eagan",
    "14-months-visit",
}
FIELD = {
    "id": "administering_program_provider",
    "label": "Administering program/provider",
    "type": "text",
    "owner": "staff",
    "staffOnly": True,
}


def insert_before_or_append(fields: list[dict], before_id: str, field: dict) -> bool:
    for existing in fields:
        if existing.get("id") == field["id"]:
            existing.update(field)
            return True

    for index, existing in enumerate(fields):
        if existing.get("id") == before_id:
            fields.insert(index, dict(field))
            return True

    fields.append(dict(field))
    return True


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated: list[str] = []

    for template in templates:
        if template.get("id") not in FORM_IDS:
            continue

        for section in template.get("sections", []):
            if section.get("title") != "Patient and Visit Information":
                continue

            insert_before_or_append(
                section.setdefault("fields", []),
                "program_information_completed_with_family",
                FIELD,
            )
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Restored staff-only administering program/provider in {len(updated)} templates.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
