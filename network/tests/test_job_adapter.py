from pathlib import Path
import unittest

from work.job_adapter import evaluate_job, load_all_jobs


class JobAdapterTests(unittest.TestCase):
    def test_all_job_records_are_admissible_without_rewriting_them(self):
        jobs_root = Path(__file__).resolve().parents[2] / "jobs"
        jobs = load_all_jobs(jobs_root)
        self.assertTrue(jobs, "the retained job ledger must not be empty")
        states = [evaluate_job(job) for job in jobs]
        self.assertLessEqual(
            {state.result.state for state in states},
            {"MOVE", "WALL", "UNKNOWN", "PARTIAL"},
        )
        self.assertTrue(any(state.result.state == "WALL" for state in states))
        self.assertTrue(any(state.result.state in {"MOVE", "PARTIAL"} for state in states))

    def test_blocked_job_does_not_emit_completion_relations(self):
        job = {
            "id": "JOB-X",
            "title": "blocked",
            "preferred_referent": "spec",
            "boundary": "do thing",
            "acceptance": "thing passes",
            "status": "blocked",
            "blockers": ["client file missing"],
            "result": "prototype exists",
        }
        state = evaluate_job(job)
        self.assertEqual(state.result.state, "WALL")
        self.assertEqual(state.result.outputs, ())


if __name__ == "__main__":
    unittest.main()
