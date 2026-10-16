"""B7: real B3 subprocess -> B4 verification -> bounded B2 continuation.

These tests use the merged repository's native finite worker and verifiers.
The initial witness is explicitly a synthetic B3 fixture; no external
owner or general correspondence edge is claimed.
"""
from __future__ import annotations
import unittest
from runtime.handoff import Handoff, HandoffEvent
from network.tests import test_workstation_return_continuation as original_b4
from systems.workspace.workstation_cycle import WorkstationCycle
from systems.workspace.process_handoff import WORKER_ID


class RealNativeCycleTests(unittest.TestCase):
    def make_b4(self, providers=None):
        return original_b4.WorkstationB4Tests.make_b4(self, providers)

    def setUp(self):
        original_b4.WorkstationB4Tests.setUp(self)
        self.cycle = WorkstationCycle(self.harness, return_continuation=self.b4)

    def _events(self):
        return self.harness._runtime().event_store.all()

    def test_native_return_advances_to_unstaffed_owner_need(self):
        self.assertEqual(self.harness._runtime().state(self.job_id).status, "COMPLETE")
        result = self.cycle.run()
        self.assertEqual(result.awaiting_source_owner, (self.lane_id,))
        self.assertIn(self.lane_id, result.derived_return_lanes)
        self.assertFalse(result.native_worker_executed)
        self.assertFalse(result.native_checkpoint_pass)
        self.assertEqual(self.harness._runtime().state(self.job_id).status, "COMPLETE")
        self.assertEqual(len([e for e in self._events() if e.event_type == "WORKSTATION_HELP_OPEN"
                              and e.handoff_id == self.lane_id]), 1)

    def test_second_invocation_is_duplicate_free(self):
        self.cycle.run()
        before = (self.data / "runtime.jsonl").read_bytes()
        self.assertEqual(self.cycle.run().journal_events_added, 0)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)
        self.assertEqual(sum(e.event_type == "STARTED" and e.handoff_id == self.job_id
                             for e in self._events()), 1)

    def test_restart_rebound_native_verifiers_preserve_history(self):
        self.cycle.run()
        before = (self.data / "runtime.jsonl").read_bytes()
        b4 = self.make_b4()
        result = WorkstationCycle(self.harness, return_continuation=b4).run()
        self.assertEqual(result.journal_events_added, 0)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_revoked_initial_observation_prevents_next_movement(self):
        self.witness_allowed = False
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "original parent movement"):
            self.cycle.run()
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_revoked_derived_relation_cannot_spawn_another_lane(self):
        self.allow_next = False
        before = (self.data / "runtime.jsonl").read_bytes()
        result = self.cycle.run()
        self.assertEqual(result.journal_events_added, 0)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_source_edition_mutation_fails_before_new_lane(self):
        assigned = self.harness.admit_native_help(self.lane_id)["native_help"]["child"]
        edition, _ = self.desk._read(WORKER_ID, assigned["version_id"])
        file = edition / "finite_required_edge_guard.py"
        file.write_text(file.read_text(encoding="utf-8") + "\n# negative source mutation\n", encoding="utf-8")
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaises(ValueError):
            self.cycle.run()
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_unrelated_system_cannot_become_b7_native_owner_request(self):
        runtime = self.harness._runtime()
        runtime.submit(Handoff("other-domain-handoff", "unrelated", "other", "other", "separate",
                               metadata={"source_system": "external-other-domain"}))
        runtime.event_store.append(HandoffEvent.create(
            handoff_id="other-domain-handoff", event_type="WORKSTATION_NATIVE_RESULT_VERIFIED",
            actor_id="outside-source", data={"job_id": "outside-native-worker"}))
        result = self.cycle.run()
        self.assertEqual(result.awaiting_source_owner, (self.lane_id,))
        self.assertNotIn("other-domain-handoff", result.derived_return_lanes)
        self.assertFalse(result.native_worker_executed)


if __name__ == "__main__":
    unittest.main()
