"""Native Cyclic Action Engine -> persistent Continuity handoff regression tests.

Exercise repository modules directly: no copied mathematical transition rule.
"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from runtime.journal import RuntimeJournal
from work.arc_like_maze.cyclic_action_continuation import CyclicActionContinuation
from work.arc_like_maze.continuity_handoff import (
    AB_CONJUGATE, B_CONJUGATE, B_DISTINGUISHED, CyclicActionHandoff,
)
from network.tests.test_arc_like_cyclic_action_continuation import negative, positive


class NativeContinuityHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.journal = self.root / "runtime.jsonl"
        self.archive = self.root / "native-witnesses"
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        self.bridge = CyclicActionHandoff(self.runtime, self.archive)

    @staticmethod
    def neg(budget):
        return CyclicActionContinuation.enter(*negative()).advance(budget)

    @staticmethod
    def pos(budget):
        return CyclicActionContinuation.enter(*positive()).advance(budget)

    def restart(self):
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        self.bridge = CyclicActionHandoff(self.runtime, self.archive)

    def test_unknown_is_preserved_as_unknown_not_equivalence(self):
        self.bridge.submit(self.neg(8), handoff_id="n8", claim=B_DISTINGUISHED)
        state = self.bridge.conclude("n8")
        self.assertEqual(state.status, "UNKNOWN")
        self.assertEqual(state.output["observed_through"], 8)
        self.assertFalse(state.output["bijection_verified"])
        self.assertEqual(self.bridge.recover("n8").status, "UNKNOWN")

    def test_negative_witness_completes_only_the_negative_B_claim(self):
        self.bridge.submit(self.neg(9), handoff_id="n9", claim=B_DISTINGUISHED)
        state = self.bridge.conclude("n9")
        self.assertEqual(state.status, "COMPLETE")
        self.assertEqual(state.output["native_status"], "DISTINGUISHED")
        self.assertEqual(state.output["distinguishing_depth"], 9)
        self.assertEqual(state.output["watched_scope"], "B_ONLY_ON_x0_EQ_2")

    def test_positive_witness_completes_only_restricted_B_claim(self):
        self.bridge.submit(self.pos(27), handoff_id="p27", claim=B_CONJUGATE)
        state = self.bridge.conclude("p27")
        self.assertEqual(state.status, "COMPLETE")
        self.assertTrue(state.output["bijection_verified"])
        self.assertEqual(state.output["state_count"], 81)
        self.assertEqual(state.output["does_not_establish"], "simultaneous A/B conjugacy")

    def test_full_AB_claim_is_rejected_even_when_B_conjugacy_is_verified(self):
        self.bridge.submit(self.pos(27), handoff_id="full", claim=AB_CONJUGATE)
        state = self.bridge.conclude("full")
        self.assertEqual(state.status, "BLOCKED")
        self.assertEqual(state.output["native_status"], "EQUIVALENT_FOR_B_ONLY")
        self.assertEqual(state.output["requested_claim"], AB_CONJUGATE)

    def test_wrong_mathematical_claim_is_blocked(self):
        self.bridge.submit(self.neg(9), handoff_id="wrong-positive", claim=B_CONJUGATE)
        self.bridge.submit(self.pos(27), handoff_id="wrong-negative", claim=B_DISTINGUISHED)
        self.assertEqual(self.bridge.conclude("wrong-positive").status, "BLOCKED")
        self.assertEqual(self.bridge.conclude("wrong-negative").status, "BLOCKED")

    def test_correct_evidence_labels_cannot_forge_complete(self):
        self.bridge.submit(self.pos(26), handoff_id="p26", claim=B_CONJUGATE)
        handoff = self.runtime.get("p26")
        fake = ExecutionResult(
            status="COMPLETE",
            output={"native_status": "EQUIVALENT_FOR_B_ONLY"},
            evidence=(EvidenceRecord(
                condition="native mathematical verification",
                kind="native-replay",
                source="CyclicActionContinuation.reenter",
                ref=handoff.inputs["native_witness_ref"],
                depth="verified",
            ),),
        )
        before = len(self.runtime.event_store.all())
        with self.assertRaises(ValueError):
            self.runtime.return_result("p26", actor_id="unverified", result=fake)
        self.assertEqual(len(self.runtime.event_store.all()), before)
        self.assertEqual(self.runtime.state("p26").status, "READY")
        self.assertEqual(self.bridge.conclude("p26").status, "UNKNOWN")

    def test_native_handoff_fails_closed_without_registered_verifier(self):
        self.bridge.submit(self.pos(27), handoff_id="p27", claim=B_CONJUGATE)
        bare = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        valid_result = self.bridge._expected_result(bare.get("p27"))
        with self.assertRaisesRegex(ValueError, "not registered"):
            bare.return_result("p27", actor_id="caller", result=valid_result)
        self.assertEqual(bare.state("p27").status, "READY")

    def test_snapshot_is_durable_and_replayed_after_real_journal_restart(self):
        self.bridge.submit(self.pos(27), handoff_id="p27", claim=B_CONJUGATE)
        self.assertEqual(self.bridge.conclude("p27").status, "COMPLETE")
        saved = self.runtime.get("p27")
        ref = saved.inputs["native_witness_ref"]
        self.assertTrue((self.archive / (ref + ".json")).exists())
        self.assertNotIn('"left_fixed"', self.journal.read_text(encoding="utf-8"))
        self.restart()
        resumed = self.bridge.recover("p27")
        self.assertEqual(resumed.status, "COMPLETE")
        self.assertEqual(resumed.evidence[0].ref, ref)
        self.assertTrue(resumed.output["bijection_verified"])

    def test_unknown_continues_without_require_complete_parent(self):
        first = self.neg(8)
        self.bridge.submit(first, handoff_id="n8", claim=B_DISTINGUISHED)
        self.assertEqual(self.bridge.conclude("n8").status, "UNKNOWN")
        self.restart()
        second = first.advance(9)
        self.bridge.submit(second, handoff_id="n9", claim=B_DISTINGUISHED,
                           previous_handoff_id="n8")
        self.assertIn("handoff:n8", self.runtime.get("n9").provenance)
        self.assertEqual(self.bridge.conclude("n9").status, "COMPLETE")
        self.restart()
        self.assertEqual(self.bridge.recover("n8").status, "UNKNOWN")
        self.assertEqual(self.bridge.recover("n9").output["distinguishing_depth"], 9)

    def test_reject_discontinuous_observation_ancestry(self):
        first = self.neg(8)
        self.bridge.submit(first, handoff_id="n8", claim=B_DISTINGUISHED)
        self.bridge.conclude("n8")
        independently_recomputed = self.neg(9)
        with self.assertRaisesRegex(ValueError, "prior mathematical observations"):
            self.bridge.submit(independently_recomputed, handoff_id="bad9",
                               claim=B_DISTINGUISHED, previous_handoff_id="n8")
        self.assertNotIn("bad9", self.runtime.snapshot())

    def test_modified_archive_is_detected_on_restart(self):
        self.bridge.submit(self.neg(9), handoff_id="n9", claim=B_DISTINGUISHED)
        self.bridge.conclude("n9")
        ref = self.runtime.get("n9").inputs["native_witness_ref"]
        path = self.archive / (ref + ".json")
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        self.restart()
        with self.assertRaisesRegex(ValueError, "stored witness content changed"):
            self.bridge.recover("n9")

    def test_missing_archive_cannot_be_treated_as_verified_recovery(self):
        self.bridge.submit(self.pos(27), handoff_id="p27", claim=B_CONJUGATE)
        self.bridge.conclude("p27")
        ref = self.runtime.get("p27").inputs["native_witness_ref"]
        (self.archive / (ref + ".json")).unlink()
        self.restart()
        with self.assertRaises(FileNotFoundError):
            self.bridge.recover("p27")

    def test_unrelated_generic_handoffs_remain_compatible(self):
        self.runtime.submit(Handoff(
            handoff_id="ordinary", referent="a task", from_actor="a",
            to_actor="b", required_relation="ordinary task",
            required_witnesses=("task evidence",),
            admissible_evidence={"task evidence": ("measurement",)},
        ))
        ordinary = self.runtime.return_result(
            "ordinary", actor_id="b",
            result=ExecutionResult(
                status="COMPLETE",
                evidence=(EvidenceRecord(
                    condition="task evidence", kind="measurement", source="test"
                ),),
            )
        )
        self.assertEqual(ordinary.status, "COMPLETE")


if __name__ == "__main__":
    unittest.main()
