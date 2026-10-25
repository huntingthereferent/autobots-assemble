"""Finite audit closure checks: no stale, skipped, or partial passes."""
import unittest

from systems.workspace.tracework_self_audit import evaluate, REQUIRED


class SelfAuditTests(unittest.TestCase):
    def test_current_head_both_pass_closes(self):
        runs = [{"name": n, "head_sha": "new", "status": "completed",
                 "conclusion": "success", "id": i, "created_at": "2026-10-25T18:00:00Z"}
                for i, n in enumerate(REQUIRED, 1)]
        self.assertTrue(evaluate("new", runs)["closed"])

    def test_old_head_does_not_close(self):
        runs = [{"name": n, "head_sha": "old", "status": "completed",
                 "conclusion": "success"} for n in REQUIRED]
        self.assertFalse(evaluate("new", runs)["closed"])

    def test_skipped_or_failed_latest_keeps_open(self):
        runs = [{"name": REQUIRED[0], "head_sha": "new", "status": "completed",
                 "conclusion": "success", "id": 1, "created_at": "2026-10-25T17:00:00Z"},
                {"name": REQUIRED[0], "head_sha": "new", "status": "completed",
                 "conclusion": "failure", "id": 2, "created_at": "2026-10-25T18:00:00Z"},
                {"name": REQUIRED[1], "head_sha": "new", "status": "completed",
                 "conclusion": "skipped", "id": 3, "created_at": "2026-10-25T18:00:00Z"}]
        self.assertFalse(evaluate("new", runs)["closed"])

    def test_in_progress_is_not_success(self):
        runs = [{"name": n, "head_sha": "new", "status": "in_progress",
                 "conclusion": None} for n in REQUIRED]
        self.assertFalse(evaluate("new", runs)["closed"])


if __name__ == "__main__":
    unittest.main()
