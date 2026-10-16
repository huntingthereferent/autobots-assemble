"""B6 walls against real reconstructed CP30 local source and finite native job.

The source-owner objects and B3 branch witness are fixtures. No external
owner identity, finite candidate edge, or genuine cross-lane collision is
inferred from those fixtures.
"""
from __future__ import annotations

import unittest

from network.tests import test_workstation_owner_native_observer as fixture
from systems.workspace.workstation_owner_source_wall import OwnerCandidateWall, WALL


@unittest.skipUnless((fixture.CP30_ROOT / "test_ab_chatbot_route_bound_task.py").is_file(),
                     "reconstructed native CP30 source required")
class B6WallTests(unittest.TestCase):
    def make_b4(self, providers=None):
        return fixture.B5NativeOwnerTests.make_b4(self, providers)

    def make(self, source_capture=None, binding=None):
        return fixture.B5NativeOwnerTests.make(
            self, source_capture=source_capture, binding=binding)

    def setUp(self):
        fixture.B5NativeOwnerTests.setUp(self)
        self.wall = OwnerCandidateWall(self.observer)

    def test_native_local_inspection_does_not_claim_new_worker_or_join(self):
        before = (self.data / "runtime.jsonl").read_bytes()
        state = self.wall.inspect(self.lane_id, "admitted")
        self.assertTrue(state["native_local_audit_current"])
        self.assertFalse(state["candidate_edge_proved"])
        self.assertFalse(state["external_owner_authenticated"])
        self.assertFalse(state["join_witnessed"])
        self.assertFalse(state["worker_admitted"])
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_preserved_wall_retains_source_native_evidence_without_new_lanes(self):
        self.observer.record(self.lane_id, task_name="admitted", allow_native_record=True)
        original = len(self.harness._runtime().snapshot())
        result = self.wall.preserve(self.lane_id, "admitted")
        self.assertTrue(result["recorded_new_event"])
        self.assertEqual(original, len(self.harness._runtime().snapshot()))
        records = [e for e in self.harness._runtime().event_store.for_handoff(self.lane_id)
                   if e.event_type == WALL]
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0].data["new_lane_admitted"])
        self.assertFalse(records[0].data["join_witnessed"])

    def test_restart_recheck_does_not_duplicate_wall_or_native_execution(self):
        self.observer.record(self.lane_id, task_name="admitted", allow_native_record=True)
        self.wall.preserve(self.lane_id, "admitted")
        before = (self.data / "runtime.jsonl").read_bytes()
        new_wall = OwnerCandidateWall(self.make())
        self.assertFalse(new_wall.preserve(self.lane_id, "admitted")["recorded_new_event"])
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_no_b5_audit_cannot_persist_wall(self):
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "must first be recorded"):
            self.wall.preserve(self.lane_id, "admitted")
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_revoked_native_pin_refuses_reuse(self):
        self.observer.record(self.lane_id, task_name="admitted", allow_native_record=True)
        self.left.first.recipient.registry.revoke(
            self.left.first.recipient._base._tokens[0])
        with self.assertRaises(ValueError):
            self.wall.preserve(self.lane_id, "admitted")

    def test_withdrawn_parent_witness_refuses_reuse(self):
        self.observer.record(self.lane_id, task_name="admitted", allow_native_record=True)
        self.witness_allowed = False
        with self.assertRaisesRegex(ValueError, "original parent movement"):
            self.wall.preserve(self.lane_id, "admitted")

    def test_missing_owner_candidate_binding_does_not_create_join(self):
        self.observer.record(self.lane_id, task_name="admitted", allow_native_record=True)
        self.allowed_bind = False
        with self.assertRaisesRegex(ValueError, "no separately bound"):
            self.wall.preserve(self.lane_id, "admitted")


if __name__ == "__main__":
    unittest.main()
