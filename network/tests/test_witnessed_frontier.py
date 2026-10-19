"""Contract tests for witnessed multi-task frontiers; fixture scores are not science."""
from dataclasses import replace
from hashlib import sha256
import unittest

from systems.workspace.witnessed_frontier import Trial, witnessed_frontier


def h(s):
    return sha256(s.encode()).hexdigest()


class VerifiedFrontierTests(unittest.TestCase):
    def setUp(self):
        self.ts = [
            self.row("alpha", "t1", 3), self.row("alpha", "t2", 1),
            self.row("beta", "t1", 1), self.row("beta", "t2", 3),
            self.row("gamma", "t1", 0), self.row("gamma", "t2", 0),
        ]
        self.native = {t.native_job_id for t in self.ts}
        self.score = {t.score_witness for t in self.ts}
        self.calls = []

    def row(self, c, task, value):
        job = f"native-{c}-{task}"
        return Trial(
            candidate=c, worker_id="finite", edition=c,
            source_sha256=h(c), setup_sha256=h("same-frozen-test-setup"),
            task_id=task, native_job_id=job, result_sha256=h(job),
            metric_id="independent-success-count", score=value,
            direction="maximize", result_witness="native:" + job,
            score_witness="score:" + job)

    def check_native(self, t):
        self.calls.append(("native", t.native_job_id))
        return t.native_job_id in self.native

    def check_score(self, t):
        self.calls.append(("score", t.native_job_id))
        return t.score_witness in self.score

    def report(self, trials=None, tasks=("t1", "t2"), **kwargs):
        return witnessed_frontier(
            trials=trials if trials is not None else self.ts,
            required_tasks=tasks,
            verify_native=kwargs.pop("verify_native", self.check_native),
            verify_score=kwargs.pop("verify_score", self.check_score),
            **kwargs,
        )

    def test_preserves_multiple_specialists_not_one_winner(self):
        result = self.report()
        self.assertEqual(result["verified_frontier"], ["alpha", "beta"])
        self.assertEqual(result["dominated_by"]["gamma"], ["alpha", "beta"])
        self.assertEqual(result["status"], "COMPLETE_FOR_DECLARED_TASKS")
        self.assertFalse(result["auto_selected"])
        self.assertFalse(result["auto_executed"])
        self.assertEqual(self.report()["report_sha256"], result["report_sha256"])

    def test_missing_or_failed_native_is_unknown_not_a_loss(self):
        self.native.remove("native-beta-t2")
        result = self.report()
        self.assertEqual(result["verified_frontier"], ["alpha"])
        self.assertEqual(result["unknown"], {"beta": ["t2"]})
        self.assertEqual(result["status"], "PROVISIONAL")
        self.assertNotIn(("score", "native-beta-t2"), self.calls)

    def test_missing_task_is_unknown(self):
        result = self.report(trials=self.ts[:-1])
        self.assertEqual(result["unknown"], {"gamma": ["t2"]})
        self.assertEqual(result["verified_frontier"], ["alpha", "beta"])

    def test_mismatched_test_setup_or_metric_or_direction_rejected(self):
        for field, value in (
            ("setup_sha256", h("other dataset")),
            ("metric_id", "other-score"),
            ("direction", "minimize"),
        ):
            changed = list(self.ts)
            changed[0] = replace(changed[0], **{field: value})
            with self.subTest(field=field), self.assertRaisesRegex(
                ValueError, "test setup or scoring metric"):
                self.report(trials=changed)

    def test_duplicate_jobs_candidates_and_unbounded_scores_rejected(self):
        for change in ({"native_job_id": self.ts[0].native_job_id},
                       {"score": float("nan")}, {"score": float("inf")},
                       {"score": True}, {"result_witness": self.ts[1].score_witness,
                                        "score_witness": self.ts[1].score_witness}):
            changed = list(self.ts)
            changed[1] = replace(changed[1], **change)
            with self.subTest(change=change), self.assertRaises((ValueError, TypeError)):
                self.report(trials=changed)

    def test_changed_source_within_candidate_rejected(self):
        changed = list(self.ts)
        changed[1] = replace(changed[1], source_sha256=h("other-source"))
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.report(trials=changed)

    def test_unverified_scores_not_ranked(self):
        self.score.remove("score:native-beta-t1")
        result = self.report()
        self.assertEqual(result["unknown"], {"beta": ["t1"]})
        self.assertEqual(result["verified_count"], 2)

    def test_verifier_output_must_be_a_boolean(self):
        with self.assertRaises(TypeError):
            self.report(verify_native=lambda t: "success")

    def test_requires_task_scope(self):
        with self.assertRaises(ValueError):
            self.report(tasks=())
        with self.assertRaises(ValueError):
            self.report(tasks=("t1", "t1"))
        with self.assertRaises(ValueError):
            self.report(tasks=("t1", "unobserved"))

    def test_minimize_is_supported_without_mixing_directions(self):
        changed = [replace(t, direction="minimize") for t in self.ts]
        result = self.report(trials=changed)
        self.assertEqual(result["verified_frontier"], ["gamma"])
        self.assertEqual(result["dominated_by"]["alpha"], ["gamma"])


if __name__ == "__main__":
    unittest.main()
