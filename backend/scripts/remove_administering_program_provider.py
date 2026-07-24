from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FIELD_ID = "administering_program_provider"
FIELD_LABEL = "Administering program/provider"


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated: list[str] = []

    for template in templates:
        changed = False
        for section in template.get("sections", []):
            fields = section.get("fields", [])
            next_fields = [
                field
                for field in fields
                if not (
                    field.get("id") == FIELD_ID
                    and field.get("label") == FIELD_LABEL
                )
            ]
            if len(next_fields) != len(fields):
                section["fields"] = next_fields
                changed = True

        if changed:
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed {FIELD_LABEL!r} from {len(updated)} templates.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
