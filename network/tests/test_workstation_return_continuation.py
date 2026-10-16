"""B4: independently replay B3 native job before admitting a next observation.

Source-native finite subprocess and source-version verification run in the
ephemeral real workstation, not mocked. The starting A->child observation and
domain relation-provider policy are explicitly declared test fixtures.
"""
from __future__ import annotations

import unittest

from network.tests import test_workstation_native_feedback_integration as native_fixture
from systems.workspace.workstation_return_continuation import (
    WorkstationReturnContinuation, NextMovement, finite_prefilter_next)
from systems.workspace.process_handoff import WORKER_ID
from systems.workspace.finite_verifier import verdicts


class WorkstationB4Tests(unittest.TestCase):
    def setUp(self):
        native_fixture.RealNativeFeedbackTests.setUp(self)
        self.receipt = native_fixture.RealNativeFeedbackTests.advance(self)
        self.assertTrue(self.receipt.recorded_new_event)
        self.provider = {WORKER_ID: finite_prefilter_next}
        self.allow_next = True
        self.b4 = self.make_b4()

    def make_b4(self, providers=None):
        def independent_relation_witness(view, move):
            # Check the B3 scope and native finite required-edge verifier, not
            # that the return's own label merely matches a second label.
            if not self.allow_next or view.worker_id != WORKER_ID:
                return False
            if view.result["verdicts"] != verdicts(view.native_inputs):
                return False
            unsettled = [i for i, x in enumerate(view.result["verdicts"])
                         if x != "CONTRADICTED"]
            if not unsettled:
                return False
            return (move.kind == "BRANCH"
                    and move.capability == "owner-native-correspondence-witness"
                    and move.relation ==
                    "Acquire owner-native evidence for unresolved candidate " +
                    str(unsettled[0]) + " of job " + view.job_id)
        return WorkstationReturnContinuation(
            self.harness, providers=self.provider if providers is None else providers,
            verify_relation=independent_relation_witness)

    def test_real_native_return_derives_one_witness_linked_open_unstaffed(self):
        result = self.b4.derive_next(self.lane_id)
        self.assertEqual(result["state"], "NEXT_RELATION_RECORDED")
        obs = result["observation_id"]
        self.assertTrue(obs.startswith("whobs-"))
        self.assertEqual(self.b4.derive_next(self.lane_id),
                         {"state": "ALREADY_RECORDED", "observation_id": obs})
        movement = self.b4.next_pass()
        self.assertEqual(movement["born_coordination_lanes"], [])
        self.assertEqual(len(movement["open_unstaffed"]), 1)
        self.assertFalse(movement["execution_started"])
        self.assertFalse(movement["native_checkpoint_pass"])
        self.assertEqual(self.b4.next_pass()["open_unstaffed"], [])

    def test_capability_registration_creates_next_coordination_lane_not_a_running_bot(self):
        self.harness.worker_editions["owner-native-correspondence-witness"] = "candidate-edition-not-admission"
        self.b4.derive_next(self.lane_id)
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])
        result = self.b4.next_pass()
        self.assertEqual(len(result["born_coordination_lanes"]), 1)
        next_lane = self.harness._runtime().get(result["born_coordination_lanes"][0])
        self.assertEqual(next_lane.metadata["parents"],
                         [self.harness._runtime().get(self.lane_id).metadata["lane_id"]])
        self.assertEqual(self.harness._runtime().state(next_lane.handoff_id).status, "READY")
        self.assertEqual(next_lane.inputs["requested_capability"],
                         "owner-native-correspondence-witness")
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["native_checkpoint_pass"])
        self.assertEqual(self.b4.next_pass()["born_coordination_lanes"], [])

    def test_next_child_can_open_its_own_observation_without_rewriting_parent(self):
        self.harness.worker_editions["owner-native-correspondence-witness"] = "candidate-edition"
        self.b4.derive_next(self.lane_id)
        result = self.b4.next_pass()
        child_handoff_id = result["born_coordination_lanes"][0]
        child = self.harness._runtime().get(child_handoff_id)
        parent_before = len(self.harness._runtime().event_store.for_handoff(self.lane_id))
        observation_id = self.harness.observe(
            lane_id=child.metadata["lane_id"],
            kind="BRANCH", relation="separate child-observed hypothesis",
            capability="finite-required-edge-prefilter",
            witness_ref="fixture:unproved-child-hypothesis",
        )
        self.assertTrue(observation_id.startswith("whobs-"))
        self.assertEqual(len(self.harness._runtime().event_store.for_handoff(self.lane_id)),
                         parent_before)
        self.assertFalse(self.b4.verify_observation(
            next(o for o in self.harness._snapshot()[3] if o.id == observation_id)))
        self.assertEqual(self.b4.next_pass()["born_coordination_lanes"], [])

    def test_next_relations_are_rechecked_and_revocation_prevents_new_lane(self):
        self.harness.worker_editions["owner-native-correspondence-witness"] = "candidate-edition"
        self.b4.derive_next(self.lane_id)
        self.allow_next = False
        self.assertEqual(self.b4.next_pass()["born_coordination_lanes"], [])
        self.allow_next = True
        self.assertEqual(len(self.b4.next_pass()["born_coordination_lanes"]), 1)

    def test_original_movement_revocation_refuses_derivation_and_next_pass(self):
        self.b4.derive_next(self.lane_id)
        self.witness_allowed = False
        with self.assertRaisesRegex(ValueError, "original parent movement"):
            self.b4.derive_next(self.lane_id)
        self.harness.worker_editions["owner-native-correspondence-witness"] = "candidate"
        self.assertEqual(self.b4.next_pass()["born_coordination_lanes"], [])

    def test_tamper_native_worker_edition_after_completion_refuses_next(self):
        self.b4.derive_next(self.lane_id)
        assigned = self.harness.admit_native_help(self.lane_id)["native_help"]["child"]
        edition, _ = self.desk._read(WORKER_ID, assigned["version_id"])
        f = edition / "finite_required_edge_guard.py"
        f.write_text(f.read_text(encoding="utf8") + "\n# modified after verified return\n",
                     encoding="utf8")
        with self.assertRaises(ValueError):
            self.b4.derive_next(self.lane_id)
        self.harness.worker_editions["owner-native-correspondence-witness"] = "candidate"
        self.assertEqual(self.b4.next_pass()["born_coordination_lanes"], [])

    def test_unknown_worker_provider_refused_not_cross_domain(self):
        other_worker = {"game-w13-world-builder": finite_prefilter_next}
        b4 = self.make_b4(providers=other_worker)
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "no domain-native continuation provider"):
            b4.derive_next(self.lane_id)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_unverified_relation_does_not_write_any_observation(self):
        self.allow_next = False
        before = (self.data / "runtime.jsonl").read_bytes()
        self.assertEqual(self.b4.derive_next(self.lane_id),
                         {"state": "NO_ADMITTED_NEXT_RELATION", "observation_id": None})
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_invalid_domain_proposal_cannot_invent_a_connection(self):
        b4 = self.make_b4(providers={
            WORKER_ID: lambda v: NextMovement("shared", "relation-connector", "RELATION")})
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "invalid or unsupported"):
            b4.derive_next(self.lane_id)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_orphan_claim_without_admitted_derivation_cannot_create_lane(self):
        self.harness.observe(
            lane_id=self.harness._runtime().get(self.lane_id).metadata["lane_id"],
            kind="BRANCH", relation="forged derivation", capability="owner-native-correspondence-witness",
            witness_ref="native-return:" + "a"*64)
        self.harness.worker_editions["owner-native-correspondence-witness"] = "candidate"
        self.assertEqual(self.b4.next_pass()["born_coordination_lanes"], [])

    def test_recovery_after_restart_keeps_linked_observation_once(self):
        first = self.b4.derive_next(self.lane_id)
        before = (self.data / "runtime.jsonl").read_bytes()
        recovered = self.make_b4()
        self.assertEqual(recovered.derive_next(self.lane_id)["observation_id"],
                         first["observation_id"])
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())
        self.assertEqual(len(recovered.next_pass()["open_unstaffed"]), 1)


if __name__ == "__main__":
    unittest.main()
