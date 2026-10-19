"""Pinned workflow drafts: no silent promotion and no fabricated execution."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from systems.workspace.workflow_draft import SCHEMA, build_preview
from systems.workspace.workflow_pins import WorkflowPins

ROOT = Path(__file__).resolve().parents[2]
TEXT = "foundation/program_examples/stateless.json"
DESCRIBE = "foundation/program_examples/composition_target.json"


def base():
    return {
        "schema": SCHEMA, "title": "Count and classify",
        "provenance": "local workflow user review", "auto_connect": True,
        "steps": [
            {"id": "count", "label": "Count", "manifest": TEXT,
             "inputs": {"text": "one two three"}},
            {"id": "classify", "label": "Classify count", "manifest": DESCRIBE},
        ], "links": [],
    }


def improvement():
    return {
        "metric": "covered_validated_cases",
        "parent_value": 8, "branch_value": 9,
        "direction": "HIGHER",
        "comparison_scope": "same fixture and native source revision",
        "source_ref": "repo:verification-fixture",
        "witness_ref": "local:claim-needs-independent-recheck",
    }


class WorkflowPinTests(unittest.TestCase):
    def test_ordinary_pin_does_not_claim_native_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            p = pins.pin_candidate(base(), ROOT, reason="Keep inspectable baseline")
            self.assertEqual(p["status"], "CANDIDATE")
            self.assertFalse(p["native_verification"])
            self.assertFalse(p["execution_authorized"])
            self.assertEqual(p["revision"], build_preview(base(), ROOT)["revision"])
            self.assertEqual(len(pins.list_pins()), 1)
            self.assertEqual(pins.pin_candidate(base(), ROOT, reason="Keep inspectable baseline"), p)
            self.assertEqual(len(pins.list_pins()), 1)

    def test_discovered_better_branch_auto_pinned_as_unverified_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            parent = pins.pin_candidate(base(), ROOT, reason="First edition")
            child = copy.deepcopy(base())
            child["parent_revision"] = parent["revision"]
            child["steps"][1]["label"] = "Revised classification"
            result = pins.consider_discovery(child, ROOT, assessment=improvement())
            self.assertTrue(result["pinned"])
            self.assertEqual(result["status"], "CANDIDATE")
            self.assertFalse(result["native_verification"])
            self.assertEqual(result["parent_revision"], parent["revision"])
            self.assertEqual(len(pins.list_pins()), 2)
            self.assertFalse(pins.list_pins()[0]["whole_workflow_verified"])

    def test_native_verifier_callback_can_verify_observation_not_whole_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            parent = pins.pin_candidate(base(), ROOT, reason="Baseline")
            child = copy.deepcopy(base())
            child["parent_revision"] = parent["revision"]
            child["steps"][0]["label"] = "New counter"
            seen = []
            def native_verifier(preview, measurement):
                seen.append((preview["revision"], measurement["comparison_scope"]))
                return measurement["branch_value"] > measurement["parent_value"]
            result = pins.consider_discovery(
                child, ROOT, assessment=improvement(), verify_observation=native_verifier)
            self.assertTrue(seen)
            self.assertEqual(result["status"], "QUALITY_OBSERVATION_VERIFIED")
            self.assertTrue(result["native_verification"])
            self.assertFalse(result["whole_workflow_verified"])
            self.assertFalse(result["execution_authorized"])

    def test_equal_or_worse_branch_not_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            parent = pins.pin_candidate(base(), ROOT, reason="First")
            child = copy.deepcopy(base())
            child["parent_revision"] = parent["revision"]
            child["steps"][0]["label"] = "Another candidate"
            poor = improvement()
            poor["branch_value"] = poor["parent_value"]
            result = pins.consider_discovery(child, ROOT, assessment=poor)
            self.assertFalse(result["pinned"])
            self.assertEqual(len(pins.list_pins()), 1)

    def test_bad_assessment_and_failed_native_verifier_do_not_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            parent = pins.pin_candidate(base(), ROOT, reason="Original")
            child = copy.deepcopy(base())
            child["parent_revision"] = parent["revision"]
            child["steps"][0]["label"] = "Second"
            bad = improvement()
            bad["branch_value"] = float("nan")
            with self.assertRaises(ValueError):
                pins.consider_discovery(child, ROOT, assessment=bad)
            with self.assertRaises(ValueError):
                pins.consider_discovery(child, ROOT, assessment=improvement(),
                                        verify_observation=lambda *_: False)
            self.assertEqual(len(pins.list_pins()), 1)

    def test_discovery_requires_pinned_ancestry(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = base()
            spec["parent_revision"] = "0" * 64
            with self.assertRaises(ValueError):
                WorkflowPins(tmp).consider_discovery(spec, ROOT, assessment=improvement())
            self.assertFalse((Path(tmp) / "workflow_pins.jsonl").exists())

    def test_source_revisions_cannot_be_silently_mutated(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            old = pins.pin_candidate(base(), ROOT, reason="Approved by user")
            with self.assertRaises(ValueError):
                pins.pin_candidate(base(), ROOT, reason="Different meaning, same revision")
            other = copy.deepcopy(base())
            other["steps"][0]["label"] = "Changed, preserve original"
            new = pins.pin_candidate(other, ROOT, reason="New distinct version")
            self.assertNotEqual(old["revision"], new["revision"])
            self.assertEqual(pins.list_pins()[0]["revision"], old["revision"])
            self.assertEqual(len(pins.list_pins()), 2)

    def test_pinned_parent_diff_retains_original_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            baseline = pins.pin_candidate(base(), ROOT, reason="Initial workflow")
            child = copy.deepcopy(base())
            child["parent_revision"] = baseline["revision"]
            child["steps"][1]["label"] = "Different classification"
            child["steps"].append({
                "id": "alternative", "label": "Inspect other evidence", "manifest": TEXT,
                "path_role": "ALTERNATIVE", "inputs": {"text": "some other material"},
            })
            difference = pins.compare_branch(child, ROOT)
            self.assertEqual(difference["changed_steps"], ["classify"])
            self.assertEqual(difference["added_steps"], ["alternative"])
            self.assertEqual(difference["removed_steps"], [])
            self.assertFalse(difference["execution_authorized"])
            self.assertEqual(pins.list_pins()[0]["revision"], baseline["revision"])

    def test_ledger_replay_detects_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            pins = WorkflowPins(tmp)
            pins.pin_candidate(base(), ROOT, reason="Original")
            path = Path(tmp) / "workflow_pins.jsonl"
            original = path.read_text()
            path.write_text(original.replace("Original", "Tampered"), encoding="utf-8")
            with self.assertRaises(ValueError):
                pins.list_pins()


if __name__ == "__main__":
    unittest.main()
