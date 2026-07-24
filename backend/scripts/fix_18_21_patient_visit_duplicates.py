from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "18-21-year-visit"
SECTION_TITLE = "Patient and Visit Information"
MISPLACED_BRIGHT_FUTURES_IDS = {
    "primary_concerns",
    "recent_changes",
    "special_health_needs",
    "special_health_needs_details",
    "tobacco_exposure",
    "tobacco_exposure_details",
    "screen_time_hours",
}


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    template = next(item for item in templates if item["id"] == FORM_ID)
    section = next(item for item in template["sections"] if item["title"] == SECTION_TITLE)

    fields = section.get("fields", [])
    removed = [
        field
        for field in fields
        if field.get("id") in MISPLACED_BRIGHT_FUTURES_IDS
    ]
    section["fields"] = [
        field
        for field in fields
        if field.get("id") not in MISPLACED_BRIGHT_FUTURES_IDS
    ]

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed {len(removed)} misplaced Bright Futures fields from {FORM_ID}.")
    for field in removed:
        print(f"- {field.get('id')}: {field.get('label')}")


if __name__ == "__main__":
    main()
