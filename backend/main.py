from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import bcrypt
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.collection import Collection

from backend.db_schema import ensure_database_schema, seed_form_templates
from backend.scoring import add_calculated_scores, review_for_submission


ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
FRONTEND_DIST_DIR = ROOT / "frontend" / "dist"
FRONTEND_PUBLIC_DIR = FRONTEND_DIST_DIR if FRONTEND_DIST_DIR.exists() else ROOT / "frontend" / "public"
TEMPLATES_FILE = DATA_DIR / "form-templates.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
USERS_FILE = DATA_DIR / "users.json"

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "pyam_intake")
PYAM_ENV = os.getenv("PYAM_ENV", "development").lower()
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-for-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
DEFAULT_CORS_ORIGINS = (
    "http://localhost:5177,"
    "http://127.0.0.1:5177,"
    "http://localhost:5178,"
    "http://127.0.0.1:5178,"
    "https://frontend-ruddy-eight-66.vercel.app,"
    "https://pyam-patient.vercel.app,"
    "https://pyam-staff.vercel.app"
)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX")

mongo_client: MongoClient | None = MongoClient(MONGO_URI) if MONGO_URI else None
mongo_db = mongo_client[MONGODB_DB] if mongo_client is not None else None

if PYAM_ENV == "production":
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is required when PYAM_ENV=production.")
    if not os.getenv("JWT_SECRET") or JWT_SECRET == "change-me-for-production":
        raise RuntimeError("A strong JWT_SECRET is required when PYAM_ENV=production.")


app = FastAPI(
    title="PYAM Intake API",
    version="0.2.0",
    description="FastAPI backend for collecting clinic intake forms.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_indexes() -> None:
    if mongo_db is None:
        return
    ensure_database_schema(mongo_db)
    seed_form_templates(mongo_db, read_json(TEMPLATES_FILE, []))


@app.middleware("http")
async def prevent_frontend_cache(request: Request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StaffCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str
    role: str = "staff"
    title: str | None = None
    clinic_location: str | None = Field(default=None, alias="clinicLocation")

    model_config = {"populate_by_name": True}


class SubmissionCreate(BaseModel):
    form_id: str | None = Field(default=None, alias="formId")
    answers: dict[str, Any] = Field(default_factory=dict)
    status: str = "new"

    model_config = {"populate_by_name": True}


class SubmissionUpdate(BaseModel):
    status: str | None = None
    answers: dict[str, Any] | None = None


class PatientDraftUpdate(BaseModel):
    answers: dict[str, Any] = Field(default_factory=dict)


class AuditEventCreate(BaseModel):
    action: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class FormTemplateUpdate(BaseModel):
    template: dict[str, Any]
    publish: bool = True


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def users() -> Collection:
    if mongo_db is None:
        raise RuntimeError("MongoDB is not configured.")
    return mongo_db["users"]


def users_exist() -> bool:
    if mongo_db is not None:
        return users().estimated_document_count() > 0
    return len(get_local_users()) > 0


def submissions() -> Collection:
    if mongo_db is None:
        raise RuntimeError("MongoDB is not configured.")
    return mongo_db["intake_forms"]


def audit_events() -> Collection:
    if mongo_db is None:
        raise RuntimeError("MongoDB is not configured.")
    return mongo_db["audit_events"]


def staff_profiles() -> Collection:
    if mongo_db is None:
        raise RuntimeError("MongoDB is not configured.")
    return mongo_db["staff_profiles"]


def form_templates() -> Collection:
    if mongo_db is None:
        raise RuntimeError("MongoDB is not configured.")
    return mongo_db["form_templates"]


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(user.get("id") or user.get("_id")),
        "email": user["email"],
        "name": user.get("name") or user["email"].split("@")[0],
        "role": user.get("role", "staff"),
        "isActive": user.get("isActive", True),
    }


def audit_actor(user: dict[str, Any] | None) -> dict[str, str]:
    if not user:
        return {"id": "patient", "email": "patient@local", "name": "Patient", "role": "patient"}
    return {
        "id": str(user.get("id") or user.get("_id")),
        "email": user.get("email", ""),
        "name": user.get("name") or user.get("email", "").split("@")[0] or "Staff user",
        "role": user.get("role", "staff"),
    }


def audit_event(
    action: str,
    actor: dict[str, str],
    entity_id: str,
    metadata: dict[str, Any] | None = None,
    entity_type: str = "intake_form",
) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "at": utc_now(),
        "action": action,
        "by": actor["id"],
        "actorId": actor["id"],
        "actorEmail": actor.get("email"),
        "actorName": actor.get("name"),
        "actorRole": actor.get("role"),
        "entityType": entity_type,
        "entityId": entity_id,
        "metadata": metadata or {},
    }


def save_audit_event(event: dict[str, Any]) -> None:
    if mongo_db is not None:
        audit_events().insert_one(dict(event))


def audit_history_for_submission(submission: dict[str, Any]) -> list[dict[str, Any]]:
    embedded_events = submission.get("audit") or []
    if mongo_db is not None:
        stored_events = [
            normalize_document(event)
            for event in audit_events().find({"entityType": "intake_form", "entityId": submission["id"]})
        ]
        if stored_events:
            return sorted(stored_events, key=lambda item: item.get("at", ""))
    return sorted(embedded_events, key=lambda item: item.get("at", ""))


def normalize_document(document: dict[str, Any]) -> dict[str, Any]:
    item = dict(document)
    if "_id" in item:
        item.setdefault("mongoId", str(item.pop("_id")))
    return item


def get_templates() -> list[dict[str, Any]]:
    if mongo_db is not None:
        return [
            normalize_document(template)
            for template in form_templates().find({"status": "active"}).sort([("category", ASCENDING), ("name", ASCENDING)])
        ]
    return [template for template in read_json(TEMPLATES_FILE, []) if template.get("status", "active") == "active"]


def get_draft_templates() -> list[dict[str, Any]]:
    if mongo_db is not None:
        return [
            normalize_document(template)
            for template in form_templates().find({"status": "draft"}).sort([("updatedAt", -1), ("name", ASCENDING)])
        ]
    return sorted(
        [template for template in read_json(TEMPLATES_FILE, []) if template.get("status") == "draft"],
        key=lambda item: item.get("updatedAt", ""),
        reverse=True,
    )


def get_template_versions(form_id: str) -> list[dict[str, Any]]:
    if mongo_db is not None:
        return [
            normalize_document(template)
            for template in form_templates().find({"id": form_id}).sort([("version", -1), ("updatedAt", -1)])
        ]
    return sorted(
        [template for template in read_json(TEMPLATES_FILE, []) if template.get("id") == form_id],
        key=lambda item: (int(item.get("version", 1)), item.get("updatedAt", "")),
        reverse=True,
    )


def get_local_users() -> list[dict[str, Any]]:
    return read_json(USERS_FILE, [])


def save_local_users(items: list[dict[str, Any]]) -> None:
    write_json(USERS_FILE, items)


def get_local_submissions() -> list[dict[str, Any]]:
    return read_json(SUBMISSIONS_FILE, [])


def save_local_submissions(items: list[dict[str, Any]]) -> None:
    write_json(SUBMISSIONS_FILE, items)


def find_user_by_email(email: str) -> dict[str, Any] | None:
    normalized = email.lower()
    if mongo_db is not None:
        user = users().find_one({"email": normalized})
        return normalize_document(user) if user else None
    return next((item for item in get_local_users() if item.get("email") == normalized), None)


def find_user_by_id(user_id: str) -> dict[str, Any] | None:
    if mongo_db is not None:
        user = users().find_one({"id": user_id})
        if user:
            return normalize_document(user)
    return next((item for item in get_local_users() if item.get("id") == user_id), None)


def permissions_for_role(role: str) -> list[str]:
    permissions = ["forms:read", "intakes:read", "intakes:update"]
    if role == "admin":
        permissions.extend(["staff:read", "staff:create", "staff:update", "templates:manage"])
    return permissions


def create_user(
    email: str,
    password: str,
    name: str | None,
    role: str = "staff",
    title: str | None = None,
    clinic_location: str | None = None,
) -> dict[str, Any]:
    if role not in {"admin", "staff"}:
        raise HTTPException(status_code=400, detail="Unsupported user role.")

    now = utc_now()
    user = {
        "id": str(uuid4()),
        "email": email.lower(),
        "name": name,
        "role": role,
        "isActive": True,
        "passwordHash": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "createdAt": now,
        "updatedAt": now,
    }
    if mongo_db is not None:
        users().insert_one(dict(user))
        staff_profiles().insert_one(
            {
                "id": str(uuid4()),
                "userId": user["id"],
                "displayName": user.get("name") or user["email"].split("@")[0],
                "title": title,
                "clinicLocation": clinic_location,
                "permissions": permissions_for_role(role),
                "createdAt": now,
                "updatedAt": now,
            }
        )
    else:
        items = get_local_users()
        items.append(user)
        save_local_users(items)
    return user


def create_access_token(user: dict[str, Any]) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user["id"], "email": user["email"], "role": user.get("role", "staff"), "exp": expires},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def get_current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired login.")

    user = find_user_by_id(str(payload.get("sub", "")))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    return user


def get_optional_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    if not authorization:
        return None
    return get_current_user(authorization)


def require_admin(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def flatten_template_fields(template: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for section in template.get("sections", []):
        for field in section.get("fields", []):
            fields.append({**field, "section": section.get("title", "")})
    return fields


def template_submission_snapshot(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": template.get("id"),
        "name": template.get("name"),
        "category": template.get("category"),
        "description": template.get("description"),
        "estimatedMinutes": template.get("estimatedMinutes"),
        "version": int(template.get("version", 1)),
        "sourceFile": template.get("sourceFile"),
        "sourceFiles": template.get("sourceFiles"),
        "sections": [
            {
                "title": section.get("title"),
                "fieldCount": len(section.get("fields", [])),
                "contentCount": len(section.get("content", [])),
                "content": section.get("content", []),
                "fields": [
                    {
                        "id": field.get("id"),
                        "label": field.get("label"),
                        "type": field.get("type"),
                        "options": field.get("options"),
                        "required": bool(field.get("required")),
                        "owner": field.get("owner"),
                        "staffOnly": bool(field.get("staffOnly") or field.get("owner") == "staff"),
                    }
                    for field in section.get("fields", [])
                ],
            }
            for section in template.get("sections", [])
        ],
    }


def validate_submission(template: dict[str, Any], answers: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in flatten_template_fields(template):
        if not field.get("required"):
            continue

        value = answers.get(field["id"])
        is_empty_list = isinstance(value, list) and len(value) == 0
        if value is None or value == "" or value is False or is_empty_list:
            errors.append(f"{field.get('label', field['id'])} is required.")

    return errors


def validate_form_template(template: dict[str, Any]) -> dict[str, Any]:
    allowed_field_types = {"text", "email", "tel", "date", "number", "datetime-local", "textarea", "select", "radio", "multicheck", "checkbox", "scale", "signature"}
    required = ["id", "name", "category", "sections"]
    missing = [key for key in required if not template.get(key)]
    if missing:
        raise HTTPException(status_code=422, detail=f"Template is missing: {', '.join(missing)}.")
    if not isinstance(template.get("sections"), list):
        raise HTTPException(status_code=422, detail="Template sections must be a list.")
    field_ids: list[str] = []
    for section_index, section in enumerate(template["sections"], start=1):
        if not section.get("title"):
            raise HTTPException(status_code=422, detail=f"Section {section_index} needs a title.")
        fields = section.get("fields", [])
        content = section.get("content", [])
        if not isinstance(fields, list) or not isinstance(content, list):
            raise HTTPException(status_code=422, detail=f"Section {section_index} fields and content must be lists.")
        for field_index, field in enumerate(fields, start=1):
            if not field.get("id") or not field.get("label") or not field.get("type"):
                raise HTTPException(status_code=422, detail=f"Field {field_index} in section {section_index} needs id, label, and type.")
            if field.get("type") not in allowed_field_types:
                raise HTTPException(status_code=422, detail=f"Field {field.get('id')} uses unsupported type {field.get('type')}.")
            field_ids.append(str(field["id"]))
            if field.get("type") in {"radio", "select", "multicheck", "scale"} and not isinstance(field.get("options", []), list):
                raise HTTPException(status_code=422, detail=f"Options for field {field.get('id')} must be a list.")
    duplicate_ids = sorted({field_id for field_id in field_ids if field_ids.count(field_id) > 1})
    if duplicate_ids:
        raise HTTPException(status_code=422, detail=f"Duplicate field ids are not allowed: {', '.join(duplicate_ids[:10])}.")
    now = utc_now()
    return {
        **template,
        "version": int(template.get("version", 1)),
        "status": template.get("status", "active"),
        "updatedAt": now,
        "createdAt": template.get("createdAt", now),
    }


def template_guardrail_warnings(template: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    field_ids = {
        str(field.get("id"))
        for section in template.get("sections", [])
        for field in section.get("fields", [])
        if field.get("id")
    }
    scoring_markers = ["asq", "epds", "phq", "gad7", "psc17", "vanderbilt", "scared", "asrs", "ppsc", "mchat", "act", "cact", "crafft", "ace"]
    scoring_ids = [field_id for field_id in field_ids if any(marker in field_id.lower() for marker in scoring_markers)]
    if scoring_ids:
        warnings.append("This template contains scoring-sensitive fields. Changing field IDs or options can affect automatic calculations.")
    asq_prefixes = sorted({field_id.rsplit("_", 1)[0] for field_id in field_ids if re_match_asq_item(field_id)})
    for prefix in asq_prefixes:
        expected = {f"{prefix}_{index}" for index in range(1, 7)}
        missing = sorted(expected - field_ids)
        if missing:
            warnings.append(f"ASQ group {prefix} is missing item fields: {', '.join(missing)}.")
    return warnings


def re_match_asq_item(field_id: str) -> bool:
    return bool(re.match(r"^asq\d*_(communication|comm|gross|fine|problem|social)_\d+$", field_id))


def next_template_version(form_id: str) -> int:
    if mongo_db is not None:
        latest = form_templates().find_one({"id": form_id}, sort=[("version", -1)])
        return int(latest.get("version", 0)) + 1 if latest else 1
    templates = read_json(TEMPLATES_FILE, [])
    versions = [int(item.get("version", 1)) for item in templates if item.get("id") == form_id]
    return max(versions, default=0) + 1


def patient_name_from_answers(answers: dict[str, Any]) -> str:
    explicit_name = answers.get("patient_name") or answers.get("child_name")
    if explicit_name:
        return str(explicit_name)

    first_last = " ".join(
        str(part) for part in [answers.get("patient_first_name"), answers.get("patient_last_name")] if part
    )
    return first_last or "Unnamed patient"


def generate_resume_code() -> str:
    return uuid4().hex[:10].upper()


def find_patient_draft_by_code(resume_code: str) -> dict[str, Any] | None:
    normalized_code = resume_code.strip().upper()
    if mongo_db is not None:
        draft = submissions().find_one({"resumeCode": normalized_code, "status": "draft"})
        return normalize_document(draft) if draft else None
    return next(
        (
            item
            for item in get_local_submissions()
            if item.get("resumeCode") == normalized_code and item.get("status") == "draft"
        ),
        None,
    )


def submission_severity_score(submission: dict[str, Any]) -> int:
    review = submission.get("review") or review_for_submission(submission)
    flags = review.get("flags") or []
    flag_score = sum(
        100 if flag.get("severity") == "high" else 30 if flag.get("severity") == "medium" else 5
        for flag in flags
    )
    status_score = (
        80
        if submission.get("status") in {"needs-follow-up", "needs-patient-follow-up"}
        else 60
        if review.get("status") == "needs-review"
        else 20
        if submission.get("status") == "new"
        else 5
        if submission.get("status") == "draft"
        else 0
    )
    return flag_score + status_score


def submission_search_text(submission: dict[str, Any]) -> str:
    review = submission.get("review") or review_for_submission(submission)
    flags = review.get("flags") or []
    parts = [
        submission.get("patientName"),
        submission.get("patientDob"),
        submission.get("formName"),
        submission.get("category"),
        submission.get("status"),
        review.get("label"),
        *(flag.get("label") for flag in flags),
        *(flag.get("type") for flag in flags),
    ]
    return " ".join(str(part or "") for part in parts).lower()


def matches_review_filter(submission: dict[str, Any], review_filter: str | None) -> bool:
    if not review_filter:
        return True
    review = submission.get("review") or review_for_submission(submission)
    return review.get("status") == review_filter or any(
        flag.get("type") == review_filter or flag.get("key") == review_filter
        for flag in review.get("flags") or []
    )


def sort_submission_items(items: list[dict[str, Any]], sort_mode: str) -> list[dict[str, Any]]:
    if sort_mode == "priority":
        return sorted(items, key=lambda item: (submission_severity_score(item), item.get("createdAt", "")), reverse=True)
    if sort_mode == "oldest":
        return sorted(items, key=lambda item: item.get("createdAt", ""))
    if sort_mode == "patient":
        return sorted(items, key=lambda item: str(item.get("patientName") or "").lower())
    if sort_mode == "form":
        return sorted(items, key=lambda item: str(item.get("formName") or "").lower())
    return sorted(items, key=lambda item: item.get("createdAt", ""), reverse=True)


@app.get("/api/health")
def health() -> dict[str, Any]:
    template_count = form_templates().count_documents({"status": "active"}) if mongo_db is not None else len(get_templates())
    return {
        "ok": True,
        "environment": PYAM_ENV,
        "storage": "mongodb" if mongo_db is not None else "local-json",
        "database": MONGODB_DB if mongo_db is not None else None,
        "activeTemplates": template_count,
        "productionReady": PYAM_ENV != "production" or (mongo_db is not None and JWT_SECRET != "change-me-for-production"),
        "timestamp": utc_now(),
    }


@app.get("/api/auth/bootstrap")
def bootstrap_status() -> dict[str, Any]:
    return {"needsFirstAdmin": not users_exist()}


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterRequest) -> dict[str, Any]:
    if users_exist():
        raise HTTPException(status_code=403, detail="Public registration is closed. Ask an admin to create your account.")
    if find_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="An account already exists for this email.")
    user = create_user(payload.email, payload.password, payload.name, role="admin", title="Administrator")
    return {"user": public_user(user), "accessToken": create_access_token(user)}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    user = find_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.get("isActive", True):
        raise HTTPException(status_code=403, detail="This account is inactive.")
    if mongo_db is not None:
        users().update_one({"id": user["id"]}, {"$set": {"lastLoginAt": utc_now()}})
    return {"user": public_user(user), "accessToken": create_access_token(user)}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": public_user(user)}


@app.get("/api/staff")
def list_staff(admin: dict[str, Any] = Depends(require_admin)) -> dict[str, list[dict[str, Any]]]:
    del admin
    if mongo_db is None:
        return {"staff": [public_user(user) for user in get_local_users()]}

    profiles_by_user_id = {
        profile["userId"]: normalize_document(profile)
        for profile in staff_profiles().find()
    }
    staff = []
    for user in users().find().sort([("role", ASCENDING), ("email", ASCENDING)]):
        item = public_user(normalize_document(user))
        profile = profiles_by_user_id.get(item["id"], {})
        item["title"] = profile.get("title")
        item["clinicLocation"] = profile.get("clinicLocation")
        item["permissions"] = profile.get("permissions", permissions_for_role(item["role"]))
        staff.append(item)
    return {"staff": staff}


@app.post("/api/staff", status_code=201)
def create_staff(
    payload: StaffCreateRequest,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, Any]:
    del admin
    if payload.role not in {"admin", "staff"}:
        raise HTTPException(status_code=400, detail="Unsupported user role.")
    if find_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="An account already exists for this email.")

    user = create_user(
        payload.email,
        payload.password,
        payload.name,
        role=payload.role,
        title=payload.title,
        clinic_location=payload.clinic_location,
    )
    return {"user": public_user(user)}


@app.get("/api/forms")
def list_forms() -> dict[str, list[dict[str, Any]]]:
    return {"forms": get_templates()}


@app.get("/api/forms/drafts")
def list_form_drafts(admin: dict[str, Any] = Depends(require_admin)) -> dict[str, list[dict[str, Any]]]:
    del admin
    return {"drafts": get_draft_templates()}


@app.delete("/api/forms/{form_id}/draft", status_code=204, response_class=Response)
def delete_form_draft(
    form_id: str,
    admin: dict[str, Any] = Depends(require_admin),
) -> Response:
    actor = audit_actor(admin)
    event = audit_event(
        "form_template_draft_discarded",
        actor,
        form_id,
        metadata={"formId": form_id},
        entity_type="form_template",
    )

    if mongo_db is not None:
        result = form_templates().delete_many({"id": form_id, "status": "draft"})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Draft template not found.")
        save_audit_event(event)
        return Response(status_code=204)

    templates = read_json(TEMPLATES_FILE, [])
    next_templates = [template for template in templates if not (template.get("id") == form_id and template.get("status") == "draft")]
    if len(next_templates) == len(templates):
        raise HTTPException(status_code=404, detail="Draft template not found.")
    write_json(TEMPLATES_FILE, next_templates)
    return Response(status_code=204)


@app.get("/api/forms/{form_id}/versions")
def list_form_versions(
    form_id: str,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, list[dict[str, Any]]]:
    del admin
    versions = get_template_versions(form_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Form template not found.")
    return {"versions": versions}


@app.get("/api/forms/{form_id}")
def get_form(form_id: str) -> dict[str, dict[str, Any]]:
    form = next((template for template in get_templates() if template.get("id") == form_id), None)
    if not form:
        raise HTTPException(status_code=404, detail="Form template not found.")
    return {"form": form}


@app.patch("/api/forms/{form_id}")
def update_form_template(
    form_id: str,
    payload: FormTemplateUpdate,
    admin: dict[str, Any] = Depends(require_admin),
) -> dict[str, dict[str, Any]]:
    template = validate_form_template(payload.template)
    if template["id"] != form_id:
        raise HTTPException(status_code=400, detail="Template id cannot be changed from this endpoint.")
    warnings = template_guardrail_warnings(template)
    requested_version = int(template.get("version", 1))
    if payload.publish:
        template["version"] = next_template_version(form_id)
        template["status"] = "active"
    else:
        template["status"] = "draft"

    now = utc_now()
    actor = audit_actor(admin)
    event = audit_event(
        "form_template_published" if payload.publish else "form_template_draft_saved",
        actor,
        form_id,
        metadata={
            "formName": template["name"],
            "previousVersion": requested_version,
            "version": template["version"],
            "sectionCount": len(template.get("sections", [])),
            "fieldCount": sum(len(section.get("fields", [])) for section in template.get("sections", [])),
        },
        entity_type="form_template",
    )
    event["at"] = now
    template["audit"] = [*(template.get("audit") or []), event]

    if mongo_db is not None:
        if payload.publish:
            form_templates().update_many(
                {"id": form_id, "status": {"$in": ["active", "draft"]}},
                {"$set": {"status": "archived", "updatedAt": now}},
            )
        result = form_templates().insert_one(dict(template))
        saved = form_templates().find_one({"_id": result.inserted_id})
        save_audit_event(event)
        return {"form": normalize_document(saved), "warnings": warnings}

    templates = read_json(TEMPLATES_FILE, [])
    if not any(item.get("id") == form_id for item in templates):
        raise HTTPException(status_code=404, detail="Form template not found.")
    if payload.publish:
        templates = [
            {**item, "status": "archived", "updatedAt": now}
            if item.get("id") == form_id and item.get("status", "active") in {"active", "draft"}
            else item
            for item in templates
        ]
        templates.append(template)
    else:
        draft_index = next((i for i, item in enumerate(templates) if item.get("id") == form_id and item.get("status") == "draft"), -1)
        if draft_index == -1:
            templates.append(template)
        else:
            templates[draft_index] = template
    write_json(TEMPLATES_FILE, templates)
    return {"form": template, "warnings": warnings}


@app.get("/api/submissions")
def list_submissions(
    user: dict[str, Any] = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    form_id: str | None = Query(default=None, alias="formId"),
    review_filter: str | None = Query(default=None, alias="review"),
    search: str | None = None,
    sort: str = Query(default="priority"),
) -> dict[str, Any]:
    del user
    query: dict[str, Any] = {}
    if status_filter:
        query["status"] = {"$in": ["needs-follow-up", "needs-patient-follow-up"]} if status_filter == "needs-patient-follow-up" else status_filter
    if form_id:
        query["formId"] = form_id
    search_text = (search or "").strip().lower()

    if mongo_db is not None:
        stored_items = [
            normalize_document(item)
            for item in submissions().find(query).sort("createdAt", -1)
        ]
    else:
        stored_items = [
            item
            for item in get_local_submissions()
            if (
                not status_filter
                or item.get("status") == status_filter
                or (status_filter == "needs-patient-follow-up" and item.get("status") == "needs-follow-up")
            )
            and (not form_id or item.get("formId") == form_id)
        ]

    enriched_items = []
    for submission in stored_items:
        item = dict(submission)
        item["review"] = item.get("review") or review_for_submission(item)
        enriched_items.append(item)

    filtered_items = [
        item
        for item in enriched_items
        if matches_review_filter(item, review_filter)
        and (not search_text or search_text in submission_search_text(item))
    ]
    sorted_items = sort_submission_items(filtered_items, sort)
    if cursor:
        sorted_items = [item for item in sorted_items if item.get("createdAt", "") < cursor]

    has_more = len(sorted_items) > limit
    page_items = sorted_items[:limit]
    summary = []
    for submission in page_items:
        item = {key: value for key, value in submission.items() if key not in {"answers", "audit", "formTemplateSnapshot"}}
        summary.append(item)

    return {
        "submissions": summary,
        "nextCursor": page_items[-1].get("createdAt") if has_more and page_items else None,
        "hasMore": has_more,
        "totalMatched": len(sorted_items),
    }


@app.get("/api/submissions/{submission_id}")
def get_submission(
    submission_id: str,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, dict[str, Any]]:
    del user
    if mongo_db is not None:
        submission = submissions().find_one({"id": submission_id})
        if submission:
            submission = normalize_document(submission)
    else:
        submission = next((item for item in get_local_submissions() if item.get("id") == submission_id), None)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    submission["auditHistory"] = audit_history_for_submission(submission)
    return {"submission": submission}


@app.post("/api/submissions", status_code=201)
def create_submission(
    payload: SubmissionCreate,
    request_user: dict[str, Any] | None = Depends(get_optional_user),
) -> dict[str, dict[str, Any]]:
    templates = get_templates()
    template = next((item for item in templates if item.get("id") == payload.form_id), None)
    if not template:
        raise HTTPException(status_code=400, detail="Unknown form template.")

    scored_answers = add_calculated_scores(template["id"], payload.answers)
    if payload.status not in {"draft", "new"}:
        raise HTTPException(status_code=400, detail="Unsupported initial submission status.")

    validation_errors = validate_submission(template, scored_answers)
    if payload.status != "draft" and validation_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Submission is missing required information.",
                "details": validation_errors,
            },
        )

    now = utc_now()
    submission_id = str(uuid4())
    actor = audit_actor(request_user)
    event = audit_event(
        "submission_created",
        actor,
        entity_id=submission_id,
        metadata={
            "formId": template["id"],
            "formName": template["name"],
            "formTemplateVersion": int(template.get("version", 1)),
            "status": payload.status,
            "requiredMissingCount": len(validation_errors),
        },
    )
    event["at"] = now
    submission = {
        "id": submission_id,
        "formId": template["id"],
        "formTemplateVersion": int(template.get("version", 1)),
        "formTemplateSnapshot": template_submission_snapshot(template),
        "formName": template["name"],
        "category": template["category"],
        "patientName": patient_name_from_answers(scored_answers),
        "patientDob": scored_answers.get("date_of_birth"),
        "status": payload.status,
        "createdAt": now,
        "updatedAt": now,
        "submittedBy": actor,
        "answers": scored_answers,
        "audit": [event],
    }
    submission["review"] = review_for_submission(submission)

    if mongo_db is not None:
        submissions().insert_one(dict(submission))
        save_audit_event(event)
    else:
        stored_items = get_local_submissions()
        stored_items.append(submission)
        save_local_submissions(stored_items)
    submission["auditHistory"] = [event]
    return {"submission": submission}


@app.post("/api/patient-drafts", status_code=201)
def create_patient_draft(payload: SubmissionCreate) -> dict[str, dict[str, Any]]:
    templates = get_templates()
    template = next((item for item in templates if item.get("id") == payload.form_id), None)
    if not template:
        raise HTTPException(status_code=400, detail="Unknown form template.")

    scored_answers = add_calculated_scores(template["id"], payload.answers)
    now = utc_now()
    submission_id = str(uuid4())
    resume_code = generate_resume_code()
    actor = audit_actor(None)
    event = audit_event(
        "patient_draft_saved",
        actor,
        entity_id=submission_id,
        metadata={
            "formId": template["id"],
            "formName": template["name"],
            "formTemplateVersion": int(template.get("version", 1)),
            "resumeCode": resume_code,
        },
    )
    event["at"] = now
    draft = {
        "id": submission_id,
        "resumeCode": resume_code,
        "formId": template["id"],
        "formTemplateVersion": int(template.get("version", 1)),
        "formTemplateSnapshot": template_submission_snapshot(template),
        "formName": template["name"],
        "category": template["category"],
        "patientName": patient_name_from_answers(scored_answers),
        "patientDob": scored_answers.get("date_of_birth"),
        "status": "draft",
        "createdAt": now,
        "updatedAt": now,
        "submittedBy": actor,
        "answers": scored_answers,
        "audit": [event],
    }
    draft["review"] = review_for_submission(draft)

    if mongo_db is not None:
        submissions().insert_one(dict(draft))
        save_audit_event(event)
    else:
        stored_items = get_local_submissions()
        stored_items.append(draft)
        save_local_submissions(stored_items)
    draft["auditHistory"] = [event]
    return {"draft": draft, "form": template}


@app.get("/api/patient-drafts/{resume_code}")
def get_patient_draft(resume_code: str) -> dict[str, dict[str, Any]]:
    draft = find_patient_draft_by_code(resume_code)
    if not draft:
        raise HTTPException(status_code=404, detail="Resume draft not found.")
    form = next((item for item in get_templates() if item.get("id") == draft.get("formId")), None)
    if not form:
        form = {
            "id": draft.get("formId"),
            "name": draft.get("formName"),
            "category": draft.get("category"),
            "sections": draft.get("formTemplateSnapshot", {}).get("sections", []),
        }
    draft["auditHistory"] = audit_history_for_submission(draft)
    return {"draft": draft, "form": form}


@app.patch("/api/patient-drafts/{resume_code}")
def update_patient_draft(resume_code: str, payload: PatientDraftUpdate) -> dict[str, dict[str, Any]]:
    existing = find_patient_draft_by_code(resume_code)
    if not existing:
        raise HTTPException(status_code=404, detail="Resume draft not found.")
    form = next((item for item in get_templates() if item.get("id") == existing.get("formId")), None)
    if not form:
        raise HTTPException(status_code=400, detail="Original form template is no longer active.")

    now = utc_now()
    scored_answers = add_calculated_scores(form["id"], payload.answers)
    actor = audit_actor(None)
    event = audit_event(
        "patient_draft_saved",
        actor,
        existing["id"],
        metadata={
            "formId": form["id"],
            "formName": form["name"],
            "formTemplateVersion": int(form.get("version", 1)),
            "resumeCode": existing.get("resumeCode"),
        },
    )
    event["at"] = now
    set_fields = {
        "answers": scored_answers,
        "patientName": patient_name_from_answers(scored_answers),
        "patientDob": scored_answers.get("date_of_birth"),
        "updatedAt": now,
    }
    review_submission = {**existing, **set_fields}
    set_fields["review"] = review_for_submission(review_submission)

    if mongo_db is not None:
        updated = submissions().find_one_and_update(
            {"id": existing["id"], "status": "draft"},
            {"$set": set_fields, "$push": {"audit": event}},
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Resume draft not found.")
        save_audit_event(event)
        draft = normalize_document(updated)
        draft["auditHistory"] = audit_history_for_submission(draft)
        return {"draft": draft, "form": form}

    stored_items = get_local_submissions()
    index = next((i for i, item in enumerate(stored_items) if item.get("id") == existing["id"]), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="Resume draft not found.")
    stored_items[index] = {**stored_items[index], **set_fields}
    stored_items[index].setdefault("audit", []).append(event)
    save_local_submissions(stored_items)
    stored_items[index]["auditHistory"] = audit_history_for_submission(stored_items[index])
    return {"draft": stored_items[index], "form": form}


@app.post("/api/patient-drafts/{resume_code}/submit", status_code=201)
def submit_patient_draft(resume_code: str, payload: PatientDraftUpdate) -> dict[str, dict[str, Any]]:
    existing = find_patient_draft_by_code(resume_code)
    if not existing:
        raise HTTPException(status_code=404, detail="Resume draft not found.")

    form = next((item for item in get_templates() if item.get("id") == existing.get("formId")), None)
    if not form:
        raise HTTPException(status_code=400, detail="Original form template is no longer active.")

    scored_answers = add_calculated_scores(form["id"], payload.answers)
    validation_errors = validate_submission(form, scored_answers)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Submission is missing required information.",
                "details": validation_errors,
            },
        )

    now = utc_now()
    actor = audit_actor(None)
    event = audit_event(
        "patient_draft_submitted",
        actor,
        existing["id"],
        metadata={
            "formId": form["id"],
            "formName": form["name"],
            "formTemplateVersion": int(form.get("version", 1)),
            "resumeCode": existing.get("resumeCode"),
            "requiredMissingCount": 0,
        },
    )
    event["at"] = now
    set_fields = {
        "answers": scored_answers,
        "patientName": patient_name_from_answers(scored_answers),
        "patientDob": scored_answers.get("date_of_birth"),
        "status": "new",
        "updatedAt": now,
        "submittedAt": now,
        "submittedBy": actor,
    }
    review_submission = {**existing, **set_fields}
    set_fields["review"] = review_for_submission(review_submission)

    if mongo_db is not None:
        updated = submissions().find_one_and_update(
            {"id": existing["id"], "status": "draft"},
            {"$set": set_fields, "$push": {"audit": event}},
            return_document=ReturnDocument.AFTER,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Resume draft not found.")
        save_audit_event(event)
        submission = normalize_document(updated)
        submission["auditHistory"] = audit_history_for_submission(submission)
        return {"submission": submission}

    stored_items = get_local_submissions()
    index = next((i for i, item in enumerate(stored_items) if item.get("id") == existing["id"] and item.get("status") == "draft"), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="Resume draft not found.")
    stored_items[index] = {**stored_items[index], **set_fields}
    stored_items[index].setdefault("audit", []).append(event)
    save_local_submissions(stored_items)
    stored_items[index]["auditHistory"] = audit_history_for_submission(stored_items[index])
    return {"submission": stored_items[index]}


@app.patch("/api/submissions/{submission_id}")
def update_submission(
    submission_id: str,
    payload: SubmissionUpdate,
    request_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, dict[str, Any]]:
    allowed_statuses = {"draft", "new", "in-review", "needs-follow-up", "needs-patient-follow-up", "ready-for-chart", "complete"}
    if payload.status and payload.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Unsupported submission status.")

    now = utc_now()
    existing_submission: dict[str, Any] | None = None
    if mongo_db is not None:
        existing_submission = submissions().find_one({"id": submission_id})
        if existing_submission:
            existing_submission = normalize_document(existing_submission)
    else:
        existing_submission = next((item for item in get_local_submissions() if item.get("id") == submission_id), None)
    if not existing_submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    set_fields: dict[str, Any] = {"updatedAt": now}
    if payload.status:
        set_fields["status"] = payload.status
    scored_payload_answers = None
    if payload.answers is not None:
        scored_payload_answers = add_calculated_scores(existing_submission.get("formId", ""), payload.answers)
        set_fields["answers"] = scored_payload_answers

    previous_answers = existing_submission.get("answers") or {}
    changed_answer_keys = []
    if scored_payload_answers is not None:
        changed_answer_keys = sorted(
            key
            for key in set(previous_answers.keys()) | set(scored_payload_answers.keys())
            if previous_answers.get(key) != scored_payload_answers.get(key)
        )

    previous_status = existing_submission.get("status")
    next_status = payload.status or previous_status
    actor = audit_actor(request_user)
    review_activity = payload.answers is not None or next_status in {"in-review", "needs-follow-up", "needs-patient-follow-up", "ready-for-chart", "complete"}
    if review_activity:
        set_fields["reviewedBy"] = actor
        set_fields["reviewedAt"] = now
        set_fields["reviewLock"] = {
            "lockedBy": actor,
            "lockedAt": now,
            "expiresAt": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat().replace("+00:00", "Z"),
            "mode": "soft",
        }
    if next_status == "complete":
        set_fields["completedBy"] = actor
        set_fields["completedAt"] = now
    action = "submission_updated"
    if payload.status and payload.status != previous_status and payload.answers is None:
        action = "status_changed"
    elif payload.answers is not None:
        action = "staff_review_updated"

    audit_entry = audit_event(
        action,
        actor,
        submission_id,
        metadata={
            "formId": existing_submission.get("formId"),
            "formName": existing_submission.get("formName"),
            "formTemplateVersion": existing_submission.get("formTemplateVersion"),
            "previousStatus": previous_status,
            "newStatus": next_status,
            "statusChanged": next_status != previous_status,
            "answersUpdated": payload.answers is not None,
            "changedAnswerCount": len(changed_answer_keys),
            "changedAnswerKeys": changed_answer_keys[:50],
            "reviewedBy": actor,
            "reviewLockUpdated": review_activity,
        },
    )
    audit_entry["at"] = now
    review_submission = {**existing_submission, **set_fields}
    set_fields["review"] = review_for_submission(review_submission)
    if mongo_db is not None:
        result = submissions().find_one_and_update(
            {"id": submission_id},
            {
                "$set": set_fields,
                "$push": {"audit": audit_entry},
            },
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Submission not found.")
        save_audit_event(audit_entry)
        updated = normalize_document(result)
        updated["auditHistory"] = audit_history_for_submission(updated)
        return {"submission": updated}

    stored_items = get_local_submissions()
    index = next((i for i, item in enumerate(stored_items) if item.get("id") == submission_id), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if payload.status:
        stored_items[index]["status"] = payload.status
    if scored_payload_answers is not None:
        stored_items[index]["answers"] = scored_payload_answers
    if review_activity:
        stored_items[index]["reviewedBy"] = actor
        stored_items[index]["reviewedAt"] = now
        stored_items[index]["reviewLock"] = set_fields["reviewLock"]
    if next_status == "complete":
        stored_items[index]["completedBy"] = actor
        stored_items[index]["completedAt"] = now
    stored_items[index]["updatedAt"] = now
    stored_items[index]["review"] = review_for_submission(stored_items[index])
    stored_items[index].setdefault("audit", []).append(audit_entry)
    save_local_submissions(stored_items)
    stored_items[index]["auditHistory"] = audit_history_for_submission(stored_items[index])
    return {"submission": stored_items[index]}


@app.post("/api/submissions/{submission_id}/audit-events", status_code=201)
def create_submission_audit_event(
    submission_id: str,
    payload: AuditEventCreate,
    request_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, dict[str, Any]]:
    allowed_actions = {"pdf_exported", "submission_viewed", "staff_note_added"}
    if payload.action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Unsupported audit action.")

    existing_submission: dict[str, Any] | None = None
    if mongo_db is not None:
        existing_submission = submissions().find_one({"id": submission_id})
        if existing_submission:
            existing_submission = normalize_document(existing_submission)
    else:
        existing_submission = next((item for item in get_local_submissions() if item.get("id") == submission_id), None)
    if not existing_submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    actor = audit_actor(request_user)
    now = utc_now()
    event = audit_event(
        payload.action,
        actor,
        submission_id,
        metadata={
            "formId": existing_submission.get("formId"),
            "formName": existing_submission.get("formName"),
            "formTemplateVersion": existing_submission.get("formTemplateVersion"),
            **payload.metadata,
        },
    )
    event["at"] = now

    if mongo_db is not None:
        result = submissions().find_one_and_update(
            {"id": submission_id},
            {"$set": {"updatedAt": now}, "$push": {"audit": event}},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Submission not found.")
        save_audit_event(event)
        updated = normalize_document(result)
        updated["auditHistory"] = audit_history_for_submission(updated)
        return {"submission": updated}

    stored_items = get_local_submissions()
    index = next((i for i, item in enumerate(stored_items) if item.get("id") == submission_id), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="Submission not found.")
    stored_items[index]["updatedAt"] = now
    stored_items[index].setdefault("audit", []).append(event)
    save_local_submissions(stored_items)
    stored_items[index]["auditHistory"] = audit_history_for_submission(stored_items[index])
    return {"submission": stored_items[index]}


if FRONTEND_PUBLIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_PUBLIC_DIR), name="assets")


def no_cache_file_response(path: Path) -> FileResponse:
    return FileResponse(
        path,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )


@app.get("/")
def index() -> FileResponse:
    return no_cache_file_response(FRONTEND_PUBLIC_DIR / "index.html")


@app.get("/{path:path}")
def static_or_spa(path: str, request: Request) -> FileResponse:
    del request
    file_path = (FRONTEND_PUBLIC_DIR / path).resolve()
    if file_path.is_file() and FRONTEND_PUBLIC_DIR.resolve() in file_path.parents:
        return no_cache_file_response(file_path)
    return no_cache_file_response(FRONTEND_PUBLIC_DIR / "index.html")
