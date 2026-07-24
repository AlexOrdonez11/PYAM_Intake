from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "well-child-visit"


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    next_templates = [template for template in templates if template.get("id") != FORM_ID]

    DATA_PATH.write_text(
        json.dumps(next_templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Removed {len(templates) - len(next_templates)} {FORM_ID} template.")


if __name__ == "__main__":
    main()
