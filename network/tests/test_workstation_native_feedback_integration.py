"""B3: actual native finite worker subprocess -> reverify -> same journal feedback.

The branch observation used to activate the harness is a synthetic test fixture.
Native completion and return verification use the repository's real source-pinned
controls on a temporary CI workstation, not fake injected controls.
"""
from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.workstation_harness import WorkstationContinuationHarness
from systems.workspace.workstation_native_feedback import WorkstationNativeFeedback
from systems.workspace.coordinator_window import CoordinatorIndex
from systems.workspace.cp_motion import admit_research
from systems.workspace.process_handoff import WORKER_ID
from systems.workspace.controls import run_job
from systems.workspace.branch_help import verify_return


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "arc_like_maze" / "chatbot"
NATIVE_INPUTS = {
    "old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
    "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
    "required_state": [0, 0, 0], "required_action": "B",
}


class RealNativeFeedbackTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data = Path(temp.name) / "private"
        selected = Path(temp.name) / "selected-source"
        selected.mkdir()
        for name in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(SOURCE / name, selected / name)
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.desk.copy_source(selected, worker_id=WORKER_ID, version_id="base")
        self.index = CoordinatorIndex(self.data / "coordinator-windows.jsonl")
        admit_research(self.index)
        self.inputs = Path(temp.name) / "native-inputs.json"
        self.inputs.write_text(json.dumps(NATIVE_INPUTS), encoding="utf8")
        self.witness_allowed = True
        self.harness = WorkstationContinuationHarness(
            self.data,
            verify_observation=lambda o: self.witness_allowed and o.witness_ref == "fixture:branch",
            verify_connection=lambda a, b: False,
            worker_editions={"finite-required-edge-prefilter": "source-edition:base"})
        self.harness.seed_lane("A", "initial native bounded A",
                               cp_lane="game", cp_slot="cp-game-w13-worlds")
        self.harness.seed_lane("B", "independent native bounded B")
        self.harness.observe(lane_id="A", kind="BRANCH",
                             relation="native finite source prefilter needed",
                             witness_ref="fixture:branch",
                             capability="finite-required-edge-prefilter")
        born = self.harness.tick()["born_coordination_lanes"]
        self.assertEqual(len(born), 1)
        self.lane_id = born[0]
        assigned = self.harness.admit_native_help(
            self.lane_id, parent_version="base", inputs_file=self.inputs,
            allow_native_admission=True)
        self.assertEqual(assigned["native_help"]["state"], "ASSIGNED_NOT_VERIFIED")
        self.job_id = assigned["native_help"]["child"]["job_id"]
        self.feedback = WorkstationNativeFeedback(
            self.harness, run_job=run_job, verify_return=verify_return)

    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))

    def advance(self):
        return self.feedback.advance(self.lane_id, confirm_execute=self.job_id,
                                     allow_local_execution=True)

    def test_true_native_worker_executes_and_return_is_recorded_on_original_lane(self):
        self.assertEqual(self.runtime().state(self.job_id).status, "READY")
        receipt = self.advance()
        self.assertTrue(receipt.recorded_new_event)
        self.assertEqual(self.runtime().state(self.job_id).status, "COMPLETE")
        self.assertFalse(receipt.checkpoint_pass)
        self.assertEqual(len(receipt.output_sha256), 64)
        self.assertEqual(len(receipt.evidence_sha256), 64)
        original = self.runtime()
        self.assertEqual(original.state(self.harness._handoff_id("A")).status, "READY")
        self.assertEqual(original.state(self.harness._handoff_id("B")).status, "READY")
        evidence = original.event_store.for_handoff(self.lane_id)
        self.assertEqual(sum(x.event_type == "WORKSTATION_NATIVE_RESULT_VERIFIED"
                             for x in evidence), 1)
        self.assertEqual(len(self.feedback.historical_returns(self.lane_id)), 1)

    def test_completed_native_job_reverified_without_duplicate_execution(self):
        self.advance()
        before = (self.data / "runtime.jsonl").read_bytes()
        other = self.advance()
        self.assertFalse(other.recorded_new_event)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())
        self.assertEqual(len(self.feedback.historical_returns(self.lane_id)), 1)

    def test_exact_job_confirmation_required_before_any_execution(self):
        with self.assertRaises(PermissionError):
            self.feedback.advance(self.lane_id, confirm_execute="wrong",
                                  allow_local_execution=True)
        self.assertEqual(self.runtime().state(self.job_id).status, "READY")
        with self.assertRaises(PermissionError):
            self.feedback.advance(self.lane_id, confirm_execute=self.job_id)
        self.assertEqual(self.runtime().state(self.job_id).status, "READY")

    def test_withdrawn_branch_observation_prevents_native_execution(self):
        self.witness_allowed = False
        with self.assertRaisesRegex(ValueError, "freshly verified"):
            self.advance()
        self.assertEqual(self.runtime().state(self.job_id).status, "READY")
        self.assertEqual(self.feedback.historical_returns(self.lane_id), ())

    def test_changed_worker_source_cannot_report_verified_return(self):
        source, _ = self.desk._read(WORKER_ID, "help-" + self.harness._runtime().get(
            self.lane_id).metadata["birth_proposal_id"][-20:])
        # Resolve actual child edition from source-owned admission, not from
        # an assumed relation with a generated proposal identifier.
        assignment = self.harness.admit_native_help(self.lane_id)["native_help"]["child"]
        edition, _ = self.desk._read(WORKER_ID, assignment["version_id"])
        changed = edition / "finite_required_edge_guard.py"
        changed.write_text(changed.read_text(encoding="utf8") + "\n# tampered after admission\n",
                           encoding="utf8")
        with self.assertRaises(ValueError):
            self.advance()
        self.assertEqual(self.runtime().state(self.job_id).status, "READY")
        self.assertEqual(self.feedback.historical_returns(self.lane_id), ())


if __name__ == "__main__":
    unittest.main()
