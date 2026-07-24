from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


ROOT = Path(__file__).resolve().parents[2]
FORM_ID = "well-child-visit"


def main() -> int:
    load_dotenv(ROOT / ".env")

    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB", "pyam_intake")
    if not mongo_uri:
        print("Missing MONGO_URI in .env or environment.")
        return 1

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    result = client[db_name]["form_templates"].delete_many({"id": FORM_ID})
    print(f"Deleted {result.deleted_count} form_templates document(s) with id {FORM_ID}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
