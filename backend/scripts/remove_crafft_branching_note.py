from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
NOTE_TITLE = "CRAFFT branching"


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    removed = 0
    updated: list[str] = []

    for template in templates:
        changed = False
        for section in template.get("sections", []):
            content = section.get("content", [])
            next_content = [
                item
                for item in content
                if item.get("title") != NOTE_TITLE
            ]
            if len(next_content) != len(content):
                removed += len(content) - len(next_content)
                section["content"] = next_content
                changed = True

        if changed:
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed {removed} CRAFFT branching notes.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
