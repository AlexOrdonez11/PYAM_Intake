from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
PHQA_TITLE = "PHQ-9 Modified for Adolescents (PHQ-A)"
OLD_TITLE = "PHQ-A scoring"
INSTRUCTION_NOTE = {
    "type": "note",
    "title": "Instructions",
    "text": (
        "How often have you been bothered by each of the following symptoms during "
        'the past two weeks? For each symptom put an "X" in the box beneath the '
        "answer that best describes how you have been feeling."
    ),
    "variant": "disclaimer",
}


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    updated: list[str] = []

    for template in templates:
        changed = False
        for section in template.get("sections", []):
            if section.get("title") != PHQA_TITLE:
                continue

            content = [
                item
                for item in section.get("content", [])
                if item.get("title") != OLD_TITLE
            ]
            if not any(
                item.get("title") == INSTRUCTION_NOTE["title"]
                and item.get("text") == INSTRUCTION_NOTE["text"]
                for item in content
            ):
                content.insert(0, dict(INSTRUCTION_NOTE))

            if section.get("content", []) != content:
                section["content"] = content
                changed = True

        if changed:
            updated.append(template["id"])

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Updated PHQ-A instructions in {len(updated)} templates.")
    for template_id in updated:
        print(f"- {template_id}")


if __name__ == "__main__":
    main()
