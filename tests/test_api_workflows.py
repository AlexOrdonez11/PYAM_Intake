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


if __name__ == "__main__":
    unittest.main()
