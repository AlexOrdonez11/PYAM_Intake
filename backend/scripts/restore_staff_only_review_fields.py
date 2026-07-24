from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"


def should_be_staff_only(field: dict) -> bool:
    field_id = str(field.get("id", "")).lower()
    label = str(field.get("label", "")).lower()
    group_title = str(field.get("groupTitle", "")).lower()

    if group_title == "administered / reviewed by":
        return True
    if field_id in {"epds_reviewed_by", "epds_administered_reviewed_by", "epds_review_date"}:
        return True
    if field_id.startswith("lead_"):
        return True
    if field_id.startswith("mnvfc_") and any(
        token in field_id
        for token in ("staff", "notes", "review", "verified", "processed", "completed_by")
    ):
        return True
    if "staff_notes" in field_id:
        return True
    if "follow_up_actions" in field_id or "referral_reason" in field_id or "rescreen_months" in field_id:
        return True
    if "staff notes" in label or "office coding" in label:
        return True
    return False


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated = 0

    for template in templates:
        for section in template.get("sections", []):
            for field in section.get("fields", []):
                if should_be_staff_only(field):
                    if field.get("owner") != "staff" or field.get("staffOnly") is not True:
                        updated += 1
                    field["owner"] = "staff"
                    field["staffOnly"] = True

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Restored {updated} explicit staff-only review fields.")


if __name__ == "__main__":
    main()
