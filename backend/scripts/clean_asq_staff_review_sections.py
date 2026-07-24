from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FOLLOW_UP_NOTE_TITLE = "Follow-up flagging"


def is_asq_score_summary(title: str) -> bool:
    return title.startswith("ASQ-3 ") and " Score Summary and Follow-Up" in title


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    notes_removed = 0
    staff_sections: list[tuple[str, str]] = []

    for template in templates:
        for section in template.get("sections", []):
            content = section.get("content", [])
            next_content = [
                item
                for item in content
                if item.get("title") != FOLLOW_UP_NOTE_TITLE
            ]
            notes_removed += len(content) - len(next_content)
            section["content"] = next_content

            title = section.get("title", "")
            if is_asq_score_summary(title):
                section["owner"] = "staff"
                section["staffOnly"] = True
                for field in section.get("fields", []):
                    field["owner"] = "staff"
                    field["staffOnly"] = True
                staff_sections.append((template["id"], title))

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed {notes_removed} follow-up flagging notes.")
    print(f"Marked {len(staff_sections)} ASQ score summary sections staff-only.")
    for template_id, section_title in staff_sections:
        print(f"- {template_id}: {section_title}")


if __name__ == "__main__":
    main()
