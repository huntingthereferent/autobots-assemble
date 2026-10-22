"""Backward wall contract: a green run alone cannot close a failed obligation."""
import unittest

from systems.workspace.inspector_gadget_wall import chase, evaluate_wall


def run(id=10, conclusion="failure", workflow_id=5, branch="main", event="push"):
    return {"id": id, "workflow_id": workflow_id, "name": "NIH Phase 2",
            "conclusion": conclusion, "event": event,
            "head_branch": branch, "created_at": f"2026-10-22T20:{id:02d}:00Z"}


def jobs(job_id=100, step="Owner evidence", outcome="failure", job="source tests"):
    return {"total_count": 1, "jobs": [{
        "id": job_id, "name": job, "steps": [
            {"name": step, "conclusion": outcome},
        ],
    }]}


def history(*items):
    return {"total_count": len(items), "workflow_runs": list(items)}


class WallTests(unittest.TestCase):
    def test_named_failed_step_is_the_wall(self):
        w = evaluate_wall(run(), jobs(), history())
        self.assertEqual(w["kind"], "failed_step")
        self.assertEqual(w["failed_job"], "source tests")
        self.assertEqual(w["failed_step"], "Owner evidence")
        self.assertEqual(w["source_job_id"], 100)
        self.assertEqual(w["wall_state"], "chasing")
        self.assertEqual(w["next_movement"], "inspect_original_failure")
        self.assertTrue(w["owner_validation_required"])

    def test_later_green_from_unrelated_branch_is_not_exit(self):
        w = evaluate_wall(run(), jobs(), history(
            run(11, "success", branch="other"),
            run(12, "success", workflow_id=900),
            run(13, "success", event="pull_request")))
        self.assertEqual(w["later_same_obligation_runs"], 0)
        self.assertIsNone(w["later_success_run_id"])
        self.assertEqual(w["wall_state"], "chasing")

    def test_matching_step_pass_is_observed_not_a_claim_of_repair(self):
        w = evaluate_wall(run(), jobs(), history(run(11, "success")),
                          jobs(200, "Owner evidence", "success"))
        self.assertEqual(w["later_success_run_id"], 11)
        self.assertEqual(w["wall_state"], "obligation_pass_observed")
        self.assertEqual(w["next_movement"], "request_owning_lane_witness")
        self.assertTrue(w["owner_validation_required"])

    def test_unrelated_step_pass_cannot_clear_wall(self):
        w = evaluate_wall(run(), jobs(), history(run(11, "success")),
                          jobs(200, "Other step", "success"))
        self.assertEqual(w["wall_state"], "chasing")
        self.assertEqual(w["next_movement"], "reproduce_missing_or_failed_step")

    def test_cancellation_wall_is_not_a_defect(self):
        w = evaluate_wall(run(conclusion="cancelled"), jobs(outcome="success"),
                          history(run(11, "success")))
        self.assertEqual(w["kind"], "cancellation_or_supersession")
        self.assertEqual(w["wall_state"], "superseded_candidate")
        self.assertEqual(w["next_movement"], "verify_expected_supersession")

    def test_bad_job_data_is_not_made_up(self):
        w = evaluate_wall(run(), {"total_count": 0, "jobs": []}, history())
        self.assertEqual(w["kind"], "incident_without_step_witness")
        self.assertEqual(w["next_movement"], "locate_failed_job_or_external_boundary")

    def test_real_chase_reads_owner_wall_then_followup_step(self):
        requested = []
        def read_job(repo, run_id, token):
            requested.append(("jobs", run_id))
            return jobs(outcome="failure" if run_id == 10 else "success")
        def read_later(repo, workflow_id, token):
            requested.append(("history", workflow_id))
            return history(run(11, "success"))
        w = chase(run(), repo="o/r", token="test", job_reader=read_job,
                  history_reader=read_later)
        self.assertEqual(requested, [("jobs", 10), ("history", 5), ("jobs", 11)])
        self.assertEqual(w["wall_state"], "obligation_pass_observed")

    def test_no_followup_does_not_make_extra_reads(self):
        requests = []
        def read_job(repo, run_id, token):
            requests.append(run_id)
            return jobs()
        w = chase(run(), repo="o/r", token="test", job_reader=read_job,
                  history_reader=lambda *a: history())
        self.assertEqual(requests, [10])
        self.assertEqual(w["wall_state"], "chasing")


if __name__ == "__main__":
    unittest.main()
