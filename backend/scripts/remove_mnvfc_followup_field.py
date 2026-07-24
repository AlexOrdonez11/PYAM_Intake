from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FIELD_ID = "mnvfc_subsequent_visit_dates"


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    removed: list[str] = []

    for template in templates:
        for section in template.get("sections", []):
            if section.get("title") != "MnVFC Eligibility Screening":
                continue

            fields = section.get("fields", [])
            next_fields = [field for field in fields if field.get("id") != FIELD_ID]
            if len(next_fields) != len(fields):
                section["fields"] = next_fields
                removed.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed {FIELD_ID} from {len(removed)} templates.")
    for template_id in removed:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
