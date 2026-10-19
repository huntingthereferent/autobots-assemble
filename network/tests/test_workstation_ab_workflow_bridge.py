"""Real A/B package -> pinned Workstation branch, native source-only observation."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
# The general protocol suite does not install optional product packages.
# Test the *same* installable A/B code in its declared source location.
sys.path.insert(0, str(ROOT / "tools/ab-provenance/src"))

from systems.workspace.workflow_draft import SCHEMA
from systems.workspace.workflow_ab_bridge import ABWorkflowSources, ABWorkflowSourceError
from systems.workspace.workflow_pins import WorkflowPins


def draft():
    return {
        "schema": SCHEMA, "title": "Preserve two source-owning workers",
        "provenance": "native worker source relationship tests",
        "auto_connect": True,
        "steps": [
            {"id": "first", "label": "Original worker one",
             "manifest": "foundation/program_examples/stateless.json",
             "inputs": {"text": "one two three"}},
            {"id": "second", "label": "Worker two follows native evidence",
             "manifest": "foundation/program_examples/composition_target.json"},
        ],
        "links": [],
    }


def source(task_id, filename):
    return {"task_id": task_id, "native_sources": [{
        "source": filename,
        "sha256": sha256((ROOT / filename).read_bytes()).hexdigest(),
    }]}


class ABWorkflowSourceTests(unittest.TestCase):
    def source_rows(self):
        return [source("worker-1", "runtime/pool_evaluator.py"),
                source("worker-2", "runtime/swallow_first.py")]

    def test_actual_ab_tool_inspects_declared_bindings_without_execution(self):
        with TemporaryDirectory() as tmp:
            bridge = ABWorkflowSources(ROOT, tmp)
            view = bridge.inspect(draft(), self.source_rows(),
                                  {"first": "worker-1", "second": "worker-2"})
            record = view["record"]
            self.assertEqual(record["ab_capability"], "ab-tool/provenance-graph-v1")
            self.assertEqual(record["ab_graph_summary"]["relations"], 2)
            self.assertEqual(record["relation_scope"], "SOURCE_REFERENCES_ONLY")
            self.assertTrue(record["source_bytes_rechecked"])
            self.assertFalse(record["native_result_verified"])
            self.assertFalse(record["branch_quality_verified"])
            self.assertFalse(record["native_worker_executed"])
            self.assertFalse(record["execution_authorized"])
            self.assertEqual(record["unbound_steps"], [])
            self.assertFalse((Path(tmp) / "workflow_ab_source_links.jsonl").exists())

    def test_record_only_exact_pinned_branch_and_preserve_prior_version(self):
        with TemporaryDirectory() as tmp:
            sources = ABWorkflowSources(ROOT, tmp)
            pins = WorkflowPins(tmp)
            first = draft()
            with self.assertRaisesRegex(ABWorkflowSourceError, "pinned"):
                sources.record_for_pinned_branch(first, self.source_rows(),
                                                 {"first": "worker-1"})
            original = pins.pin_candidate(first, ROOT, reason="Preserve baseline")
            receipt = sources.record_for_pinned_branch(
                first, self.source_rows(), {"first": "worker-1", "second": "worker-2"})
            self.assertTrue(receipt["recorded"])
            self.assertEqual(receipt["record"]["draft_revision"], original["revision"])
            path = Path(tmp) / "workflow_ab_source_links.jsonl"
            before = path.read_bytes()
            second = sources.record_for_pinned_branch(
                first, self.source_rows(), {"first": "worker-1", "second": "worker-2"})
            self.assertFalse(second["recorded"])
            self.assertEqual(path.read_bytes(), before)
            changed = deepcopy(first)
            changed["parent_revision"] = original["revision"]
            changed["steps"][1]["label"] = "New alternative branch"
            new_pin = pins.pin_candidate(changed, ROOT, reason="Keep new revision")
            self.assertNotEqual(new_pin["revision"], original["revision"])
            self.assertEqual(len(sources.list_records(original["revision"])), 1)
            self.assertEqual(sources.list_records(new_pin["revision"]), [])
            self.assertEqual(pins.list_pins()[0]["revision"], original["revision"])

    def test_unmatched_or_outside_source_stays_wall(self):
        with TemporaryDirectory() as tmp:
            bridge = ABWorkflowSources(ROOT, tmp)
            rows = self.source_rows()
            rows[0]["native_sources"][0]["sha256"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                bridge.inspect(draft(), rows, {"first": "worker-1"})
            with self.assertRaisesRegex(ABWorkflowSourceError, "absent"):
                bridge.inspect(draft(), self.source_rows(), {"first": "unknown"})
            with self.assertRaisesRegex(ABWorkflowSourceError, "known steps"):
                bridge.inspect(draft(), self.source_rows(), {"imaginary": "worker-1"})
            self.assertFalse(bridge.path.exists())

    def test_unbound_steps_remain_visible(self):
        with TemporaryDirectory() as tmp:
            view = ABWorkflowSources(ROOT, tmp).inspect(
                draft(), self.source_rows(), {"first": "worker-1"})
            self.assertEqual(view["record"]["unbound_steps"], ["second"])
            self.assertFalse(view["record"]["branch_quality_verified"])

    def test_journal_ancestry_tampering_detected(self):
        with TemporaryDirectory() as tmp:
            bridge = ABWorkflowSources(ROOT, tmp)
            pins = WorkflowPins(tmp)
            pins.pin_candidate(draft(), ROOT, reason="Original")
            bridge.record_for_pinned_branch(
                draft(), self.source_rows(), {"first": "worker-1"})
            journal = bridge.path
            before = journal.read_text(encoding="utf-8")
            journal.write_text(before.replace("SOURCE_REFERENCES_ONLY", "ALLEGED_NATIVE_PROOF"),
                               encoding="utf-8")
            with self.assertRaisesRegex(ABWorkflowSourceError, "changed"):
                bridge.list_records()


if __name__ == "__main__":
    unittest.main()
