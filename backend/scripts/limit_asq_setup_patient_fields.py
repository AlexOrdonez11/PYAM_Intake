from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
DATE_LABEL = "Date ASQ completed"
STAFF_DEMOGRAPHIC_IDS = {"baby_id", "administering_program_provider"}


def is_asq_setup_section(section: dict) -> bool:
    title = section.get("title", "")
    return title.startswith("ASQ-3 ") and "Questionnaire Setup" in title


def is_asq_setup_field(field: dict) -> bool:
    field_id = str(field.get("id", ""))
    if not field_id.startswith("asq"):
        return False
    return (
        field_id.endswith("_completed_date")
        or field_id.endswith("_return_by")
        or field_id.endswith("_prematurity_adjusted")
        or field_id.endswith("_notes")
    )


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated_sections: list[tuple[str, str]] = []
    staff_only_fields = 0

    for template in templates:
        for section in template.get("sections", []):
            changed = False
            for field in section.get("fields", []):
                if not (is_asq_setup_section(section) or is_asq_setup_field(field)):
                    continue

                if not is_asq_setup_field(field):
                    continue

                if field.get("label") == DATE_LABEL:
                    field["owner"] = "patient"
                    field["staffOnly"] = False
                    changed = True
                    continue

                if not (field.get("owner") == "staff" and field.get("staffOnly") is True):
                    staff_only_fields += 1
                field["owner"] = "staff"
                field["staffOnly"] = True
                changed = True

            if changed:
                updated_sections.append((template["id"], section.get("title", "")))

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Updated {len(updated_sections)} ASQ setup sections.")
    print(f"Marked {staff_only_fields} setup fields staff-only.")
    for template_id, title in updated_sections:
        print(f"- {template_id}: {title}")


if __name__ == "__main__":
    main()
