"""Existing native actor runner polls source-grounded first-hop Workstation views."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult
from runtime.journal import RuntimeJournal
from runtime.repository_tasks import admit_active_work, read_active_work
from systems.workspace.workflow_draft import SCHEMA
from systems.workspace.workflow_pins import WorkflowPins
from systems.workspace.workflow_idea_frontier import IdeaFrontier
from systems.workspace.workflow_native_continuation import NativePosition, ScopedRepositoryWorker

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "TASKS.md"
MANIFEST = "foundation/program_examples/stateless.json"


def spec(label: str, parent: str = "") -> dict:
    return {
        "schema": SCHEMA, "title": "Native continuation fixture",
        "provenance": "source-recorded test task",
        "parent_revision": parent, "auto_connect": False,
        "steps": [{"id": "site", "label": label, "manifest": MANIFEST,
                   "inputs": {"text": "local-source"}, "path_role": "REQUIRED"}],
        "links": [],
    }


class NativeWorkerContinuationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data_dir = Path(self.tmp.name)
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.data_dir/"runtime.jsonl"))
        admit_active_work(self.runtime, TASKS, actor_id="james")
        self.idea = read_active_work(TASKS)[0].source_id
        self.handoff_id = "repo-work-" + self.idea
        self.frontier = IdeaFrontier(ROOT, self.data_dir)
        self.pins = WorkflowPins(self.data_dir)
        self.root = self.pins.pin_candidate(spec("Original"), ROOT, reason="Original")
        self.pins_branch = self.pins.pin_candidate(
            spec("Exploring alpha", self.root["revision"]), ROOT, reason="Explore alpha")
        self.peer = self.pins.pin_candidate(
            spec("Exploring beta", self.root["revision"]), ROOT, reason="Explore beta")
        for pin, owner in ((self.root, "james"),
                           (self.pins_branch, "james"), (self.peer, "worker-B")):
            self.frontier.bind(idea_id=self.idea, revision=pin["revision"],
                               worker=owner, reason="Explicit native test-source association")
        self.position = NativePosition(self.handoff_id, self.pins_branch["revision"], "site")

    def test_opt_in_runtime_worker_observes_new_peer_help_during_same_move(self):
        seen = []

        def native_handler(handoff, context):
            first = context.observe()
            seen.append(first)
            self.assertEqual(first["native_handoff"]["state"], "ACTIVE")
            self.assertEqual(first["incoming_peer_help"], [])
            # This is a distinct, previously bound peer's witnessed first-hop
            # proposal; the worker does NOT gain access to the peer's graph.
            self.frontier.propose(
                kind="HELP", idea_id=self.idea, revision=self.peer["revision"],
                step_id="site", worker="worker-B",
                target_revision=self.pins_branch["revision"],
                reason="Observed a different declared approach at the same step")
            again = context.observe()
            seen.append(again)
            self.assertEqual(len(again["incoming_peer_help"]), 1)
            self.assertEqual(again["incoming_peer_help"][0]["from_revision"],
                             self.peer["revision"])
            self.assertFalse(again["native_relationships_verified"])
            self.assertNotIn("draft", str(again))
            self.assertTrue(all("steps" not in peer for peer in again["visible_branches"]))
            return ExecutionResult(
                status="UNKNOWN", output={"observed_help": True},
                note="No native result witness; original task remains unresolved")

        wrapped = ScopedRepositoryWorker(
            runtime=self.runtime, frontier=self.frontier,
            position=self.position, handler=native_handler)
        self.assertEqual(wrapped.as_actor().actor_id, "james")
        before = (self.data_dir/"runtime.jsonl").read_bytes()
        with self.assertRaises(PermissionError):
            wrapped.run()
        self.assertEqual((self.data_dir/"runtime.jsonl").read_bytes(), before)
        result = wrapped.run(allow_native_execution=True)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertEqual(len(seen), 2)
        self.assertEqual(self.runtime.state(self.handoff_id).status, "UNKNOWN")
        self.assertEqual(len(self.pins.list_pins()), 3)
        self.assertEqual(self.frontier._read()[-1]["type"], "HELP_PROPOSED")

    def test_run_preflight_fails_closed_on_wrong_assignment_or_source(self):
        actual = self.handoff_id
        rejected = NativePosition(actual, self.peer["revision"], "site")
        with self.assertRaisesRegex(ValueError, "no explicit current"):
            ScopedRepositoryWorker(
                runtime=self.runtime, frontier=self.frontier,
                position=rejected,
                handler=lambda *_: ExecutionResult(status="UNKNOWN"))
        before = (self.data_dir/"runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(KeyError, "unknown handoff"):
            ScopedRepositoryWorker(
                runtime=self.runtime, frontier=self.frontier,
                position=NativePosition("repo-work-imaginary", self.pins_branch["revision"], "site"),
                handler=lambda *_: ExecutionResult(status="UNKNOWN"))
        self.assertEqual((self.data_dir/"runtime.jsonl").read_bytes(), before)

    def test_native_actor_rejects_other_handoffs_even_with_same_actor_capabilities(self):
        _, other = read_active_work(TASKS)[:2]
        wrapped = ScopedRepositoryWorker(
            runtime=self.runtime, frontier=self.frontier, position=self.position,
            handler=lambda *_: ExecutionResult(status="UNKNOWN"))
        native = wrapped.as_actor()
        with self.assertRaisesRegex(ValueError, "another task"):
            native.execute(self.runtime.get("repo-work-" + other.source_id))
        self.assertEqual(self.runtime.state("repo-work-" + other.source_id).status, "READY")

    def test_native_context_backtrack_is_recorded_but_not_performed(self):
        captured = []

        def handler(_handoff, context):
            result = context.propose(
                kind="BACKTRACK", target_revision=self.root["revision"],
                reason="Observed parent source structure to revisit")
            captured.append(result)
            return ExecutionResult(status="UNKNOWN", note="Proposal only")

        worker = ScopedRepositoryWorker(
            runtime=self.runtime, frontier=self.frontier,
            position=self.position, handler=handler)
        result = worker.run(allow_native_execution=True)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertEqual(captured[0]["event"]["type"], "BACKTRACK_PROPOSED")
        self.assertFalse(captured[0]["event"]["rewind_executed"])
        self.assertEqual(self.runtime.state(self.handoff_id).status, "UNKNOWN")
        self.assertEqual(len(self.pins.list_pins()), 3)

    def test_wrong_return_type_never_counts_as_completed_native_result(self):
        bad = ScopedRepositoryWorker(
            runtime=self.runtime, frontier=self.frontier,
            position=self.position, handler=lambda *_: {"status": "COMPLETE"})
        with self.assertRaisesRegex(TypeError, "ExecutionResult"):
            bad.run(allow_native_execution=True)
        self.assertNotEqual(self.runtime.state(self.handoff_id).status, "COMPLETE")


if __name__ == "__main__":
    unittest.main()
