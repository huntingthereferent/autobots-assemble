"""A real finite edition in the existing HandoffRuntime; no new scheduler."""
from __future__ import annotations

from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import (
    CorrespondenceWorkBridge, CorrespondenceWorker, WORKER_ID, VERIFIER,
)

HERE = Path(__file__).resolve().parents[2]
FINITE = HERE / "work" / "arc_like_maze" / "chatbot"
MODULES = ("finite_goal_priority.py", "finite_required_edge_guard.py")
INPUTS = {"old_phi": [0,0,1], "new_phi": [0,0,0],
          "candidate_words": [["ABAA","ABBABA"], ["ABAA","AAABB","BAAAB"], ["ABBABA"]],
          "required_state": [0,0,0], "required_action": "B"}


class CorrespondenceWorkerHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        source = base / "original"
        source.mkdir()
        for f in MODULES:
            shutil.copyfile(FINITE / f, source / f)
        self.workstation = ProcessWorkstation(base / "private")
        self.workstation.copy_source(source, worker_id=WORKER_ID, version_id="baseline")
        self.journal_path = base / "handoffs.jsonl"
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal_path))
        self.bridge = CorrespondenceWorkBridge(runtime=self.runtime, workstation=self.workstation)

    def admit(self, **kwargs):
        return self.bridge.admit(version_id="baseline", inputs=INPUTS, from_actor="james", **kwargs)

    def test_explicit_admission_does_not_execute_worker(self):
        h = self.admit(lane_id="research")
        self.assertEqual(self.runtime.state(h.handoff_id).status, "READY")
        self.assertEqual(self.bridge.inspect(h.handoff_id)["lane_refs"], ["workspace-lane:research"])
        self.assertEqual([e.event_type for e in self.runtime.event_store.for_handoff(h.handoff_id)], ["CREATED"])

    def test_explicit_execution_runs_copied_finite_modules_and_replays(self):
        h = self.admit()
        state = self.bridge.execute(h.handoff_id,allow_local_execution=True)
        self.assertEqual(state.status,"COMPLETE")
        self.assertEqual(state.output["verdicts"], ["CONTRADICTED", "NOT_CONTRADICTED", "CONTRADICTED"])
        self.assertGreater(state.output["child_pid"],0)
        self.assertTrue(self.bridge.reverify(h.handoff_id))
        self.assertEqual([e.event_type for e in self.runtime.event_store.for_handoff(h.handoff_id)], ["CREATED","STARTED","RESULT"])

    def test_no_implicit_execution(self):
        h = self.admit()
        with self.assertRaises(PermissionError):
            self.bridge.execute(h.handoff_id)
        self.assertEqual(self.runtime.state(h.handoff_id).status, "READY")

    def test_result_verifier_rejects_unsupported_claim(self):
        h = self.admit()
        false = ExecutionResult("COMPLETE",output={"kind":"finite-prefilter-v1","verdicts":["CONTRADICTED"]*3,
                    "edition_fingerprint":h.metadata["edition_fingerprint"],"worker_version":"baseline","child_pid":42},
                    evidence=(EvidenceRecord(condition="finite prefilter independently reproduced",kind="computation",source="local finite correspondence process edition",ref=h.metadata["edition_fingerprint"],depth="local-replay"),))
        with self.assertRaises(ValueError):
            self.runtime.return_result(h.handoff_id,actor_id=h.to_actor,result=false)
        self.assertEqual(self.runtime.state(h.handoff_id).status,"READY")

    def test_wrong_kind_and_synthetic_physical_record_fail(self):
        h=self.admit()
        forged = ExecutionResult("COMPLETE",output={"kind":"finite-prefilter-v1","verdicts":["CONTRADICTED","NOT_CONTRADICTED","CONTRADICTED"],
                    "edition_fingerprint":h.metadata["edition_fingerprint"],"worker_version":"baseline","child_pid":42},
                    evidence=(EvidenceRecord(condition="finite prefilter independently reproduced",kind="measurement",source="machine",ref="fake"),))
        with self.assertRaises(ValueError):
            self.runtime.return_result(h.handoff_id,actor_id="machine",result=forged)
        self.assertEqual(self.runtime.state(h.handoff_id).status,"READY")

    def test_worker_file_edited_after_admission_rejects_execution(self):
        h=self.admit()
        (Path(self.workstation._edition(WORKER_ID,"baseline"))/MODULES[0]).write_text("# changed after admission\n")
        with self.assertRaisesRegex(ValueError,"source changed"):
            self.bridge.execute(h.handoff_id,allow_local_execution=True)
        self.assertEqual(self.runtime.state(h.handoff_id).status,"READY")

    def test_branch_is_independent_and_can_be_selected(self):
        branched=self.workstation.branch(worker_id=WORKER_ID,parent_version="baseline",version_id="branch-a")
        (Path(branched["path"]) / "notes.txt").write_text("trial notes\n")
        h=self.bridge.admit(version_id="branch-a",inputs=INPUTS,from_actor="james")
        self.assertNotEqual(h.metadata["edition_fingerprint"],self.workstation.inspect(worker_id=WORKER_ID,version_id="baseline")["current_fingerprint"])
        self.assertEqual(self.bridge.execute(h.handoff_id,allow_local_execution=True).status,"COMPLETE")
        self.assertFalse((Path(self.workstation._edition(WORKER_ID,"baseline")) / "notes.txt").exists())

    def test_incompatible_seed_rejected_before_admission(self):
        bad={**INPUTS,"candidate_words":[["B","ABBABA"]]}
        with self.assertRaises(ValueError):
            self.bridge.admit(version_id="baseline",inputs=bad,from_actor="james")
        self.assertFalse(self.runtime.snapshot())

    def test_missing_module_fails_admission(self):
        (Path(self.workstation._edition(WORKER_ID,"baseline"))/MODULES[1]).unlink()
        with self.assertRaises(ValueError):
            self.admit()

    def test_malformed_task_rejected(self):
        for bad in ({**INPUTS,"old_phi":[0,0,4]}, {**INPUTS,"required_action":"X"}, {**INPUTS,"candidate_words":[["ZZ"]]}, {**INPUTS,"unexpected":1}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                self.bridge.admit(version_id="baseline",inputs=bad,from_actor="james")
        self.assertFalse(self.runtime.snapshot())

    def test_runtime_restart_restores_receipt_and_fresh_reverification(self):
        h=self.admit()
        self.bridge.execute(h.handoff_id,allow_local_execution=True)
        restored=HandoffRuntime(event_store=RuntimeJournal(self.journal_path))
        bridge=CorrespondenceWorkBridge(runtime=restored,workstation=self.workstation)
        self.assertEqual(restored.state(h.handoff_id).status,"COMPLETE")
        self.assertTrue(bridge.reverify(h.handoff_id))

    def test_completed_job_not_executed_twice(self):
        h=self.admit()
        self.bridge.execute(h.handoff_id,allow_local_execution=True)
        with self.assertRaises(ValueError):
            self.bridge.execute(h.handoff_id,allow_local_execution=True)

    def test_job_source_version_bound_to_edition(self):
        h=self.admit()
        other=self.workstation.branch(worker_id=WORKER_ID,parent_version="baseline",version_id="next")
        worker=CorrespondenceWorker(self.bridge,h.handoff_id)
        self.assertFalse(worker.can_execute(self.bridge.admit(version_id="next",inputs=INPUTS,from_actor="james")))
        self.assertEqual(self.runtime.get(h.handoff_id).metadata["worker_version"],"baseline")

    def test_worker_process_invalid_claim_not_journaled(self):
        # Deliberately altered process executable is an untrusted worker copy.
        edition=Path(self.workstation._edition(WORKER_ID,"baseline"))
        (edition / "finite_required_edge_guard.py").write_text("def preflight(*args): return 'NOT_CONTRADICTED'\n")
        h=self.admit()
        with self.assertRaisesRegex(ValueError,"native finite verifier rejected"):
            self.bridge.execute(h.handoff_id,allow_local_execution=True)
        self.assertEqual(self.runtime.state(h.handoff_id).status,"ACTIVE")
        self.assertNotIn("RESULT",[e.event_type for e in self.runtime.event_store.for_handoff(h.handoff_id)])

    def test_result_witness_is_not_proof_of_admitted_edge(self):
        h=self.admit()
        self.bridge.execute(h.handoff_id,allow_local_execution=True)
        self.assertIn("NOT_CONTRADICTED",self.runtime.state(h.handoff_id).output["verdicts"])
        self.assertIn("NOT_CONTRADICTED is not a proven admitted edge.",h.boundaries)

    def test_undecided_candidate_is_not_upgraded(self):
        inputs={**INPUTS, "candidate_words":[["A"]], "required_state":[1,1,1]}
        h=self.bridge.admit(version_id="baseline",inputs=inputs,from_actor="james")
        state=self.bridge.execute(h.handoff_id,allow_local_execution=True)
        self.assertEqual(state.output["verdicts"],["UNDECIDED"])

    def test_no_reverify_without_result(self):
        h=self.admit()
        with self.assertRaises(ValueError):
            self.bridge.reverify(h.handoff_id)


if __name__=="__main__": unittest.main()
