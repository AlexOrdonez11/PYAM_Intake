from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FIELD_LABEL = "Administering program or provider"


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated: list[str] = []

    for template in templates:
        changed = False
        for section in template.get("sections", []):
            for field in section.get("fields", []):
                if field.get("label") != FIELD_LABEL:
                    continue

                field["owner"] = "staff"
                field["staffOnly"] = True
                changed = True

        if changed:
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Marked {FIELD_LABEL!r} staff-only in {len(updated)} templates.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
