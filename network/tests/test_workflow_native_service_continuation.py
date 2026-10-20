"""Real EcosystemService/Ohayo source handoff -> bounded native worker help."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.handoff import ExecutionResult
from runtime.repository_tasks import read_active_work
from runtime.service import EcosystemService
from systems.workspace.workflow_draft import SCHEMA
from systems.workspace.workflow_idea_frontier import IdeaFrontier
from systems.workspace.workflow_pins import WorkflowPins

ROOT = Path(__file__).resolve().parents[2]


def draft(label: str, parent: str = "") -> dict:
    return {
        "schema": SCHEMA,
        "title": "Existing source task continuation",
        "provenance": "real repo-work handoff, test handler only",
        "auto_connect": False,
        "parent_revision": parent,
        "steps": [{"id": "source-step", "label": label,
                   "manifest": "foundation/program_examples/stateless.json",
                   "inputs": {"text": "source-owned fixture"},
                   "path_role": "REQUIRED"}],
        "links": [],
    }


class EcosystemServiceNativeContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name)
        self.service = EcosystemService(
            data_dir=self.data, repository_work_file=ROOT / "TASKS.md")
        self.idea = read_active_work(ROOT / "TASKS.md")[0].source_id
        self.handoff = "repo-work-" + self.idea
        self.pins = WorkflowPins(self.data)
        self.frontier = IdeaFrontier(ROOT, self.data)

    def pinned(self):
        parent = self.pins.pin_candidate(draft("Original"), ROOT, reason="Native source")
        mine = self.pins.pin_candidate(draft("Owner approach", parent["revision"]),
                                      ROOT, reason="Owner branch")
        peer = self.pins.pin_candidate(draft("Peer alternative", parent["revision"]),
                                      ROOT, reason="Peer branch")
        for pin, actor in ((parent, "james"), (mine, "james"), (peer, "worker-B")):
            self.frontier.bind(idea_id=self.idea, revision=pin["revision"],
                               worker=actor, reason="Explicit source-bound test association")
        return parent, mine, peer

    def test_ohayo_admission_reaches_real_service_native_worker(self):
        parent, mine, peer = self.pinned()
        initial = self.service.ohayo(actor_id="james")
        self.assertIn(self.handoff, initial["repository_handoffs_admitted"])
        native = self.service.runtime.get(self.handoff)
        self.assertEqual(native.to_actor, "james")
        self.assertEqual(native.metadata["repository_source"], "TASKS.md")
        self.frontier.propose(
            kind="HELP", idea_id=self.idea, revision=peer["revision"],
            step_id="source-step", worker="worker-B",
            target_revision=mine["revision"],
            reason="Recorded peer alternative at the same declared source step")
        before = tuple(self.service.runtime.event_store.for_handoff(self.handoff))
        observed = []

        def owner_handler(handoff, context):
            self.assertEqual(handoff.handoff_id, self.handoff)
            view = context.observe()
            self.assertEqual(view["native_handoff"]["state"], "ACTIVE")
            self.assertEqual(view["native_handoff"]["source_work_id"], self.idea)
            self.assertEqual(len(view["incoming_peer_help"]), 1)
            self.assertEqual(len(view["visible_branches"]), 2)
            self.assertTrue(all("draft" not in b and "links" not in b
                                for b in view["visible_branches"]))
            proposal = view["incoming_peer_help"][0]
            result = context.review_help(
                proposal_ref=proposal["proposal_ref"], decision="DECLINE",
                reason="This locally visible alternative does not answer my current source step")
            self.assertFalse(result["event"]["branch_adopted"])
            observed.append(context.observe()["incoming_peer_help"][0]["state"])
            return ExecutionResult(
                status="UNKNOWN", note="Reviewer made a decision, native task still unresolved")

        with self.assertRaises(PermissionError):
            self.service.run_repository_worker_with_frontier(
                handoff_id=self.handoff, revision=mine["revision"],
                step_id="source-step", handler=owner_handler)
        self.assertEqual(tuple(self.service.runtime.event_store.for_handoff(self.handoff)), before)
        state = self.service.run_repository_worker_with_frontier(
            handoff_id=self.handoff, revision=mine["revision"],
            step_id="source-step", handler=owner_handler, allow_native_execution=True)
        self.assertEqual(state.status, "UNKNOWN")
        self.assertEqual(observed, ["DECLINE"])
        self.assertEqual(self.service.runtime.state(self.handoff).status, "UNKNOWN")
        self.assertEqual(len(self.pins.list_pins()), 3)
        reply = self.frontier.worker_frontier(
            idea_id=self.idea, revision=peer["revision"],
            step_id="source-step", worker="worker-B")["outgoing_help_reviews"]
        self.assertEqual(len(reply), 1)
        self.assertEqual(reply[0]["review"], "DECLINE")
        self.assertFalse(reply[0]["branch_adopted"])

    def test_without_configured_native_repository_source_no_execution(self):
        unrelated = EcosystemService(data_dir=self.data / "separate")
        _, mine, _ = self.pinned()
        before = tuple(unrelated.runtime.event_store.all())
        with self.assertRaisesRegex(ValueError, "TASKS.md must be configured"):
            unrelated.run_repository_worker_with_frontier(
                handoff_id=self.handoff, revision=mine["revision"],
                step_id="source-step", handler=lambda *_: ExecutionResult(status="UNKNOWN"),
                allow_native_execution=True)
        self.assertEqual(tuple(unrelated.runtime.event_store.all()), before)

    def test_unadmitted_and_wrong_worker_position_are_rejected(self):
        _, mine, peer = self.pinned()
        before = tuple(self.service.runtime.event_store.all())
        with self.assertRaisesRegex(KeyError, "unknown handoff"):
            self.service.run_repository_worker_with_frontier(
                handoff_id=self.handoff, revision=mine["revision"],
                step_id="source-step", handler=lambda *_: ExecutionResult(status="UNKNOWN"),
                allow_native_execution=True)
        self.assertEqual(tuple(self.service.runtime.event_store.all()), before)
        self.service.ohayo(actor_id="james")
        before = tuple(self.service.runtime.event_store.for_handoff(self.handoff))
        with self.assertRaisesRegex(ValueError, "no explicit current"):
            self.service.run_repository_worker_with_frontier(
                handoff_id=self.handoff, revision=peer["revision"],
                step_id="source-step", handler=lambda *_: ExecutionResult(status="UNKNOWN"),
                allow_native_execution=True)
        self.assertEqual(tuple(self.service.runtime.event_store.for_handoff(self.handoff)), before)


if __name__ == "__main__":
    unittest.main()
