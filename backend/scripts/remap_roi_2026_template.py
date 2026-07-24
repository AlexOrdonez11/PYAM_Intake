from __future__ import annotations

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "form-templates.json"
FORM_ID = "roi-2026"


def field(field_id: str, label: str, field_type: str = "text", **extra: object) -> dict:
    output = {"id": field_id, "label": label, "type": field_type}
    output.update(extra)
    return output


def note(title: str, text: str | None = None, items: list[str] | None = None, variant: str | None = None) -> dict:
    output = {"type": "note", "title": title}
    if text:
        output["text"] = text
    if items:
        output["items"] = items
    if variant:
        output["variant"] = variant
    return output


def main() -> None:
    templates = json.loads(DATA_PATH.read_text(encoding="utf-8-sig"))
    template = next(item for item in templates if item["id"] == FORM_ID)

    template["description"] = "Authorization for release of medical information mapped from NEW ROI 2026.docx."
    template["estimatedMinutes"] = 10
    template["sections"] = [
        {
            "title": "Patient Information",
            "content": [
                note(
                    "Instructions",
                    "Please complete all sections legibly. Incomplete forms may result in delay or denial of this request.",
                    variant="disclaimer",
                )
            ],
            "fields": [
                field("patient_name", "Patient name"),
                field("date_of_birth", "Date of birth", "date"),
                field("previous_names", "Previous name(s)"),
                field("account_number", "Internal use only - account number", "text", owner="staff", staffOnly=True),
                field("pickup_instructions", "Internal use only - pickup instructions", "textarea", owner="staff", staffOnly=True),
                field("baby_id", "Baby ID", "text", owner="staff", staffOnly=True),
                field("administering_program_provider", "Administering program/provider", "text", owner="staff", staffOnly=True),
            ],
        },
        {
            "title": "Release My Records From",
            "fields": [
                field("source_facility_name", "Facility name"),
                field("source_facility_address", "Address", "textarea"),
                field("source_facility_fax", "Fax"),
            ],
        },
        {
            "title": "Send My Records To",
            "fields": [
                field("recipient_name", "Name"),
                field("recipient_attention", "Attention to"),
                field("recipient_address", "Address", "textarea"),
                field("recipient_city", "City"),
                field("recipient_state", "State"),
                field("recipient_zip", "ZIP"),
                field("recipient_phone", "Phone", "tel"),
                field("recipient_fax", "Fax for continuing care only"),
                field("recipient_email", "Email", "email"),
            ],
            "content": [
                note("Email note", "Only if you want records sent via encrypted email.", variant="disclaimer"),
            ],
        },
        {
            "title": "Types of Records",
            "fields": [
                field("dates_of_service", "Date(s) of service"),
                field(
                    "records",
                    "Types of records",
                    "multicheck",
                    options=[
                        "All health records, not including billing",
                        "Lab reports",
                        "Billing records",
                        "Office notes",
                        "Immunization record",
                        "Mental health records",
                        "Other",
                    ],
                ),
                field("records_other", "Other records", "textarea"),
            ],
        },
        {
            "title": "Reason for Request",
            "fields": [
                field(
                    "purpose",
                    "Reason for request",
                    "multicheck",
                    options=[
                        "Personal use",
                        "Disability",
                        "Insurance",
                        "Legal",
                        "Transfer care",
                        "Continuing care",
                    ],
                ),
            ],
        },
        {
            "title": "Return Completed Forms To",
            "content": [
                note(
                    "Return completed forms to PYAM",
                    items=[
                        "Mail: Pediatric and Young Adult Medicine, 1804 7th Street W., Ste 200, Saint Paul, MN 55116",
                        "Fax: 1-888-891-5871",
                        "Email: medicalrecords@pyam.com",
                        "Drop off: Any PYAM location",
                    ],
                ),
                note(
                    "Processing note",
                    "Records will be mailed to the person(s) identified in section 3. Please allow up to 2 weeks for processing.",
                    variant="warning",
                ),
            ],
            "fields": [],
        },
        {
            "title": "Authorization and Signature",
            "content": [
                note(
                    "I understand that by signing below",
                    items=[
                        "I may revoke this authorization at any time by notifying the facility identified above in writing.",
                        "By authorizing the release of my protected health information, the health information is no longer protected and has the potential to be re-disclosed.",
                        "There may be a fee for release of this information, and I may be responsible for that fee.",
                        "I am authorizing the release of my personal protected health information from any i-Health facility unless otherwise specified above.",
                        "Treatment will not be denied to me if I do not sign this form.",
                        "This authorization will expire one year from the date I sign on this form unless specified.",
                        "i-Health is a multispecialty practice including, and without limitation, the clinic above. Your i-Health record will be released, unless you otherwise specify in writing.",
                    ],
                    variant="disclaimer",
                ),
                note(
                    "Signature requirement",
                    "Electronic typed signatures cannot be accepted on the source ROI form. Confirm clinic policy before accepting an electronic signature for this digital workflow.",
                    variant="warning",
                ),
            ],
            "fields": [
                field("expiration_specified", "Authorization expiration if otherwise specified"),
                field("signature", "Signature", "signature"),
                field("signature_date", "Date", "date"),
                field("print_name", "Print name"),
                field("relationship", "Signer relationship if not patient"),
            ],
        },
        {
            "title": "Original Paper Form",
            "content": [
                {
                    "type": "note",
                    "title": "Original paper form",
                    "text": "For reference, you may open the original paper packet after completing the digital form.",
                    "variant": "disclaimer",
                    "url": "/source-forms/NEW-ROI-2026.docx",
                    "linkLabel": "Open original paper packet",
                }
            ],
            "fields": [],
        },
    ]

    DATA_PATH.write_text(
        json.dumps(templates, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Remapped roi-2026 to NEW ROI 2026.docx sections.")


if __name__ == "__main__":
    main()
