import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_FILE = ROOT / "backend" / "data" / "form-templates.json"


def set_group(fields, group_title):
    for field in fields:
        field["groupTitle"] = group_title
        field.pop("groupDescription", None)
        field.pop("groupVariant", None)


def main():
    templates = json.loads(TEMPLATES_FILE.read_text(encoding="utf-8-sig"))
    form = next(item for item in templates if item.get("id") == "1-month-visit")
    sections = form.get("sections", [])

    bright_futures = next(section for section in sections if section.get("title") == "Bright Futures 1 month previsit questionnaire")
    questions = next((section for section in sections if section.get("title") == "Questions About Your Baby"), None)
    growing = next((section for section in sections if section.get("title") == "Your Growing and Developing Baby"), None)

    if questions is None and growing is None:
        TEMPLATES_FILE.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
        print("1 Month Bright Futures sub-sections already use internal headers.")
        return

    question_fields = questions.get("fields", []) if questions else []
    growing_fields = growing.get("fields", []) if growing else []

    if question_fields:
        question_fields[0]["groupTitle"] = "Questions About Your Baby"
        question_fields[0].pop("groupDescription", None)
        question_fields[0].pop("groupVariant", None)
    if growing_fields:
        set_group(growing_fields, "Your Growing and Developing Baby")

    existing_ids = {field.get("id") for field in bright_futures.get("fields", [])}
    merged_fields = list(bright_futures.get("fields", []))
    merged_fields.extend(field for field in question_fields if field.get("id") not in existing_ids)
    existing_ids.update(field.get("id") for field in question_fields)
    merged_fields.extend(field for field in growing_fields if field.get("id") not in existing_ids)
    bright_futures["fields"] = merged_fields

    form["sections"] = [
        section for section in sections
        if section.get("title") not in {"Questions About Your Baby", "Your Growing and Developing Baby"}
    ]

    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2) + "\n", encoding="utf-8")
    print("Merged 1 Month Bright Futures sub-sections into internal headers.")


if __name__ == "__main__":
    main()
