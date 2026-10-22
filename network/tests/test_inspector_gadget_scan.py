import unittest
from systems.workspace.inspector_gadget_scan import build_report


class InspectorGadgetScanTests(unittest.TestCase):
    def test_groups_repeated_cancellations_without_claiming_defect(self):
        runs = [
            {"id": 1, "workflow_id": 7, "name": "ARC", "conclusion": "cancelled",
             "created_at": "2026-10-22T20:00:00Z", "html_url": "https://github.com/a/b/actions/runs/1"},
            {"id": 2, "workflow_id": 7, "name": "ARC", "conclusion": "cancelled",
             "created_at": "2026-10-22T20:01:00Z", "html_url": "https://github.com/a/b/actions/runs/2"},
            {"id": 3, "workflow_id": 8, "name": "NIH", "conclusion": "success",
             "created_at": "2026-10-22T20:02:00Z"},
        ]
        result = build_report(runs, "2026-10-22T19:00:00Z")
        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(result["findings"][0]["count"], 2)
        self.assertEqual(result["findings"][0]["kind"], "candidate")

    def test_recently_cancelled_old_run_is_included(self):
        runs = [{"id": 9, "workflow_id": 4, "name": "WORLD", "conclusion": "cancelled",
                 "created_at": "2026-10-20T00:00:00Z",
                 "updated_at": "2026-10-22T20:00:00Z"}]
        result = build_report(runs, "2026-10-22T19:00:00Z")
        self.assertEqual(result["findings"][0]["run_ids"], [9])
        self.assertEqual(result["findings"][0]["dispatch_state"], "awaiting_source_verification")

    def test_old_runs_excluded(self):
        runs = [{"id": 1, "workflow_id": 7, "name": "ARC", "conclusion": "failure",
                 "created_at": "2026-10-21T00:00:00Z"}]
        self.assertFalse(build_report(runs, "2026-10-22T00:00:00Z")["findings"])


if __name__ == "__main__":
    unittest.main()
