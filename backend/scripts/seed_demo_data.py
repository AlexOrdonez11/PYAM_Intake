from __future__ import annotations

import json
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import bcrypt
from dotenv import load_dotenv
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.db_schema import ensure_database_schema, seed_form_templates  # noqa: E402


DEMO_PASSWORD = os.getenv("PYAM_DEMO_STAFF_PASSWORD") or secrets.token_urlsafe(18)

STAFF_USERS = [
    {
        "id": "demo-admin",
        "email": "admin.demo@example.com",
        "name": "Priya Admin",
        "role": "admin",
        "title": "Clinic Administrator",
        "clinicLocation": "Maplewood",
    },
    {
        "id": "demo-staff",
        "email": "demo.staff@example.com",
        "name": "Jordan Staff",
        "role": "staff",
        "title": "Intake Coordinator",
        "clinicLocation": "Maplewood",
    },
    {
        "id": "demo-nurse-maplewood",
        "email": "nurse.maplewood@example.com",
        "name": "Marisol Reyes",
        "role": "staff",
        "title": "Registered Nurse",
        "clinicLocation": "Maplewood",
    },
    {
        "id": "demo-frontdesk-eagan",
        "email": "frontdesk.eagan@example.com",
        "name": "Sam Patel",
        "role": "staff",
        "title": "Front Desk",
        "clinicLocation": "Eagan",
    },
    {
        "id": "demo-provider",
        "email": "provider.demo@example.com",
        "name": "Dr. Elena Brooks",
        "role": "staff",
        "title": "Pediatrician",
        "clinicLocation": "Maplewood",
    },
    {
        "id": "demo-care-coordinator",
        "email": "care.demo@example.com",
        "name": "Avery Chen",
        "role": "staff",
        "title": "Care Coordinator",
        "clinicLocation": "Eagan",
    },
]

PATIENTS = [
    ("patient-maya-demo", "Maya Demo", "2026-01-08", "maya.guardian@example.com", "651-555-0101"),
    ("patient-leo-maple", "Leo Maple Demo", "2025-07-08", "leo.guardian@example.com", "651-555-0102"),
    ("patient-nora-followup", "Nora Followup Demo", "2025-05-08", "nora.guardian@example.com", "651-555-0103"),
    ("patient-oliver-two", "Oliver Two Demo", "2024-07-08", "oliver.guardian@example.com", "651-555-0104"),
    ("patient-avery-teen", "Avery Teen Demo", "2012-10-16", "avery.guardian@example.com", "651-555-0105"),
    ("patient-sophia-four", "Sophia Four Demo", "2022-06-18", "sophia.guardian@example.com", "651-555-0106"),
    ("patient-mateo-six", "Mateo Six Demo", "2020-09-28", "mateo.guardian@example.com", "651-555-0107"),
    ("patient-emma-eight", "Emma Eight Demo", "2018-02-21", "emma.guardian@example.com", "651-555-0108"),
    ("patient-jackson-ten", "Jackson Ten Demo", "2016-03-04", "jackson.guardian@example.com", "651-555-0109"),
    ("patient-lily-twelve", "Lily Twelve Demo", "2014-11-12", "lily.guardian@example.com", "651-555-0110"),
    ("patient-henry-portal", "Henry Portal Demo", "2010-05-15", "henry.patient@example.com", "651-555-0111"),
    ("patient-isabella-acute", "Isabella Records Demo", "2019-08-30", "isabella.guardian@example.com", "651-555-0112"),
]

SUBMISSION_BLUEPRINTS = [
    ("mock-asq-6m-mixed", "patient-maya-demo", "6-months-visit", "new", "mixed-asq", 1),
    ("mock-asq-12m-maplewood", "patient-leo-maple", "12-months-visit-maplewood", "in-review", "monitor-asq", 2),
    ("mock-asq-14m-followup", "patient-nora-followup", "14-months-visit", "needs-follow-up", "low-asq", 3),
    ("mock-asq-24m-maplewood", "patient-oliver-two", "2-year-visit-maplewood", "new", "mixed-asq", 4),
    ("mock-teen-13-gad7-phqa", "patient-avery-teen", "13-14-year-visit", "new", "behavioral", 5),
    ("demo-4m-healthy", "patient-sophia-four", "4-months-visit", "complete", "healthy-asq", 6),
    ("demo-6y-psc-review", "patient-mateo-six", "6-year-visit", "needs-follow-up", "psc-review", 7),
    ("demo-8y-well", "patient-emma-eight", "8-year-visit", "complete", "well-child", 8),
    ("demo-10y-sdoh", "patient-jackson-ten", "10-year-visit", "in-review", "sdoh", 9),
    ("demo-12y-behavioral", "patient-lily-twelve", "12-year-visit", "needs-follow-up", "behavioral", 10),
    ("demo-portal-teen", "patient-henry-portal", "patient-portal-12-17", "new", "portal", 11),
    ("demo-release-records", "patient-isabella-acute", "roi-2026", "new", "records", 12),
    ("demo-2m-newborn", "patient-maya-demo", "2-months-visit", "new", "monitor-asq", 13),
    ("demo-7-8m-followup", "patient-leo-maple", "7-8-months-visit", "needs-follow-up", "low-asq", 14),
    ("demo-11y-school", "patient-lily-twelve", "11-year-visit", "in-review", "psc-review", 15),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def iso_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days, hours=days % 5)).isoformat().replace("+00:00", "Z")


def permissions_for_role(role: str) -> list[str]:
    permissions = ["forms:read", "intakes:read", "intakes:update"]
    if role == "admin":
        permissions.extend(["staff:read", "staff:create", "staff:update", "templates:manage"])
    return permissions


def password_hash() -> str:
    return bcrypt.hashpw(DEMO_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def load_templates() -> list[dict[str, Any]]:
    with (ROOT / "backend" / "data" / "form-templates.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def field_value(field: dict[str, Any], patient: dict[str, Any], scenario: str, index: int) -> Any:
    field_id = field.get("id", "")
    field_type = field.get("type", "text")
    options = field.get("options") or []

    fixed_values = {
        "patient_name": patient["fullName"],
        "child_name": patient["fullName"],
        "date_of_birth": patient["dateOfBirth"],
        "completed_by": "Demo Parent",
        "relationship": "Mother",
        "phone": patient["phone"],
        "visit_date": datetime.now(timezone.utc).date().isoformat(),
        "visit_age": field.get("label", "").replace("Visit age", "") or "Age appropriate",
        "clinic_location": "Maplewood" if index % 2 else "Eagan",
        "patient_email": patient["email"],
        "guardian_email": patient["email"],
        "guardian_phone": patient["phone"],
        "guardian_name": "Demo Guardian",
        "signature": f"{patient['fullName']} Guardian",
    }
    if field_id in fixed_values:
        return fixed_values[field_id]

    if field.get("staffOnly"):
        if field_type == "number":
            return 45 if scenario != "low-asq" else 20
        return "Staff review seeded for demo."

    if "asq" in field_id and options == ["Yes", "Sometimes", "Not Yet"]:
        if scenario == "low-asq":
            return "Not Yet" if index % 3 != 0 else "Sometimes"
        if scenario in {"mixed-asq", "monitor-asq"}:
            return ["Yes", "Sometimes", "Not Yet", "Yes", "Sometimes"][index % 5]
        return "Yes" if index % 4 else "Sometimes"

    if field_id.startswith("psc17_") and options:
        if scenario in {"psc-review", "behavioral"}:
            return ["Often (2)", "Sometimes (1)", "Never (0)"][index % 3]
        return "Never (0)" if index % 5 else "Sometimes (1)"

    if field_id.startswith("phqa_") and options:
        return "More than half the days (2)" if scenario == "behavioral" and index % 3 == 0 else "Several days (1)"

    if field_id.startswith("gad7_") and options:
        return "Nearly every day (3)" if scenario == "behavioral" and index % 4 == 0 else "Several days (1)"

    if field_id.startswith("sdoh_") and options:
        return "Yes" if scenario == "sdoh" and index % 3 == 0 else "No"

    if field_type in {"checkbox", "signature"}:
        return True if field_type == "checkbox" else f"{patient['fullName']} Guardian"
    if field_type in {"radio", "select"} and options:
        if "No" in options and scenario not in {"sdoh", "behavioral", "psc-review"}:
            return "No"
        return options[min(index % len(options), len(options) - 1)]
    if field_type == "multicheck" and options:
        return options[: min(3, len(options))]
    if field_type == "date":
        return datetime.now(timezone.utc).date().isoformat()
    if field_type == "number":
        return 1 if "score" not in field_id else 0
    if field_type == "tel":
        return patient["phone"]
    if field_type == "email":
        return patient["email"]
    if field_type == "textarea":
        if scenario in {"behavioral", "psc-review", "sdoh", "low-asq"}:
            return "Seeded demo note: please review this response during staff workflow."
        return "No additional concerns today."
    return "Demo response"


def build_answers(template: dict[str, Any], patient: dict[str, Any], scenario: str) -> dict[str, Any]:
    answers: dict[str, Any] = {}
    counter = 0
    for section in template.get("sections", []):
        for field in section.get("fields", []):
            counter += 1
            if field.get("type") == "display":
                continue
            answers[field["id"]] = field_value(field, patient, scenario, counter)
    return answers


def main() -> int:
    load_dotenv(ROOT / ".env")
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB", "pyam_intake")
    if not mongo_uri:
        print("Missing MONGO_URI in .env or environment.")
        return 1

    templates = load_templates()
    templates_by_id = {template["id"]: template for template in templates}

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    db = client[db_name]
    ensure_database_schema(db)
    seed_form_templates(db, templates, overwrite_existing=True)

    now = utc_now()
    for staff in STAFF_USERS:
        existing_user = db["users"].find_one({"email": staff["email"]})
        user_id = existing_user.get("id") if existing_user else staff["id"]
        user_doc = {
            "id": user_id,
            "email": staff["email"],
            "name": staff["name"],
            "role": staff["role"],
            "isActive": True,
            "passwordHash": password_hash(),
            "createdAt": now,
            "updatedAt": now,
        }
        db["users"].update_one({"email": staff["email"]}, {"$set": user_doc}, upsert=True)
        db["staff_profiles"].update_one(
            {"userId": user_id},
            {
                "$set": {
                    "id": f"profile-{user_id}",
                    "userId": user_id,
                    "displayName": staff["name"],
                    "title": staff["title"],
                    "clinicLocation": staff["clinicLocation"],
                    "permissions": permissions_for_role(staff["role"]),
                    "createdAt": now,
                    "updatedAt": now,
                }
            },
            upsert=True,
        )

    patients = {}
    for patient_id, full_name, dob, email, phone in PATIENTS:
        patient = {
            "id": patient_id,
            "fullName": full_name,
            "dateOfBirth": dob,
            "email": email,
            "phone": phone,
            "createdAt": now,
            "updatedAt": now,
        }
        patients[patient_id] = patient
        db["patients"].update_one({"id": patient_id}, {"$set": patient}, upsert=True)

    for submission_id, patient_id, form_id, status, scenario, days_ago in SUBMISSION_BLUEPRINTS:
        template = templates_by_id.get(form_id)
        patient = patients.get(patient_id)
        if not template or not patient:
            print(f"Skipping {submission_id}: missing template or patient.")
            continue

        created_at = iso_days_ago(days_ago)
        actor = {"id": "patient", "email": "patient@local", "role": "patient"}
        submission = {
            "id": submission_id,
            "formId": form_id,
            "formTemplateVersion": int(template.get("version", 1)),
            "formName": template["name"],
            "category": template["category"],
            "patientId": patient_id,
            "patientName": patient["fullName"],
            "patientDob": patient["dateOfBirth"],
            "status": status,
            "createdAt": created_at,
            "updatedAt": created_at,
            "submittedBy": actor,
            "answers": build_answers(template, patient, scenario),
            "audit": [{"at": created_at, "action": "created", "by": actor["id"]}],
        }
        db["intake_forms"].update_one({"id": submission_id}, {"$set": submission}, upsert=True)
        db["audit_events"].update_one(
            {"id": f"audit-{submission_id}-created"},
            {
                "$set": {
                    "id": f"audit-{submission_id}-created",
                    "at": created_at,
                    "action": "created",
                    "actorId": actor["id"],
                    "entityType": "intake_form",
                    "entityId": submission_id,
                    "metadata": {"formId": form_id, "scenario": scenario},
                }
            },
            upsert=True,
        )

    print(f"Connected to MongoDB database: {db_name}")
    print(f"Demo users upserted: {len(STAFF_USERS)}")
    print(f"Demo patients upserted: {len(PATIENTS)}")
    print(f"Demo submissions upserted: {len(SUBMISSION_BLUEPRINTS)}")
    print("Current collection totals:")
    print(f"- users: {db['users'].estimated_document_count()}")
    print(f"- patients: {db['patients'].estimated_document_count()}")
    print(f"- intake_forms: {db['intake_forms'].estimated_document_count()}")
    print(f"Password for all demo staff users: {DEMO_PASSWORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
