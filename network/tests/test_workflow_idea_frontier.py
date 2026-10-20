"""Existing task-list ideas: source-scoped branch visibility and nonexecuting help."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
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
        # The direct child's MATCHED current step is in front of us;
        # its internal graph and any further descendants still are not.
        direct = next(r for r in local["visible_branches"]
                      if r["revision"] == grandchild["revision"])
        self.assertEqual(direct["local_step_delta"]["neighbor_step_label"],
                         "Deep unexplored C")
        self.assertNotIn("steps", direct)
        self.assertNotIn("links", direct)
        self.assertNotIn("draft", direct)
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
        self.assertEqual(len(peer_view["incoming_peer_help"]), 1)
        proposed = peer_view["incoming_peer_help"][0]
        self.assertEqual(proposed["from_worker"], "worker-A")
        self.assertEqual(proposed["from_revision"], first["revision"])
        self.assertEqual(proposed["source_step_id"], "start")
        self.assertEqual(proposed["reason"], "Inspect peer branch source differences")
        self.assertEqual(proposed["relationship"], "SHARED_PARENT")
        self.assertEqual(proposed["state"], "AWAITING_REVIEW")
        self.assertEqual(len(proposed["proposal_ref"]), 64)
        self.assertFalse(proposed["worker_help_executed"])
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

    def test_shared_parent_without_matching_step_does_not_create_help_relation(self):
        parent = self.pin("Root with known step")
        own = self.pin("Own branch step", parent["revision"], "worker-A")
        unrelated_step = spec("Peer unrelated step", parent["revision"])
        unrelated_step["steps"][0]["id"] = "different-step"
        other = self.pins.pin_candidate(
            unrelated_step, ROOT, reason="Separate declared step")
        self.index.bind(
            idea_id=self.idea, revision=other["revision"], worker="worker-B",
            reason="Different recorded step under same parent")
        view = self.index.worker_frontier(
            idea_id=self.idea, revision=own["revision"],
            step_id="start", worker="worker-A")
        candidate = next(x for x in view["visible_branches"]
                         if x["revision"] == other["revision"])
        self.assertFalse(candidate["same_step_id_present"])
        self.assertIsNone(candidate["local_step_delta"])
        with self.assertRaisesRegex(ValueError, "another recorded worker"):
            self.index.propose(
                kind="HELP", idea_id=self.idea, revision=own["revision"],
                step_id="start", worker="worker-A",
                target_revision=other["revision"], reason="Only share parent")
        # The mere parent association did not record any help or view leak.
        self.assertTrue(all(e["type"] == "BIND" for e in self.index._read()))
        self.assertEqual(view["incoming_peer_help"], [])
        self.assertEqual(view["outgoing_help_reviews"], [])

    def test_no_auto_ranking_even_if_pins_claim_verification(self):
        parent = self.pin("Original")
        first = self.pin("Alpha", parent["revision"], "worker-A")
        second = self.pin("Beta", parent["revision"], "worker-B")
        local = self.index.worker_frontier(idea_id=self.idea, revision=first["revision"],
                                            step_id="start", worker="worker-A")
        peer = next(x for x in local["visible_branches"] if x["revision"] == second["revision"])
        self.assertFalse(peer["quality_superiority_proven"])
        self.assertFalse(peer["execution_authorized"])

    def test_current_native_manifest_drift_disables_branch_view(self):
        with TemporaryDirectory() as temp:
            local = Path(temp)
            repo = local / "repo"
            manifest = repo / MANIFEST
            manifest.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / MANIFEST, manifest)
            (repo / "TASKS.md").write_text(
                "# Tasks\\n\\n## Active ALL WORK\\n"
                "| Work | Lane | State | Next movement |\\n"
                "|---|---|---|---|\\n"
                "| [Original work](foundation/PROGRAM_FOUNDATION.md) | Test | MOVE | Observe sources |\\n",
                encoding="utf-8",
            )
            # Literal line breaks are the Markdown ledger's native shape.
            taskfile = repo / "TASKS.md"
            taskfile.write_text(taskfile.read_text().replace("\\n", "\n"), encoding="utf-8")
            store = local / "runtime"
            manager = WorkflowPins(store)
            pinned = manager.pin_candidate(spec("Local original"), repo, reason="Exact source")
            index = IdeaFrontier(repo, store)
            idea_id = next(iter(index._active()))
            index.bind(idea_id=idea_id, revision=pinned["revision"],
                       worker="worker-A", reason="Explicit source")
            self.assertEqual(index.worker_frontier(
                idea_id=idea_id, revision=pinned["revision"],
                step_id="start", worker="worker-A")["visible_branches"], [])
            changed = json.loads(manifest.read_text(encoding="utf-8"))
            changed["referent"] = changed["referent"] + " modified"
            manifest.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                index.worker_frontier(idea_id=idea_id, revision=pinned["revision"],
                                      step_id="start", worker="worker-A")

    def test_native_handoff_supplies_task_and_actor_without_caller_guesswork(self):
        from runtime.engine import HandoffRuntime
        from runtime.journal import RuntimeJournal
        from runtime.repository_tasks import admit_active_work
        local_runtime = HandoffRuntime(
            event_store=RuntimeJournal(self.directory / "runtime.jsonl"))
        admitted = admit_active_work(local_runtime, TASKS, actor_id="james")
        self.assertEqual(len(admitted), len(self.work))
        first = self.pin("Original native step", worker="james")
        child = self.pin("Alternative native step", first["revision"],
                         worker="worker-B")
        handoff_id = "repo-work-" + self.idea
        before = (self.directory / "runtime.jsonl").read_bytes()
        view = self.index.native_handoff_frontier(
            local_runtime, handoff_id=handoff_id,
            revision=first["revision"], step_id="start")
        self.assertEqual(view["native_handoff"]["to_actor"], "james")
        self.assertEqual(view["native_handoff"]["source_work_id"], self.idea)
        self.assertEqual(view["position"]["worker"], "james")
        self.assertEqual(view["visible_branches"][0]["revision"], child["revision"])
        self.assertTrue(view["native_handoff"]["task_origin_rechecked"])
        self.assertFalse(view["native_handoff"]["actor_identity_authenticated"])
        with self.assertRaisesRegex(ValueError, "no explicit"):
            self.index.native_handoff_frontier(
                local_runtime, handoff_id=handoff_id,
                revision=child["revision"], step_id="start")
        with self.assertRaisesRegex(ValueError, "no explicit"):
            self.index.native_handoff_frontier(
                local_runtime, handoff_id="repo-work-" + self.other_idea,
                revision=first["revision"], step_id="start")
        self.assertEqual((self.directory / "runtime.jsonl").read_bytes(), before)

    def test_native_handoff_help_is_visible_to_exact_peer_at_next_observation(self):
        from runtime.engine import HandoffRuntime
        from runtime.journal import RuntimeJournal
        from runtime.repository_tasks import admit_active_work
        runtime = HandoffRuntime(
            event_store=RuntimeJournal(self.directory / "runtime.jsonl"))
        admit_active_work(runtime, TASKS, actor_id="james")
        parent = self.pin("Native root", worker="james")
        first = self.pin("Worker branch", parent["revision"], worker="james")
        peer = self.pin("Peer approach", parent["revision"], worker="worker-B")
        caller = "repo-work-" + self.idea
        proposal = self.index.propose_from_native_handoff(
            runtime, handoff_id=caller, revision=first["revision"],
            step_id="start", target_revision=peer["revision"],
            kind="HELP", reason="Matching declared step exposes a different label")
        self.assertEqual(proposal["event"]["target_revision"], peer["revision"])
        self.assertFalse(proposal["event"]["worker_help_executed"])
        peer_view = self.index.worker_frontier(
            idea_id=self.idea, revision=peer["revision"], step_id="start",
            worker="worker-B")
        self.assertEqual(peer_view["incoming_peer_help"][0]["from_revision"],
                         first["revision"])
        first_view = self.index.native_handoff_frontier(
            runtime, handoff_id=caller, revision=first["revision"],
            step_id="start")
        self.assertEqual(first_view["visible_branches"][1]["local_step_delta"]["scope"],
                         "MATCHED_DECLARED_STEP_ONLY_NOT_SUPERIORITY")
        self.assertFalse(first_view["visible_branches"][1]["quality_superiority_proven"])

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
