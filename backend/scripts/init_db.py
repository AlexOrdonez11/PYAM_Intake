from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.db_schema import COLLECTION_SCHEMAS, ensure_database_schema, seed_form_templates  # noqa: E402


def main() -> int:
    load_dotenv(ROOT / ".env")

    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB", "pyam_intake")
    if not mongo_uri:
        print("Missing MONGO_URI in .env or environment.")
        return 1

    templates_path = ROOT / "backend" / "data" / "form-templates.json"
    with templates_path.open("r", encoding="utf-8") as file:
        templates = json.load(file)

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    db = client[db_name]

    ensure_database_schema(db)
    changed_templates = seed_form_templates(db, templates, overwrite_existing=True)

    print(f"Connected to MongoDB database: {db_name}")
    print("Collections ready:")
    for name in COLLECTION_SCHEMAS:
        print(f"- {name}: {db[name].estimated_document_count()} documents")
    print(f"Form templates seeded/updated: {changed_templates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
