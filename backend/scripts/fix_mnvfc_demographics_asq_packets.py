from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
EXTENDED_DEMOGRAPHIC_FORMS = {
    "7-8-months-visit",
    "10-months-visit",
    "12-months-visit-eagan",
    "14-months-visit",
}
ASQ_ONLY_PACKET_FORMS = {"15-months-visit", "18-months-visit"}


def insert_after(fields: list[dict], after_id: str, field: dict) -> bool:
    for existing in fields:
        if existing.get("id") == field["id"]:
            return False

    for index, existing in enumerate(fields):
        if existing.get("id") == after_id:
            fields.insert(index + 1, field)
            return True

    fields.append(field)
    return True


def normalize_mnvfc(section: dict) -> bool:
    changed = False
    for field in section.get("fields", []):
        if field.get("id") != "mnvfc_eligibility":
            continue
        if field.get("type") != "select":
            field["type"] = "select"
            changed = True
    return changed


def normalize_extended_demographics(section: dict) -> bool:
    fields = section.setdefault("fields", [])
    before = json.dumps(fields, sort_keys=True)

    section["fields"] = [
        field
        for field in fields
        if field.get("id") != "program_information_follow_up_needed"
    ]
    fields = section["fields"]

    insert_after(
        fields,
        "phone",
        {
            "id": "email",
            "label": "Email",
            "type": "email",
        },
    )
    insert_after(
        fields,
        "person_filling_out_questionnaire",
        {
            "id": "people_assisting_questionnaire",
            "label": "Names of people assisting with filling out this questionnaire",
            "type": "textarea",
        },
    )

    return json.dumps(fields, sort_keys=True) != before


def remove_non_source_asq_packet_fields(section: dict) -> bool:
    fields = section.get("fields", [])
    next_fields = [
        field
        for field in fields
        if field.get("id") not in {"special_health_needs", "special_health_needs_details"}
    ]
    if len(next_fields) == len(fields):
        return False
    section["fields"] = next_fields
    return True


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    mnvfc_updates: list[str] = []
    demographic_updates: list[str] = []
    packet_updates: list[str] = []

    for template in templates:
        template_id = template["id"]
        for section in template.get("sections", []):
            title = section.get("title")

            if title == "MnVFC Eligibility Screening" and normalize_mnvfc(section):
                mnvfc_updates.append(template_id)

            if (
                template_id in EXTENDED_DEMOGRAPHIC_FORMS
                and title == "Patient and Visit Information"
                and normalize_extended_demographics(section)
            ):
                demographic_updates.append(template_id)

            if (
                template_id in ASQ_ONLY_PACKET_FORMS
                and title == "Patient and Visit Information"
                and remove_non_source_asq_packet_fields(section)
            ):
                packet_updates.append(template_id)

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"MnVFC select updates: {sorted(set(mnvfc_updates))}")
    print(f"Extended demographic updates: {sorted(set(demographic_updates))}")
    print(f"ASQ packet field removals: {sorted(set(packet_updates))}")


if __name__ == "__main__":
    main()
