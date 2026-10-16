"""B5 CP30 owner-native integration: actual live native task objects in CI.

The CP30 source is reconstructed from the preserved repository and uses its
*synthetic local source-owner fixtures*. The candidate-to-task binding function
is also a declared test fixture. This does not authenticate an outside owner
or prove a new correspondence edge.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

from network.tests import test_workstation_return_continuation as b4_fixture
from systems.workspace.workstation_owner_native_observer import WorkstationOwnerNativeObserver
from systems.workspace.process_handoff import WORKER_ID

CP30_ROOT = Path(os.environ.get("CP30_NATIVE_SOURCE_DIR", "/nonexistent-cp30")).resolve()
if CP30_ROOT.is_dir() and str(CP30_ROOT) not in sys.path:
    sys.path.insert(0, str(CP30_ROOT))


@unittest.skipUnless((CP30_ROOT / "test_ab_chatbot_route_bound_task.py").is_file(),
                     "reconstructed native CP30 source required")
class B5NativeOwnerTests(unittest.TestCase):
    def make_b4(self, providers=None):
        return b4_fixture.WorkstationB4Tests.make_b4(self, providers)

    def setUp(self):
        b4_fixture.WorkstationB4Tests.setUp(self)
        self.b4.derive_next(self.lane_id)
        result = self.b4.next_pass()
        self.assertEqual(len(result["open_unstaffed"]), 1)
        from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
        self.owner_helper = RouteBoundTaskTests("runTest")
        self.refresh, self.comparison, self.left, self.right, *_ = self.owner_helper.fixture()
        self.tasks = {
            "admitted": self.owner_helper.task(
                self.refresh, "left",
                required_edges=[{"state": [1, 0, 0], "action": "B"}]),
            "missing": self.owner_helper.task(
                self.refresh, "left",
                required_edges=[{"state": [0, 1, 2], "action": "B"}]),
        }
        # This is a deliberately synthetic binder. It does NOT establish
        # external authority or candidate/source equivalence.
        self.allowed_bind = True
        self.observer = self.make()

    def make(self, source_capture=None, binding=None):
        def fixture_binding(view, task_name, report):
            return bool(self.allowed_bind and view.worker_id == WORKER_ID
                        and view.result["verdicts"]
                        and any(v != "CONTRADICTED" for v in view.result["verdicts"])
                        and task_name == "admitted"
                        and report["route"] == self.tasks["admitted"].route_name
                        and report["route_fingerprint"] == self.tasks["admitted"].expected
                        and report["local_owner_pins_verified"])
        return WorkstationOwnerNativeObserver(
            self.b4, native_source_root=CP30_ROOT,
            source_capture=source_capture or (lambda: self.tasks),
            verify_candidate_binding=binding or fixture_binding)

    def test_live_cp30_task_audited_and_returned_into_existing_lane(self):
        before = len(self.harness._runtime().event_store.all())
        result = self.observer.record(
            self.lane_id, task_name="admitted", allow_native_record=True)
        self.assertTrue(result.recorded_new_event)
        self.assertEqual(result.status, "NATIVE_LOCAL_TASK_AUDITED_NOT_EXTERNAL_PROOF")
        self.assertEqual(result.candidate_index, 0)
        self.assertEqual(len(self.harness._runtime().event_store.all()), before + 1)
        row = self.observer.recorded(self.lane_id)[0]
        self.assertEqual(row["job_id"], self.job_id)
        self.assertTrue(len(row["local_evidence_sha256"]) == 64)
        self.assertFalse(row["external_owner_identity_authenticated"])
        self.assertFalse(row["finite_prefilter_edge_proven"])
        self.assertFalse(row["parent_cp_witnessed"])
        self.assertEqual(self.harness._runtime().state(self.job_id).status, "COMPLETE")
        self.assertEqual(self.harness._runtime().state(self.harness._handoff_id("B")).status,
                         "READY")

    def test_native_audit_is_repeated_without_duplicate_journal_record(self):
        self.observer.record(self.lane_id, task_name="admitted", allow_native_record=True)
        before = (self.data / "runtime.jsonl").read_bytes()
        second = self.make().record(self.lane_id, task_name="admitted",
                                    allow_native_record=True)
        self.assertFalse(second.recorded_new_event)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_absent_explicit_record_approval_is_refused(self):
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaises(PermissionError):
            self.observer.record(self.lane_id, task_name="admitted")
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_missing_native_route_obligation_is_not_claimed_complete(self):
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "not witnessed complete"):
            self.observer.record(self.lane_id, task_name="missing",
                                 allow_native_record=True)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_native_owner_pin_revocation_refuses_stale_evidence(self):
        self.left.first.recipient.registry.revoke(self.left.first.recipient._base._tokens[0])
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "pin is revoked"):
            self.observer.record(self.lane_id, task_name="admitted",
                                 allow_native_record=True)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_replaced_owner_task_between_captures_is_refused(self):
        calls = [0]
        def changed():
            calls[0] += 1
            if calls[0] == 1:
                return self.tasks
            return {**self.tasks, "admitted": self.owner_helper.task(
                self.refresh, "left",
                required_edges=[{"state": [1, 0, 0], "action": "B"}])}
        first = self.make(source_capture=changed)
        with self.assertRaisesRegex(ValueError, "changed during"):
            first.record(self.lane_id, task_name="admitted", allow_native_record=True)
        self.assertEqual(first.recorded(self.lane_id), ())

    def test_unbound_candidate_does_not_inherit_local_cp30_task_proof(self):
        self.allowed_bind = False
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "no separately bound"):
            self.observer.record(self.lane_id, task_name="admitted",
                                 allow_native_record=True)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_original_b2_witness_revoked_blocks_owner_audit(self):
        self.witness_allowed = False
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "original parent movement"):
            self.observer.record(self.lane_id, task_name="admitted",
                                 allow_native_record=True)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_domain_relation_verifier_revocation_blocks_owner_audit(self):
        self.allow_next = False
        with self.assertRaisesRegex(ValueError, "no admitted owner-native"):
            self.observer.inspect(self.lane_id, task_name="admitted")

    def test_unstaffed_does_not_fake_a_subprocess_worker(self):
        read = self.observer.inspect(self.lane_id, task_name="admitted")
        self.assertTrue(read["native_task_completed"])
        self.assertFalse(read["runtime_job_started"])
        self.assertFalse(read["journal_modified"])
        self.assertFalse(read["external_identity_proven"])
        self.assertFalse(read["finite_candidate_edge_proven"])
        self.assertEqual(self.observer.recorded(self.lane_id), ())


if __name__ == "__main__":
    unittest.main()
