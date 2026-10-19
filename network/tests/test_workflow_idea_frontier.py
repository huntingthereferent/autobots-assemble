"""Existing task-list ideas: source-scoped branch visibility and nonexecuting help."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.repository_tasks import read_active_work
from systems.workspace.workflow_draft import SCHEMA
from systems.workspace.workflow_idea_frontier import IdeaFrontier
from systems.workspace.workflow_pins import WorkflowPins

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "TASKS.md"
MANIFEST = "foundation/program_examples/stateless.json"


def spec(label="Original", parent=""):
    return {
        "schema": SCHEMA, "title": "Observe shared work without invented branches",
        "provenance": "test fixture only", "parent_revision": parent,
        "auto_connect": False,
        "steps": [
            {"id": "start", "label": label, "manifest": MANIFEST, "inputs": {"text": "source"}},
        ], "links": [],
    }


class IdeaFrontierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.index = IdeaFrontier(ROOT, self.directory)
        self.pins = WorkflowPins(self.directory)
        self.work = read_active_work(TASKS)
        self.assertGreaterEqual(len(self.work), 2)
        self.idea, self.other_idea = self.work[0].source_id, self.work[1].source_id

    def pin(self, name, parent="", worker="worker-A", idea=None):
        draft = spec(name, parent)
        receipt = self.pins.pin_candidate(draft, ROOT, reason="Retain a source edition")
        self.index.bind(idea_id=idea or self.idea, revision=receipt["revision"],
                        worker=worker, reason="Explicit reviewer-selected association")
        return receipt

    def test_checklist_is_exact_active_move_rows_not_new_ideas(self):
        known = {x.source_id for x in self.work}
        listing = self.index.ideas()
        self.assertEqual({i["idea_id"] for i in listing}, known)
        self.assertTrue(all(i["status"] == "SOURCE_RECORDED_NOT_COMPLETED" for i in listing))
        self.assertTrue(all(i["bound_branches"] == 0 for i in listing))
        self.assertFalse((self.directory / "runtime.jsonl").exists())

    def test_backtrack_and_sibling_help_are_visible_only_one_hop(self):
        parent = self.pin("Root")
        first = self.pin("Explore A", parent["revision"], "worker-A")
        peer = self.pin("Explore B", parent["revision"], "worker-B")
        grandchild = self.pin("Deep unexplored C", first["revision"], "worker-C")
        local = self.index.worker_frontier(idea_id=self.idea, revision=first["revision"],
                                            step_id="start", worker="worker-A")
        relations = {r["revision"]: r["relationship"] for r in local["visible_branches"]}
        self.assertEqual(relations[parent["revision"]], "DIRECT_PARENT")
        self.assertEqual(relations[peer["revision"]], "SHARED_PARENT")
        self.assertEqual(relations[grandchild["revision"]], "DIRECT_CHILD")
        self.assertEqual(len(relations), 3)
        self.assertNotIn("Deep unexplored C", str(local))
        self.assertFalse(local["claimed_global_worker_visibility"])
        self.assertFalse(local["native_relationships_verified"])
        self.assertFalse(local["current_view_authenticated_as_worker"])

        back = self.index.propose(kind="BACKTRACK", idea_id=self.idea,
                                  revision=first["revision"], step_id="start",
                                  worker="worker-A", target_revision=parent["revision"],
                                  reason="Return to original witnessed parent")
        help_ = self.index.propose(kind="HELP", idea_id=self.idea,
                                   revision=first["revision"], step_id="start",
                                   worker="worker-A", target_revision=peer["revision"],
                                   reason="Inspect peer branch source differences")
        self.assertEqual(back["event"]["witnessed_relation"], "DIRECT_PARENT")
        self.assertEqual(help_["event"]["witnessed_relation"], "SHARED_PARENT")
        self.assertFalse(help_["event"]["worker_help_executed"])
        peer_view = self.index.worker_frontier(
            idea_id=self.idea, revision=peer["revision"], step_id="start", worker="worker-B")
        self.assertEqual(peer_view["incoming_peer_help"], [{
            "from_worker": "worker-A",
            "from_revision": first["revision"],
            "source_step_id": "start",
            "reason": "Inspect peer branch source differences",
            "relationship": "SHARED_PARENT",
            "state": "PROPOSED_NOT_EXECUTED",
        }])
        self.assertFalse(back["event"]["rewind_executed"])
        self.assertEqual(len(self.pins.list_pins()), 4)
        self.assertFalse((self.directory / "runtime.jsonl").exists())

    def test_other_ideas_and_unrelated_roots_are_not_visible(self):
        root = self.pin("Origin")
        own = self.pin("Own", root["revision"], "worker-A")
        other_root = self.pin("Unrelated origin", "", "worker-X", self.other_idea)
        alien = self.pin("Unrelated child", other_root["revision"], "worker-Y", self.other_idea)
        unrelated_same_idea = self.pin("Independent idea root", "", "worker-Z")
        local = self.index.worker_frontier(idea_id=self.idea, revision=own["revision"],
                                            step_id="start", worker="worker-A")
        self.assertEqual([x["revision"] for x in local["visible_branches"]], [root["revision"]])
        dump = str(local)
        self.assertNotIn(alien["revision"], dump)
        self.assertNotIn(unrelated_same_idea["revision"], dump)
        with self.assertRaisesRegex(ValueError, "not visible"):
            self.index.propose(kind="HELP", idea_id=self.idea,
                               revision=own["revision"], step_id="start",
                               worker="worker-A", target_revision=alien["revision"],
                               reason="Pretend workers are connected")

    def test_missing_ancestor_binding_and_misidentified_worker_rejected(self):
        root = self.pins.pin_candidate(spec("Original"), ROOT, reason="Original")
        child = self.pins.pin_candidate(spec("Child", root["revision"]), ROOT, reason="Child")
        with self.assertRaisesRegex(ValueError, "parent must be bound"):
            self.index.bind(idea_id=self.idea, revision=child["revision"],
                            worker="worker-A", reason="Skip parent")
        self.index.bind(idea_id=self.idea, revision=root["revision"],
                        worker="worker-A", reason="Explicit source association")
        self.index.bind(idea_id=self.idea, revision=child["revision"],
                        worker="worker-B", reason="Explicit child")
        with self.assertRaisesRegex(ValueError, "no explicit current"):
            self.index.worker_frontier(idea_id=self.idea, revision=child["revision"],
                                       step_id="start", worker="worker-A")
        with self.assertRaisesRegex(ValueError, "cannot silently change"):
            self.index.bind(idea_id=self.idea, revision=child["revision"],
                            worker="worker-C", reason="Replace worker identity")
        with self.assertRaisesRegex(ValueError, "CURRENT source-recorded"):
            self.index.bind(idea_id="unknown", revision=root["revision"],
                            worker="worker-A", reason="Make an idea up")

    def test_backtracking_cannot_jump_to_sibling_and_help_requires_other_worker(self):
        parent = self.pin("Original")
        first = self.pin("Alpha", parent["revision"], "worker-A")
        same_worker = self.pin("Beta", parent["revision"], "worker-A")
        with self.assertRaisesRegex(ValueError, "directly witnessed parent"):
            self.index.propose(kind="BACKTRACK", idea_id=self.idea,
                               revision=first["revision"], step_id="start",
                               worker="worker-A", target_revision=same_worker["revision"],
                               reason="Not backwards")
        with self.assertRaisesRegex(ValueError, "another recorded worker"):
            self.index.propose(kind="HELP", idea_id=self.idea,
                               revision=first["revision"], step_id="start",
                               worker="worker-A", target_revision=same_worker["revision"],
                               reason="Not another worker")
        self.assertTrue(self.index.path.exists())  # explicit BINDs are journaled
        self.assertEqual([r["type"] for r in self.index._read()],
                         ["BIND", "BIND", "BIND"])  # no invalid movement proposal

    def test_no_auto_ranking_even_if_pins_claim_verification(self):
        parent = self.pin("Original")
        first = self.pin("Alpha", parent["revision"], "worker-A")
        second = self.pin("Beta", parent["revision"], "worker-B")
        local = self.index.worker_frontier(idea_id=self.idea, revision=first["revision"],
                                            step_id="start", worker="worker-A")
        peer = next(x for x in local["visible_branches"] if x["revision"] == second["revision"])
        self.assertFalse(peer["quality_superiority_proven"])
        self.assertFalse(peer["execution_authorized"])

    def test_tampered_binding_history_fails_closed(self):
        parent = self.pin("Initial")
        journal = self.index.path
        journal.write_text(journal.read_text().replace("OPERATOR_SELECTED_NOT_VERIFIED",
                                                        "CLAIM_NATIVE_VERIFIED"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.index.worker_frontier(idea_id=self.idea, revision=parent["revision"],
                                       step_id="start", worker="worker-A")


if __name__ == "__main__":
    unittest.main()
