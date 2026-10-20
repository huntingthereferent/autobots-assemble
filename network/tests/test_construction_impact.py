"""Real B9 journal graphs exercise read-only proposed downstream review."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.handoff import HandoffEvent
from systems.workspace.workstation_construction import (
    LINK, WorkstationConstruction
)
from systems.workspace.construction_impact import preview_downstream_review


class CandidateImpactTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name)
        self.graph = WorkstationConstruction(self.data)
        self.goal = self.graph.goal(
            "Make checked world motion", provenance="user:goal")
        self.left = self.graph.candidate(
            self.goal, "Build a finite collision adapter",
            provenance="user:option-a", path_role="ALTERNATIVE")
        self.right = self.graph.candidate(
            self.goal, "Retain a separate finite solver",
            provenance="user:option-b", path_role="ALTERNATIVE")
        self.extra = self.graph.candidate(
            self.goal, "Separate graphics pipeline",
            provenance="user:graphics", path_role="ALTERNATIVE")

    def report(self, *changed):
        return preview_downstream_review(self.graph, self.goal, list(changed))

    def test_shared_prerequisite_sends_both_branches_to_review(self):
        upstream = self.graph.candidate(
            self.left, "Recheck original source geometry",
            provenance="user:shared")
        self.graph.propose_connection(
            upstream, self.right, reason="possible shared upstream requirement")
        before = (self.data / "runtime.jsonl").read_bytes()
        result = self.report(upstream)
        self.assertEqual(
            result["review_candidate_ids"],
            sorted([self.left, self.right, self.goal]))
        self.assertIn(self.extra, result["unreached_candidate_ids"])
        self.assertEqual(
            result["by_change"][upstream]["example_paths"][self.goal],
            [upstream, self.left, self.goal]
            if self.left < self.right else [upstream, self.right, self.goal])
        self.assertEqual(result["state"], "POSSIBLE_REVIEW_ONLY")
        self.assertFalse(result["current_native_evidence_reverified"])
        self.assertFalse(result["worker_execution_authorized"])
        self.assertFalse(result["wrote_events"])
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())
        self.assertEqual(self.report(upstream)["report_sha256"],
                         result["report_sha256"])

    def test_branched_alternatives_do_not_inherit_each_others_change(self):
        result = self.report(self.left)
        self.assertEqual(result["review_candidate_ids"], [self.goal])
        self.assertIn(self.right, result["unreached_candidate_ids"])
        self.assertIn(self.extra, result["unreached_candidate_ids"])

    def test_shared_downstream_is_explicit_not_forced_merge(self):
        result = self.report(self.left, self.right)
        self.assertEqual(result["review_candidate_ids"], [self.goal])
        self.assertEqual(result["shared_review_candidate_ids"], [self.goal])
        self.assertIn(self.extra, result["unreached_candidate_ids"])
        self.assertFalse(result["worker_execution_authorized"])

    def test_changed_root_no_downstream_and_no_proof_claim(self):
        result = self.report(self.goal)
        self.assertEqual(result["review_candidate_ids"], [])
        self.assertFalse(result["current_native_evidence_reverified"])

    def test_cross_goal_or_missing_node_refused(self):
        other_goal = self.graph.goal(
            "Unrelated analysis", provenance="user:other-goal")
        with self.assertRaisesRegex(ValueError, "outside original B9 goal"):
            self.report(other_goal)
        with self.assertRaisesRegex(ValueError, "outside original B9 goal"):
            self.report("unknown")
        with self.assertRaisesRegex(ValueError, "root goal"):
            preview_downstream_review(self.graph, self.left, [self.left])

    def test_duplicate_or_empty_or_excessive_change_list_refused(self):
        with self.assertRaisesRegex(ValueError, "bounded"):
            self.report()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.report(self.left, self.left)
        with self.assertRaisesRegex(ValueError, "bounded"):
            preview_downstream_review(self.graph, self.goal,
                                      [self.left] * 33)

    def test_corrupted_journal_cycle_fails_instead_of_partial_routes(self):
        # Real admission rejects cycles. Simulate a corrupted persisted LINK
        # without going through graph.propose_connection().
        rt = self.graph._runtime()
        rt.event_store.append(HandoffEvent.create(
            handoff_id=self.left, event_type=LINK,
            actor_id="malformed-journal-fixture",
            data={"upstream_id": self.goal,
                  "link_id": "fixture-corrupt-cycle",
                  "relation_state": "PROPOSED_NOT_OBSERVED",
                  "reason": "untrusted journal corruption"},
        ))
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.report(self.left)

    def test_graph_and_native_journal_stay_unchanged(self):
        before = (self.data / "runtime.jsonl").read_bytes()
        for candidate in [self.left, self.right, self.extra]:
            self.report(candidate)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())
        self.assertFalse((self.data / "preferred_editions.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
