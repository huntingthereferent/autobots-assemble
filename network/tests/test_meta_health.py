"""Regression tests: open workflow check counts return to zero on later passes."""
import datetime as dt
import unittest

from systems.workspace.meta_health import update_status, collect, SCHEMA

NOW = dt.datetime(2026, 10, 22, 18, 0, tzinfo=dt.timezone.utc)


def run(run_id, conclusion, workflow_id=101, at="2026-10-22T17:00:00Z"):
    return {
        "id": run_id, "workflow_id": workflow_id,
        "name": "Research contract", "status": "completed", "conclusion": conclusion,
        "updated_at": at, "run_attempt": 1,
        "head_branch": "main", "created_at": at,
    }


class HealthTests(unittest.TestCase):
    def test_failure_open_then_success_clears_to_zero(self):
        state = {}
        update_status(state, run(1, "failure", at="2026-10-22T16:00:00Z"), "o/r")
        self.assertEqual(state["101"]["state"], "needs_attention")
        update_status(state, run(2, "success", at="2026-10-22T17:00:00Z"), "o/r")
        self.assertEqual(state["101"]["state"], "clear")

    def test_cancelled_and_skipped_do_not_create_or_clear_failure(self):
        state = {}
        update_status(state, run(1, "failure"), "o/r")
        update_status(state, run(2, "cancelled", at="2026-10-22T17:30:00Z"), "o/r")
        update_status(state, run(3, "skipped", at="2026-10-22T17:35:00Z"), "o/r")
        self.assertEqual(state["101"]["state"], "needs_attention")

    def test_unrelated_workflow_success_does_not_clear(self):
        state = {}
        update_status(state, run(1, "failure", workflow_id=101), "o/r")
        update_status(state, run(2, "success", workflow_id=102), "o/r")
        self.assertEqual(state["101"]["state"], "needs_attention")
        self.assertEqual(state["102"]["state"], "clear")

    def test_newer_outcome_is_not_overwritten_by_delayed_older_job(self):
        state = {}
        update_status(state, run(2, "success", at="2026-10-22T17:30:00Z"), "o/r")
        update_status(state, run(1, "failure", at="2026-10-22T16:00:00Z"), "o/r")
        self.assertEqual(state["101"]["state"], "clear")

    def test_complete_current_inventory_counts_only_latest_bad_active_checks(self):
        registry = '{"schema":"meta-workstation/registry-v1","nodes":[{"id":"A","repo":"owner-a/repo"},{"id":"B","repo":"owner-b/repo"}]}'
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            f = Path(folder) / "registry.json"
            f.write_text(registry)
            def getter(path):
                if "/actions/workflows?" in path:
                    return {"workflows":[{"id":101,"state":"active"},{"id":102,"state":"disabled_manually"}]}
                if "/actions/runs?created=" in path:
                    if "owner-a" in path:
                        events = [run(1,"failure",workflow_id=101,at="2026-10-22T15:00:00Z"),
                                  run(2,"success",workflow_id=101,at="2026-10-22T16:00:00Z"),
                                  run(3,"failure",workflow_id=102,at="2026-10-22T16:00:00Z")]
                    else:
                        events = [run(4,"failure",workflow_id=101,at="2026-10-22T17:00:00Z")]
                    return {"total_count":len(events),"workflow_runs":events}
                if "/actions/runs/" in path:
                    return run(4,"failure",workflow_id=101,at="2026-10-22T17:00:00Z")
                raise ValueError(path)
            result = collect(None, f, now=NOW, getter=getter)
            self.assertTrue(result["all_sources"])
            self.assertEqual(result["nodes"]["A"]["open_count"], 0)
            self.assertEqual(result["nodes"]["B"]["open_count"], 1)
            self.assertEqual(result["summary"]["open_count"], 1)

    def test_unavailable_source_never_claims_0(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            f = Path(folder) / "registry.json"
            f.write_text('{"schema":"meta-workstation/registry-v1","nodes":[{"id":"A","repo":"x/y"},{"id":"B","repo":"q/z"}]}')
            result = collect(None, f, NOW, getter=lambda _: (_ for _ in ()).throw(RuntimeError("rate limit")))
            self.assertFalse(result["all_sources"])
            self.assertIsNone(result["summary"])


if __name__ == "__main__":
    unittest.main()
