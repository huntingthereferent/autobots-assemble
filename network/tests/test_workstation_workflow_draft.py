"""Source-bound workflow draft construction tests; never execute user workers."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from foundation.program_kernel.graph import GraphError, GraphNode, validate_graph
from foundation.program_kernel.manifest import load_manifest
from systems.workspace.workflow_draft import SCHEMA, build_preview, commit_proposal
from systems.workspace.workstation_construction import WorkstationConstruction


ROOT = Path(__file__).resolve().parents[2]
TEXT = "foundation/program_examples/stateless.json"
DESCRIBE = "foundation/program_examples/composition_target.json"
STATEFUL = "foundation/program_examples/stateful.json"


def example() -> dict:
    return {
        "schema": SCHEMA, "title": "Inspect text transformations",
        "provenance": "user-authored example, not native proof",
        "auto_connect": True, "steps": [
            {"id": "normalize", "label": "Normalize and count", "manifest": TEXT,
             "inputs": {"text": "one two three"}},
            {"id": "describe", "label": "Describe count", "manifest": DESCRIBE},
        ], "links": [],
    }


class WorkflowDraftTests(unittest.TestCase):
    def test_unique_native_ports_generate_compatible_link_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = example()
            result = build_preview(spec, ROOT)
            self.assertEqual(result["order"], ["normalize", "describe"])
            self.assertEqual(result["generated_links"],
                             [{"from": "normalize", "output": "count",
                               "to": "describe", "input": "count"}])
            self.assertEqual(result["unresolved_inputs"], [])
            self.assertFalse(result["execution_authorized"])
            self.assertEqual(result["contract_check"], "STRUCTURAL_ONLY")
            self.assertFalse((Path(tmp) / "runtime.jsonl").exists())

    def test_import_records_actual_b9_nodes_and_proposed_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = example()
            record = commit_proposal(spec, ROOT, tmp)
            self.assertTrue((Path(tmp) / "runtime.jsonl").exists())
            nodes = record["projection"]["nodes"]
            self.assertEqual(len(nodes), 3)  # one root and two candidates
            self.assertEqual(len(record["candidate_ids"]), 2)
            self.assertFalse(record["execution_started"])
            self.assertFalse(record["native_verification"])
            self.assertTrue(all(not n["native_execution_admitted"] for n in nodes))
            self.assertTrue(all(n["contract_state"] == "PROPOSED" for n in nodes))
            links = set(map(tuple, record["projection"]["candidate_links"]))
            self.assertIn((record["candidate_ids"]["normalize"],
                           record["candidate_ids"]["describe"]), links)
            self.assertIn((record["candidate_ids"]["describe"],
                           record["goal_id"]), links)
            self.assertEqual(record["revision"], build_preview(spec, ROOT)["revision"])
            # Same exact edition can be re-imported without rewriting old events.
            before = (Path(tmp) / "runtime.jsonl").read_bytes()
            again = commit_proposal(spec, ROOT, tmp)
            self.assertEqual(again["goal_id"], record["goal_id"])
            self.assertEqual((Path(tmp) / "runtime.jsonl").read_bytes(), before)

    def test_new_edit_is_new_revision_old_graph_survives(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = example()
            a = commit_proposal(first, ROOT, tmp)
            revised = example()
            revised["steps"][1]["label"] = "Describe revised count"
            revised["parent_revision"] = a["revision"]
            b = commit_proposal(revised, ROOT, tmp)
            self.assertNotEqual(a["goal_id"], b["goal_id"])
            self.assertEqual(len(WorkstationConstruction(tmp).inspect(a["goal_id"])["nodes"]), 3)
            self.assertEqual(len(WorkstationConstruction(tmp).inspect(b["goal_id"])["nodes"]), 3)

    def test_ambiguous_generation_does_not_guess_or_overwrite_input(self):
        spec = example()
        spec["steps"].insert(1, {"id": "other", "label": "Other count",
                                  "manifest": TEXT, "inputs": {"text": "hello"}})
        preview = build_preview(spec, ROOT)
        self.assertFalse(preview["generated_links"])
        self.assertEqual(preview["ambiguous_links"], [
            {"to": "describe", "input": "count",
             "possible_sources": ["normalize", "other"]}])
        self.assertEqual(preview["unresolved_inputs"], [
            {"step": "describe", "input": "count", "state": "OPEN_NOT_LINKED"}])

    def test_optional_alternative_branch_not_collapsed(self):
        spec = example()
        spec["steps"][1]["path_role"] = "ALTERNATIVE"
        p = build_preview(spec, ROOT)
        self.assertEqual(p["draft"]["steps"][1]["path_role"], "ALTERNATIVE")
        with tempfile.TemporaryDirectory() as tmp:
            committed = commit_proposal(spec, ROOT, tmp)
            node = next(n for n in committed["projection"]["nodes"]
                        if n["id"] == committed["candidate_ids"]["describe"])
            self.assertEqual(node["path_role"], "ALTERNATIVE")
            self.assertEqual(node["source_options"][0]["execution_authorized"], False)

    def test_incompatible_explicit_link_refused_before_any_journal_write(self):
        spec = example()
        spec["auto_connect"] = False
        spec["links"] = [{"from": "normalize", "output": "normalized",
                          "to": "describe", "input": "count"}]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(GraphError):
                commit_proposal(spec, ROOT, tmp)
            self.assertFalse((Path(tmp) / "runtime.jsonl").exists())

    def test_unsafe_or_missing_manifest_refused(self):
        spec = example()
        for invalid in ("/tmp/external.json", "../outside.json", "foundation/program_examples/unknown.json"):
            spec["steps"][0]["manifest"] = invalid
            with self.assertRaises(ValueError):
                build_preview(spec, ROOT)

    def test_missing_inputs_are_visible_and_not_claimed_executable(self):
        spec = example()
        spec["auto_connect"] = False
        preview = build_preview(spec, ROOT)
        self.assertEqual(preview["unresolved_inputs"], [
            {"step": "describe", "input": "count", "state": "OPEN_NOT_LINKED"}])
        # Strict Program Foundation graph execution gate remains strict.
        manifest = load_manifest(ROOT / DESCRIBE)
        with self.assertRaises(GraphError):
            validate_graph({"describe": GraphNode(manifest)}, [])

    def test_cycles_and_conflicting_ports_fail_before_commit(self):
        spec = example()
        spec["steps"] = [
            {"id": "a", "label": "A", "manifest": TEXT},
            {"id": "b", "label": "B", "manifest": TEXT},
        ]
        spec["auto_connect"] = False
        spec["links"] = [
            {"from": "a", "output": "normalized", "to": "b", "input": "text"},
            {"from": "b", "output": "normalized", "to": "a", "input": "text"},
        ]
        with self.assertRaises(GraphError):
            build_preview(spec, ROOT)


if __name__ == "__main__":
    unittest.main()
