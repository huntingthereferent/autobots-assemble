"""Actual B2->B3 W13 bounded helper in an ephemeral source-owned workstation."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.branch_help import CAP_GAME, CAP_GAME_W13_NATIVE
from systems.workspace.coordinator_window import CoordinatorIndex
from systems.workspace.cp_motion import admit_research
from systems.workspace.controls import run_job
from systems.workspace.game_w13_native_bridge import (
    GameW13NativeBridge, WORKER_ID, copy_game_source,
)
from systems.workspace.game_w13_native_cli import bounded_input
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.workstation_w13_delegate import (
    PARENT_JOB, PARENT_VERSION, INPUTS, delegate_w13,
)


class RealW13DelegationTests(unittest.TestCase):
    def setUp(self):
        tmp=TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data=Path(tmp.name)/"native"
        self.output=Path(tmp.name)/"evidence"
        index=CoordinatorIndex(self.data/"coordinator-windows.jsonl")
        admit_research(index)
        copy_game_source(self.data, version_id=PARENT_VERSION, allow_copy=True)
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        desk=ProcessWorkstation(self.data/"workstation")
        GameW13NativeBridge(runtime=runtime, workstation=desk).admit(
            version_id=PARENT_VERSION, inputs=bounded_input(INPUTS),
            from_actor="test-original-native-job", job_id=PARENT_JOB)
        run_job(data_dir=self.data, job_id=PARENT_JOB, confirm_execute=PARENT_JOB)

    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))

    def test_01_actual_w13_delegation_executes_different_child_and_returns(self):
        report=delegate_w13(data_dir=self.data, output_dir=self.output)
        self.assertEqual(report["native_worker_id"], WORKER_ID)
        self.assertNotEqual(report["delegate_job_id"], PARENT_JOB)
        self.assertTrue(report["delegated_subprocess_completed"])
        self.assertTrue(report["verified_native_return_recorded"])
        self.assertEqual(report["worlds_completed"], 2)
        self.assertEqual(report["native_verification"], "PASS")
        self.assertTrue(report["original_AB_lanes_present"])
        self.assertTrue(report["repeat_did_not_execute"])
        child=self.runtime().get(report["delegate_job_id"])
        self.assertEqual(child.metadata["worker_id"], WORKER_ID)
        self.assertEqual(self.runtime().state(child.handoff_id).status,"COMPLETE")
        events=self.runtime().event_store.for_handoff(report["coordination_handoff_id"])
        self.assertEqual(len([e for e in events
                             if e.event_type=="WORKSTATION_NATIVE_RESULT_VERIFIED"]),1)
        self.assertTrue((self.output/"delegation.json").is_file())

    def test_02_second_invocation_does_not_create_other_native_job_or_new_history(self):
        first=delegate_w13(data_dir=self.data, output_dir=self.output)
        before=(self.data/"runtime.jsonl").read_bytes()
        second=delegate_w13(data_dir=self.data, output_dir=self.output)
        self.assertEqual(second["delegate_job_id"],first["delegate_job_id"])
        self.assertFalse(second["new_return_event"])
        self.assertEqual((self.data/"runtime.jsonl").read_bytes(),before)

    def test_03_changed_original_w13_source_cannot_authorize_a_helper(self):
        copied=ProcessWorkstation(self.data/"workstation")._edition(WORKER_ID, PARENT_VERSION)
        p=copied/"game_worlds_worker.py"
        p.write_text(p.read_text()+"\n# mutated prior source\n")
        with self.assertRaises(ValueError):
            delegate_w13(data_dir=self.data, output_dir=self.output)
        self.assertFalse((self.output/"delegation.json").exists())

    def test_04_unwitnessed_source_job_cannot_delegate(self):
        from runtime.handoff import HandoffEvent
        # Tampering journal bytes is rejected at the source boundary.
        journal=self.data/"runtime.jsonl"
        journal.write_bytes(journal.read_bytes()+b"not valid JSON\n")
        with self.assertRaises((ValueError, KeyError)):
            delegate_w13(data_dir=self.data, output_dir=self.output)

    def test_05_generic_game_engine_is_still_not_registered(self):
        self.assertNotEqual(CAP_GAME, CAP_GAME_W13_NATIVE)
        self.assertEqual(CAP_GAME_W13_NATIVE, "game-w13-native-two-room")


if __name__=="__main__":
    unittest.main()
