from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import bcrypt
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.collection import Collection


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
FRONTEND_PUBLIC_DIR = ROOT / "frontend" / "public"
TEMPLATES_FILE = DATA_DIR / "form-templates.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
USERS_FILE = DATA_DIR / "users.json"

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "pyam_intake")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-for-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5177,http://127.0.0.1:5177").split(",")
    if origin.strip()
]

mongo_client: MongoClient | None = MongoClient(MONGODB_URI) if MONGODB_URI else None
mongo_db = mongo_client[MONGODB_DB] if mongo_client is not None else None


app = FastAPI(
    title="PYAM Intake API",
    version="0.2.0",
    description="FastAPI backend for collecting clinic intake forms.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_indexes() -> None:
    if mongo_db is None:
        return
    users().create_index([("email", ASCENDING)], unique=True)
    submissions().create_index([("createdAt", ASCENDING)])


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


class SubmissionCreate(BaseModel):
    form_id: str | None = Field(default=None, alias="formId")
    answers: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class SubmissionUpdate(BaseModel):
    status: str | None = None


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


def submissions() -> Collection:
    if mongo_db is None:
        raise RuntimeError("MongoDB is not configured.")
    return mongo_db["submissions"]


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(user.get("_id") or user.get("id")),
        "email": user["email"],
        "name": user.get("name") or user["email"].split("@")[0],
        "role": user.get("role", "staff"),
    }


def normalize_document(document: dict[str, Any]) -> dict[str, Any]:
    item = dict(document)
    if "_id" in item:
        item["id"] = str(item.pop("_id"))
    return item


def get_templates() -> list[dict[str, Any]]:
    return read_json(TEMPLATES_FILE, [])


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


def create_user(payload: RegisterRequest) -> dict[str, Any]:
    now = utc_now()
    user = {
        "id": str(uuid4()),
        "email": payload.email.lower(),
        "name": payload.name,
        "role": "staff",
        "passwordHash": bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "createdAt": now,
        "updatedAt": now,
    }
    if mongo_db is not None:
        users().insert_one(user)
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


def flatten_template_fields(template: dict[str, Any]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for section in template.get("sections", []):
        for field in section.get("fields", []):
            fields.append({**field, "section": section.get("title", "")})
    return fields


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


def patient_name_from_answers(answers: dict[str, Any]) -> str:
    explicit_name = answers.get("patient_name") or answers.get("child_name")
    if explicit_name:
        return str(explicit_name)

    first_last = " ".join(
        str(part) for part in [answers.get("patient_first_name"), answers.get("patient_last_name")] if part
    )
    return first_last or "Unnamed patient"


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "storage": "mongodb" if mongo_db is not None else "local-json",
        "timestamp": utc_now(),
    }


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterRequest) -> dict[str, Any]:
    if find_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="An account already exists for this email.")
    user = create_user(payload)
    return {"user": public_user(user), "accessToken": create_access_token(user)}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    user = find_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"user": public_user(user), "accessToken": create_access_token(user)}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": public_user(user)}


@app.get("/api/forms")
def list_forms() -> dict[str, list[dict[str, Any]]]:
    return {"forms": get_templates()}


@app.get("/api/forms/{form_id}")
def get_form(form_id: str) -> dict[str, dict[str, Any]]:
    form = next((template for template in get_templates() if template.get("id") == form_id), None)
    if not form:
        raise HTTPException(status_code=404, detail="Form template not found.")
    return {"form": form}


@app.get("/api/submissions")
def list_submissions(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, list[dict[str, Any]]]:
    del user
    if mongo_db is not None:
        stored_items = [normalize_document(item) for item in submissions().find()]
    else:
        stored_items = get_local_submissions()

    summary = []
    for submission in stored_items:
        item = {key: value for key, value in submission.items() if key not in {"answers", "audit"}}
        summary.append(item)

    summary.sort(key=lambda item: item.get("createdAt", ""), reverse=True)
    return {"submissions": summary}


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

    validation_errors = validate_submission(template, payload.answers)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Submission is missing required information.",
                "details": validation_errors,
            },
        )

    now = utc_now()
    actor = public_user(request_user) if request_user else {"id": "patient", "email": "patient@local", "role": "patient"}
    submission = {
        "id": str(uuid4()),
        "formId": template["id"],
        "formName": template["name"],
        "category": template["category"],
        "patientName": patient_name_from_answers(payload.answers),
        "patientDob": payload.answers.get("date_of_birth"),
        "status": "new",
        "createdAt": now,
        "updatedAt": now,
        "submittedBy": actor,
        "answers": payload.answers,
        "audit": [{"at": now, "action": "created", "by": actor["id"]}],
    }

    if mongo_db is not None:
        submissions().insert_one(dict(submission))
    else:
        stored_items = get_local_submissions()
        stored_items.append(submission)
        save_local_submissions(stored_items)
    return {"submission": submission}


@app.patch("/api/submissions/{submission_id}")
def update_submission(
    submission_id: str,
    payload: SubmissionUpdate,
    request_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, dict[str, Any]]:
    allowed_statuses = {"new", "in-review", "complete", "needs-follow-up"}
    if payload.status and payload.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Unsupported submission status.")

    now = utc_now()
    audit_entry = {"at": now, "action": "updated", "by": request_user["id"], "status": payload.status}
    if mongo_db is not None:
        result = submissions().find_one_and_update(
            {"id": submission_id},
            {
                "$set": {"status": payload.status, "updatedAt": now},
                "$push": {"audit": audit_entry},
            },
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Submission not found.")
        return {"submission": normalize_document(result)}

    stored_items = get_local_submissions()
    index = next((i for i, item in enumerate(stored_items) if item.get("id") == submission_id), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail="Submission not found.")

    stored_items[index]["status"] = payload.status or stored_items[index].get("status", "new")
    stored_items[index]["updatedAt"] = now
    stored_items[index].setdefault("audit", []).append(audit_entry)
    save_local_submissions(stored_items)
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
