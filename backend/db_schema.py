from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.database import Database


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


USER_SCHEMA: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "email", "passwordHash", "role", "isActive", "createdAt", "updatedAt"],
        "properties": {
            "id": {"bsonType": "string"},
            "email": {"bsonType": "string"},
            "name": {"bsonType": ["string", "null"]},
            "role": {"enum": ["admin", "staff"]},
            "passwordHash": {"bsonType": "string"},
            "isActive": {"bsonType": "bool"},
            "lastLoginAt": {"bsonType": ["string", "null"]},
            "createdAt": {"bsonType": "string"},
            "updatedAt": {"bsonType": "string"},
        },
    }
}

STAFF_PROFILE_SCHEMA: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "userId", "displayName", "permissions", "createdAt", "updatedAt"],
        "properties": {
            "id": {"bsonType": "string"},
            "userId": {"bsonType": "string"},
            "displayName": {"bsonType": "string"},
            "title": {"bsonType": ["string", "null"]},
            "clinicLocation": {"bsonType": ["string", "null"]},
            "permissions": {"bsonType": "array"},
            "createdAt": {"bsonType": "string"},
            "updatedAt": {"bsonType": "string"},
        },
    }
}

FORM_TEMPLATE_SCHEMA: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "name", "category", "version", "status", "sections", "createdAt", "updatedAt"],
        "properties": {
            "id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "category": {"bsonType": "string"},
            "description": {"bsonType": ["string", "null"]},
            "estimatedMinutes": {"bsonType": ["int", "long", "double", "null"]},
            "version": {"bsonType": "int"},
            "status": {"enum": ["draft", "active", "archived"]},
            "sections": {"bsonType": "array"},
            "sourceFiles": {"bsonType": ["array", "null"]},
            "createdAt": {"bsonType": "string"},
            "updatedAt": {"bsonType": "string"},
        },
    }
}

INTAKE_FORM_SCHEMA: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "id",
            "formId",
            "formName",
            "category",
            "patientName",
            "status",
            "createdAt",
            "updatedAt",
            "answers",
        ],
        "properties": {
            "id": {"bsonType": "string"},
            "formId": {"bsonType": "string"},
            "formTemplateVersion": {"bsonType": ["int", "null"]},
            "formName": {"bsonType": "string"},
            "category": {"bsonType": "string"},
            "patientId": {"bsonType": ["string", "null"]},
            "patientName": {"bsonType": "string"},
            "patientDob": {"bsonType": ["string", "null"]},
            "status": {"enum": ["new", "in-review", "complete", "needs-follow-up"]},
            "submittedBy": {"bsonType": "object"},
            "answers": {"bsonType": "object"},
            "audit": {"bsonType": ["array", "null"]},
            "createdAt": {"bsonType": "string"},
            "updatedAt": {"bsonType": "string"},
        },
    }
}

PATIENT_SCHEMA: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "fullName", "createdAt", "updatedAt"],
        "properties": {
            "id": {"bsonType": "string"},
            "fullName": {"bsonType": "string"},
            "dateOfBirth": {"bsonType": ["string", "null"]},
            "email": {"bsonType": ["string", "null"]},
            "phone": {"bsonType": ["string", "null"]},
            "createdAt": {"bsonType": "string"},
            "updatedAt": {"bsonType": "string"},
        },
    }
}

AUDIT_EVENT_SCHEMA: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "at", "action", "actorId", "entityType", "entityId"],
        "properties": {
            "id": {"bsonType": "string"},
            "at": {"bsonType": "string"},
            "action": {"bsonType": "string"},
            "actorId": {"bsonType": "string"},
            "entityType": {"bsonType": "string"},
            "entityId": {"bsonType": "string"},
            "metadata": {"bsonType": ["object", "null"]},
        },
    }
}

COLLECTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "users": USER_SCHEMA,
    "staff_profiles": STAFF_PROFILE_SCHEMA,
    "form_templates": FORM_TEMPLATE_SCHEMA,
    "intake_forms": INTAKE_FORM_SCHEMA,
    "patients": PATIENT_SCHEMA,
    "audit_events": AUDIT_EVENT_SCHEMA,
}


def ensure_collection(db: Database, name: str, validator: dict[str, Any]) -> None:
    if name not in db.list_collection_names():
        db.create_collection(name, validator=validator, validationLevel="moderate")
        return

    db.command(
        {
            "collMod": name,
            "validator": validator,
            "validationLevel": "moderate",
        }
    )


def ensure_indexes(db: Database) -> None:
    db["users"].create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("role", ASCENDING), ("isActive", ASCENDING)]),
        ]
    )
    db["staff_profiles"].create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("userId", ASCENDING)], unique=True),
            IndexModel([("clinicLocation", ASCENDING)]),
        ]
    )
    db["form_templates"].create_indexes(
        [
            IndexModel([("id", ASCENDING), ("version", ASCENDING)], unique=True),
            IndexModel([("status", ASCENDING), ("category", ASCENDING), ("name", ASCENDING)]),
        ]
    )
    db["intake_forms"].create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("formId", ASCENDING), ("createdAt", DESCENDING)]),
            IndexModel([("status", ASCENDING), ("createdAt", DESCENDING)]),
            IndexModel([("patientName", ASCENDING)]),
            IndexModel([("patientDob", ASCENDING)]),
        ]
    )
    db["patients"].create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("fullName", ASCENDING), ("dateOfBirth", ASCENDING)]),
            IndexModel([("email", ASCENDING)]),
        ]
    )
    db["audit_events"].create_indexes(
        [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("entityType", ASCENDING), ("entityId", ASCENDING), ("at", DESCENDING)]),
            IndexModel([("actorId", ASCENDING), ("at", DESCENDING)]),
        ]
    )


def ensure_database_schema(db: Database) -> None:
    for name, schema in COLLECTION_SCHEMAS.items():
        ensure_collection(db, name, schema)
    ensure_indexes(db)


def seed_form_templates(db: Database, templates: list[dict[str, Any]], overwrite_existing: bool = False) -> int:
    now = utc_now()
    changed = 0
    for template in templates:
        document = {
            **template,
            "version": int(template.get("version", 1)),
            "status": template.get("status", "active"),
            "createdAt": template.get("createdAt", now),
            "updatedAt": now,
        }
        if document["status"] == "active":
            db["form_templates"].update_many(
                {"id": document["id"], "version": {"$ne": document["version"]}, "status": "active"},
                {"$set": {"status": "archived", "updatedAt": now}},
            )

        existing = db["form_templates"].find_one({"id": document["id"], "version": document["version"]})
        if existing and not overwrite_existing:
            continue

        result = db["form_templates"].update_one(
            {"id": document["id"], "version": document["version"]},
            {"$set": document},
            upsert=True,
        )
        if result.upserted_id or result.modified_count:
            changed += 1
    return changed
