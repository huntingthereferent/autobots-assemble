import unittest
from systems.workspace.audit_cancelled_run import cancellation_receipt


class CancellationTests(unittest.TestCase):
    def test_cancelled_run_generates_candidate_not_defect(self):
        event = {"action": "completed", "workflow_run": {
            "id": 123, "name": "protocol-tests", "conclusion": "cancelled",
            "html_url": "https://github.com/o/r/actions/runs/123",
            "head_sha": "abc", "run_attempt": 1}}
        result = cancellation_receipt(event)
        finding = result["findings"][0]
        self.assertEqual(finding["id"], "workflow-cancel-123")
        self.assertEqual(finding["kind"], "candidate")
        self.assertEqual(finding["state"], "awaiting_verification")
        self.assertEqual(finding["workflow_run"]["head_sha"], "abc")

    def test_success_does_not_trigger(self):
        with self.assertRaises(ValueError):
            cancellation_receipt({"action": "completed", "workflow_run": {
                "id": 123, "conclusion": "success",
                "html_url": "https://github.com/o/r/actions/runs/123"}})

    def test_missing_source_rejected(self):
        with self.assertRaises(ValueError):
            cancellation_receipt({"action": "completed", "workflow_run": {
                "id": 123, "conclusion": "cancelled"}})


if __name__ == "__main__":
    unittest.main()
