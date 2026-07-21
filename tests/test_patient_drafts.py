import unittest

from fastapi import HTTPException

from tests.helpers import IsolatedBackendState
import backend.main as api


class PatientDraftTests(unittest.TestCase):
    def setUp(self):
        self.state = IsolatedBackendState(api).start()

    def tearDown(self):
        self.state.stop()

    def test_patient_draft_submit_promotes_existing_record(self):
        draft_response = api.create_patient_draft(
            api.SubmissionCreate(
                formId="unit-test-intake",
                answers={"patient_name": "Mayo Demo", "date_of_birth": "2024-01-01", "consent": True},
                status="draft",
            )
        )
        draft = draft_response["draft"]

        submit_response = api.submit_patient_draft(
            draft["resumeCode"],
            api.PatientDraftUpdate(
                answers={"patient_name": "Mayo Demo Updated", "date_of_birth": "2024-01-01", "consent": True}
            ),
        )

        stored = api.get_local_submissions()
        self.assertEqual(len(stored), 1)
        self.assertEqual(submit_response["submission"]["id"], draft["id"])
        self.assertEqual(submit_response["submission"]["status"], "new")
        self.assertEqual(submit_response["submission"]["patientName"], "Mayo Demo Updated")
        self.assertEqual(stored[0]["id"], draft["id"])
        self.assertEqual(stored[0]["status"], "new")
        self.assertEqual([event["action"] for event in stored[0]["audit"]], ["patient_draft_saved", "patient_draft_submitted"])

    def test_patient_draft_submit_validates_required_fields(self):
        draft_response = api.create_patient_draft(
            api.SubmissionCreate(
                formId="unit-test-intake",
                answers={"patient_name": "Mayo Demo", "date_of_birth": "2024-01-01"},
                status="draft",
            )
        )

        with self.assertRaises(HTTPException) as raised:
            api.submit_patient_draft(
                draft_response["draft"]["resumeCode"],
                api.PatientDraftUpdate(answers={"patient_name": "Mayo Demo", "date_of_birth": "2024-01-01"}),
            )

        self.assertEqual(raised.exception.status_code, 422)
        stored = api.get_local_submissions()
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["status"], "draft")


if __name__ == "__main__":
    unittest.main()
