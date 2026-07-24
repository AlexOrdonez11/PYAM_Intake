from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
OLD_TITLE = "Eligibility review"
OLD_TEXT = "Staff should confirm current MnVFC eligibility rules before administering vaccine from program stock."
NEW_TITLE = "Eligibility note"
NEW_TEXT = "Check only one eligibility category for children 18 years of age or younger."


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated: list[str] = []

    for template in templates:
        changed = False
        for section in template.get("sections", []):
            if section.get("title") != "MnVFC Eligibility Screening":
                continue

            for item in section.get("content", []):
                if item.get("title") == OLD_TITLE and item.get("text") == OLD_TEXT:
                    item["title"] = NEW_TITLE
                    item["text"] = NEW_TEXT
                    changed = True

        if changed:
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Normalized MnVFC eligibility notes in {len(updated)} templates.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
