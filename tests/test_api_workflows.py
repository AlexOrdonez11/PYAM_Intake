import unittest

from fastapi import HTTPException

from tests.helpers import IsolatedBackendState
import backend.main as api


class ApiWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.state = IsolatedBackendState(api).start()

    def tearDown(self):
        self.state.stop()

    def test_auth_register_login_and_me_flow(self):
        bootstrap = api.bootstrap_status()
        self.assertTrue(bootstrap["needsFirstAdmin"])

        registered = api.register(api.RegisterRequest(email="admin@example.com", password="super-secret", name="Admin User"))
        self.assertEqual(registered["user"]["role"], "admin")
        self.assertTrue(registered["accessToken"])
        self.assertFalse(api.bootstrap_status()["needsFirstAdmin"])

        with self.assertRaises(HTTPException) as blocked:
            api.register(api.RegisterRequest(email="second@example.com", password="super-secret", name="Second User"))
        self.assertEqual(blocked.exception.status_code, 403)

        login = api.login(api.LoginRequest(email="ADMIN@example.com", password="super-secret"))
        self.assertEqual(login["user"]["email"], "admin@example.com")

        current_user = api.get_current_user(f"Bearer {login['accessToken']}")
        self.assertEqual(current_user["email"], "admin@example.com")
        self.assertEqual(api.me(current_user)["user"]["name"], "Admin User")

        with self.assertRaises(HTTPException) as failed_login:
            api.login(api.LoginRequest(email="admin@example.com", password="wrong-password"))
        self.assertEqual(failed_login.exception.status_code, 401)

    def test_forms_list_uses_active_templates(self):
        response = api.list_forms()

        self.assertEqual(len(response["forms"]), 1)
        self.assertEqual(response["forms"][0]["id"], "unit-test-intake")

    def test_create_submission_validates_and_lists_summary_and_detail(self):
        submission_response = api.create_submission(
            api.SubmissionCreate(
                formId="unit-test-intake",
                answers={"patient_name": "Mayo Demo", "date_of_birth": "2024-01-01", "consent": True},
            ),
            request_user=None,
        )
        submission = submission_response["submission"]

        self.assertEqual(submission["status"], "new")
        self.assertEqual(submission["patientName"], "Mayo Demo")
        self.assertEqual(submission["submittedBy"]["role"], "patient")

        summary_response = api.list_submissions(
            user={"id": "staff-1", "email": "staff@example.com", "role": "staff"},
            limit=10,
            cursor=None,
            status_filter=None,
            form_id=None,
            review_filter=None,
            search="mayo",
            sort="priority",
        )
        self.assertEqual(summary_response["totalMatched"], 1)
        self.assertEqual(summary_response["submissions"][0]["id"], submission["id"])
        self.assertNotIn("answers", summary_response["submissions"][0])

        detail_response = api.get_submission(
            submission["id"],
            user={"id": "staff-1", "email": "staff@example.com", "role": "staff"},
        )
        self.assertEqual(detail_response["submission"]["answers"]["patient_name"], "Mayo Demo")
        self.assertEqual(detail_response["submission"]["auditHistory"][0]["action"], "submission_created")

    def test_create_submission_rejects_missing_required_answers(self):
        with self.assertRaises(HTTPException) as raised:
            api.create_submission(
                api.SubmissionCreate(
                    formId="unit-test-intake",
                    answers={"patient_name": "Mayo Demo", "date_of_birth": "2024-01-01"},
                ),
                request_user=None,
            )

        self.assertEqual(raised.exception.status_code, 422)
        self.assertEqual(api.get_local_submissions(), [])

    def test_create_submission_does_not_require_internal_or_staff_fields_from_patient(self):
        self.state.stop()
        internal_template = {
            "id": "internal-field-test",
            "name": "Internal Field Test",
            "category": "Tests",
            "status": "active",
            "version": 1,
            "sections": [
                {
                    "title": "Patient and Visit Information",
                    "fields": [
                        {"id": "patient_name", "label": "Patient name", "type": "text", "required": True},
                        {"id": "date_of_birth", "label": "Date of birth", "type": "date", "required": True},
                        {"id": "baby_id", "label": "Baby ID #", "type": "text", "required": True},
                        {"id": "staff_initials", "label": "Staff initials", "type": "text", "required": True, "staffOnly": True},
                    ],
                }
            ],
        }
        self.state = IsolatedBackendState(api, templates=[internal_template]).start()

        response = api.create_submission(
            api.SubmissionCreate(
                formId="internal-field-test",
                answers={"patient_name": "Mayo Demo", "date_of_birth": "2024-01-01"},
            ),
            request_user=None,
        )

        self.assertEqual(response["submission"]["status"], "new")
        self.assertEqual(response["submission"]["patientName"], "Mayo Demo")

    def test_delete_form_draft_removes_local_draft_template(self):
        draft_template = {
            "id": "draft-test",
            "name": "Draft Test",
            "category": "Tests",
            "status": "draft",
            "version": 2,
            "sections": [],
        }
        active_template = {**draft_template, "status": "active", "version": 1}
        api.write_json(api.TEMPLATES_FILE, [active_template, draft_template])

        response = api.delete_form_draft(
            "draft-test",
            admin={"id": "admin-1", "email": "admin@example.com", "name": "Admin", "role": "admin"},
        )

        self.assertEqual(response.status_code, 204)
        templates = api.read_json(api.TEMPLATES_FILE, [])
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0]["status"], "active")

        with self.assertRaises(HTTPException) as raised:
            api.delete_form_draft(
                "draft-test",
                admin={"id": "admin-1", "email": "admin@example.com", "name": "Admin", "role": "admin"},
            )
        self.assertEqual(raised.exception.status_code, 404)

    def test_template_draft_can_be_saved_repeatedly_and_published(self):
        active_template = {
            "id": "publish-test",
            "name": "Publish Test",
            "category": "Tests",
            "status": "active",
            "version": 1,
            "sections": [{"title": "Patient", "fields": []}],
        }
        api.write_json(api.TEMPLATES_FILE, [active_template])
        admin = {"id": "admin-1", "email": "admin@example.com", "name": "Admin", "role": "admin"}

        first_draft = api.update_form_template(
            "publish-test",
            api.FormTemplateUpdate(template={**active_template, "name": "Publish Test Draft"}, publish=False),
            admin=admin,
        )["form"]
        second_draft = api.update_form_template(
            "publish-test",
            api.FormTemplateUpdate(template={**first_draft, "description": "Edited again"}, publish=False),
            admin=admin,
        )["form"]

        self.assertEqual(first_draft["version"], second_draft["version"])
        self.assertEqual(len([item for item in api.read_json(api.TEMPLATES_FILE, []) if item.get("status") == "draft"]), 1)

        published = api.update_form_template(
            "publish-test",
            api.FormTemplateUpdate(template=second_draft, publish=True),
            admin=admin,
        )["form"]
        templates = api.read_json(api.TEMPLATES_FILE, [])

        self.assertEqual(published["status"], "active")
        self.assertEqual(published["version"], second_draft["version"])
        self.assertEqual(len([item for item in templates if item.get("status") == "draft"]), 0)
        self.assertEqual(len([item for item in templates if item.get("status") == "active"]), 1)
        self.assertEqual(len({(item["id"], item["version"]) for item in templates}), len(templates))

    def test_published_template_history_keeps_current_and_previous_only(self):
        active_template = {
            "id": "history-test",
            "name": "History Test",
            "category": "Tests",
            "status": "active",
            "version": 1,
            "sections": [{"title": "Patient", "fields": []}],
        }
        api.write_json(api.TEMPLATES_FILE, [active_template])
        admin = {"id": "admin-1", "email": "admin@example.com", "name": "Admin", "role": "admin"}

        version_two = api.update_form_template(
            "history-test",
            api.FormTemplateUpdate(template={**active_template, "description": "Second"}, publish=True),
            admin=admin,
        )["form"]
        version_three = api.update_form_template(
            "history-test",
            api.FormTemplateUpdate(template={**version_two, "description": "Third"}, publish=True),
            admin=admin,
        )["form"]
        templates = [item for item in api.read_json(api.TEMPLATES_FILE, []) if item.get("id") == "history-test"]

        self.assertEqual(version_three["version"], 3)
        self.assertEqual(len(templates), 2)
        self.assertEqual([item["status"] for item in sorted(templates, key=lambda item: item["version"])], ["archived", "active"])
        self.assertEqual([item["version"] for item in sorted(templates, key=lambda item: item["version"])], [2, 3])


if __name__ == "__main__":
    unittest.main()
