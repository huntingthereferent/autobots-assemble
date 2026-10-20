"""Genuine existing finite worker subprocess -> independent replay -> workflow pin."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import CorrespondenceWorkBridge, WORKER_ID
from systems.workspace.workflow_draft import SCHEMA
from systems.workspace.workflow_pins import WorkflowPins
from systems.workspace.workflow_native_results import WorkflowNativeResults, NativeResultBoundary
from systems.workspace.workflow_idea_frontier import IdeaFrontier
from systems.workspace.workflow_native_continuation import NativePosition, BoundedWorkerContext
from runtime.repository_tasks import admit_active_work, read_active_work

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "arc_like_maze" / "chatbot"
FILES = ("finite_goal_priority.py", "finite_required_edge_guard.py")
INPUTS = {
    "old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
    "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"], ["ABBABA"]],
    "required_state": [0, 0, 0], "required_action": "B",
}


def workflow():
    return {
        "schema": SCHEMA, "title": "Finite source-backed native trials",
        "provenance": "local example of native evidence comparison",
        "auto_connect": False,
        "steps": [{
            "id": "finite", "label": "Native finite correspondence prefilter",
            "manifest": "foundation/program_examples/stateless.json",
            "inputs": {"text": "native bounded fixture"},
        }], "links": [],
    }


class NativeResultWorkstationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.data = Path(self.temporary.name)
        raw = self.data / "original"
        raw.mkdir()
        for file in FILES:
            shutil.copyfile(SOURCE / file, raw / file)
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.desk.copy_source(raw, worker_id=WORKER_ID, version_id="baseline")
        second = self.desk.branch(worker_id=WORKER_ID, parent_version="baseline", version_id="another")
        (Path(second["path"]) / "notes.txt").write_text("second source edition\n")
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        self.bridge = CorrespondenceWorkBridge(runtime=self.runtime, workstation=self.desk)
        self.results = WorkflowNativeResults(ROOT, self.data)
        self.pins = WorkflowPins(self.data)

    def run_native(self, version, job):
        handoff = self.bridge.admit(
            version_id=version, inputs=INPUTS,
            from_actor="explicit-test-operator", job_id=job)
        status = self.bridge.execute(handoff.handoff_id, allow_local_execution=True)
        self.assertEqual(status.status, "COMPLETE")
        return handoff.handoff_id

    def setup_pins(self):
        parent = workflow()
        first = self.pins.pin_candidate(parent, ROOT, reason="Source-bound original")
        changed = deepcopy(parent)
        changed["parent_revision"] = first["revision"]
        changed["steps"][0]["label"] = "Second native edition observation"
        second = self.pins.pin_candidate(changed, ROOT, reason="Compare native edition")
        return parent, changed, first, second

    def test_real_native_worker_is_independently_replayed_without_reexecution(self):
        job = self.run_native("baseline", "finite-first")
        earlier = (self.data/"runtime.jsonl").read_bytes()
        report = self.results.inspect(job)
        self.assertTrue(report["native_result_reverified"])
        self.assertEqual(report["verdict_counts"],
                         {"CONTRADICTED": 2, "NOT_CONTRADICTED": 1, "UNDECIDED": 0})
        self.assertEqual(len(report["verdict_sequence_sha256"]), 64)
        self.assertTrue(report["result_event_id"].startswith("evt_"))
        self.assertFalse(report["branch_quality_verified"])
        self.assertFalse(report["native_job_reexecuted"])
        self.assertEqual((self.data/"runtime.jsonl").read_bytes(), earlier)

    def test_two_native_editions_attach_to_distinct_pins_and_compare(self):
        j1 = self.run_native("baseline", "finite-one")
        j2 = self.run_native("another", "finite-two")
        parent, child, first, second = self.setup_pins()
        left = self.results.attach(parent, step_id="finite", job_id=j1)
        right = self.results.attach(child, step_id="finite", job_id=j2)
        self.assertTrue(left["recorded"])
        self.assertTrue(right["recorded"])
        before = (self.data/"workflow_native_result_links.jsonl").read_bytes()
        again = self.results.attach(child, step_id="finite", job_id=j2)
        self.assertFalse(again["recorded"])
        self.assertEqual((self.data/"workflow_native_result_links.jsonl").read_bytes(), before)
        diff = self.results.compare(
            parent_revision=first["revision"], branch_revision=second["revision"],
            parent_step_id="finite", branch_step_id="finite")
        self.assertTrue(diff["source_owned_native_results_reverified_now"])
        self.assertTrue(diff["identical_native_verdicts"])
        self.assertEqual(diff["verdict_count_deltas"]["CONTRADICTED"], 0)
        self.assertFalse(diff["workflow_quality_ranked"])
        self.assertFalse(diff["whole_workflow_verified"])
        self.assertFalse(diff["automatic_pin_promotion"])
        self.assertEqual(len(self.pins.list_pins()), 2)
        self.assertEqual(len(self.results.list_records()), 2)

    def native_idea_context(self, revision: str, first: dict,
                            second: dict) -> BoundedWorkerContext:
        active = read_active_work(ROOT / "TASKS.md")[0].source_id
        admit_active_work(self.runtime, ROOT / "TASKS.md", actor_id="james")
        frontier = IdeaFrontier(ROOT, self.data)
        frontier.bind(idea_id=active, revision=first["revision"],
                      worker="james", reason="Original explicitly witnessed task")
        frontier.bind(idea_id=active, revision=second["revision"],
                      worker="james", reason="Known directly pinned continuation")
        return BoundedWorkerContext(frontier, self.runtime,
                                    NativePosition("repo-work-" + active,
                                                   second["revision"], "finite"))

    def test_native_worker_sees_reverified_result_only_at_current_and_parent_step(self):
        native_original = self.run_native("baseline", "visible-finite-original")
        native_branch = self.run_native("another", "visible-finite-branch")
        parent, child, first, second = self.setup_pins()
        self.results.attach(parent, step_id="finite", job_id=native_original)
        self.results.attach(child, step_id="finite", job_id=native_branch)
        context = self.native_idea_context(second["revision"], first, second)
        before = (self.data / "runtime.jsonl").read_bytes()
        observed = context.observe_native_results()
        self.assertEqual(observed["current_step_native_evidence"]["native"]["native_job_id"],
                         native_branch)
        self.assertEqual(len(observed["visible_related_step_evidence"]), 1)
        peer = observed["visible_related_step_evidence"][0]
        self.assertEqual(peer["revision"], first["revision"])
        self.assertEqual(peer["native"]["native_job_id"], native_original)
        self.assertEqual(peer["comparison"], "SAME_OPERATION_INPUTS_REVERIFIED")
        self.assertTrue(peer["matching_observed_result"])
        self.assertFalse(peer["quality_superiority_proven"])
        self.assertTrue(observed["other_ideas_not_read"])
        self.assertTrue(observed["operator_association_is_not_source_execution_proof"])
        self.assertFalse(observed["branch_quality_ranked"])
        self.assertFalse(observed["native_jobs_reexecuted"])
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_unverified_or_missing_native_result_never_assumed(self):
        parent, child, first, second = self.setup_pins()
        context = self.native_idea_context(second["revision"], first, second)
        observed = context.observe_native_results()
        self.assertEqual(observed["current_step_native_evidence"]["status"],
                         "NO_ATTACHED_NATIVE_RESULT")
        self.assertEqual(observed["visible_related_step_evidence"][0]["status"],
                         "NO_ATTACHED_NATIVE_RESULT")
        self.assertNotIn("native", observed["visible_related_step_evidence"][0])
        self.assertFalse(observed["branch_quality_ranked"])

    def test_visible_native_result_changed_after_attaching_fails_closed(self):
        native_original = self.run_native("baseline", "drift-source-parent")
        native_branch = self.run_native("another", "drift-source-child")
        parent, child, first, second = self.setup_pins()
        self.results.attach(parent, step_id="finite", job_id=native_original)
        self.results.attach(child, step_id="finite", job_id=native_branch)
        context = self.native_idea_context(second["revision"], first, second)
        context.observe_native_results()  # verify before mutating the source
        (self.desk._edition(WORKER_ID, "baseline") / FILES[0]).write_text("changed\\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            context.observe_native_results()

    def test_unpinned_workflow_cannot_claim_native_result(self):
        job = self.run_native("baseline", "finite-only")
        with self.assertRaisesRegex(NativeResultBoundary, "pinned"):
            self.results.attach(workflow(), step_id="finite", job_id=job)
        self.assertFalse(self.results.path.exists())

    def test_no_result_is_never_claimed_complete(self):
        self.bridge.admit(version_id="baseline", inputs=INPUTS,
                          from_actor="explicit-test-operator", job_id="not-executed")
        parent, _, _, _ = self.setup_pins()
        with self.assertRaises(ValueError):
            self.results.attach(parent, step_id="finite", job_id="not-executed")
        self.assertFalse(self.results.path.exists())

    def test_edited_source_fails_fresh_verification(self):
        job = self.run_native("baseline", "native-source-drift")
        parent, _, _, _ = self.setup_pins()
        self.results.attach(parent, step_id="finite", job_id=job)
        (self.desk._edition(WORKER_ID, "baseline") / FILES[0]).write_text("tampered\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            self.results.inspect(job)
        self.assertEqual(len(self.results.list_records()), 1)

    def test_wrong_job_binding_rejected_without_changing_pin(self):
        job = self.run_native("baseline", "one-native-result")
        parent, _, _, _ = self.setup_pins()
        with self.assertRaisesRegex(NativeResultBoundary, "existing workflow step"):
            self.results.attach(parent, step_id="unknown-step", job_id=job)
        self.results.attach(parent, step_id="finite", job_id=job)
        with self.assertRaisesRegex(NativeResultBoundary, "already has another"):
            other = self.run_native("another", "different-native-job")
            self.results.attach(parent, step_id="finite", job_id=other)
        self.assertEqual(len(self.results.list_records()), 1)

    def test_persisted_result_tampering_detected(self):
        job = self.run_native("baseline", "original-job")
        parent, _, _, _ = self.setup_pins()
        self.results.attach(parent, step_id="finite", job_id=job)
        path = self.results.path
        old = path.read_text()
        path.write_text(old.replace("NATIVE_FINITE_PREFILTER_RESULT_ONLY", "FICTITIOUS_PROOF"))
        with self.assertRaisesRegex(NativeResultBoundary, "mismatch"):
            self.results.list_records()


if __name__ == "__main__":
    unittest.main()
