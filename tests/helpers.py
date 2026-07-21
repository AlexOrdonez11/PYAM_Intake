import os
import tempfile
from pathlib import Path
from unittest.mock import patch


os.environ["MONGO_URI"] = ""
os.environ["MONGODB_URI"] = ""


TEST_TEMPLATE = {
    "id": "unit-test-intake",
    "name": "Unit Test Intake",
    "category": "Tests",
    "description": "Small test template.",
    "estimatedMinutes": 1,
    "version": 1,
    "status": "active",
    "sections": [
        {
            "title": "Patient",
            "fields": [
                {"id": "patient_name", "label": "Patient name", "type": "text", "required": True},
                {"id": "date_of_birth", "label": "Date of birth", "type": "date", "required": True},
                {"id": "consent", "label": "Consent", "type": "checkbox", "required": True},
            ],
        }
    ],
}


class IsolatedBackendState:
    def __init__(self, api_module, templates=None):
        self.api = api_module
        self.templates = templates or [TEST_TEMPLATE]
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)
        self.patches = [
            patch.object(api_module, "mongo_db", None),
            patch.object(api_module, "SUBMISSIONS_FILE", temp_path / "submissions.json"),
            patch.object(api_module, "USERS_FILE", temp_path / "users.json"),
            patch.object(api_module, "TEMPLATES_FILE", temp_path / "form-templates.json"),
            patch.object(api_module, "get_templates", return_value=self.templates),
        ]

    def start(self):
        for item in self.patches:
            item.start()
        return self

    def stop(self):
        for item in reversed(self.patches):
            item.stop()
        self.temp_dir.cleanup()
