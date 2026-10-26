"""Executable NIH Phase 1 oscillation against actual Traceworks boundaries.

Run: python -m unittest -v network.tests.test_nih_traceworks_oscillation
No native NIH execution is claimed by this test; it challenges the real comparator
and public projection with controlled inputs, preserving failures as test failures.
"""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from systems.workspace.nih_phase1_output_compare import CANDIDATES, compare
from views.traces.research_live import projection


def original_snapshot():
    return {
        "schema": "workstation-research-continuity/v1",
        "source_records": [
            {"path": "research/nih_audit/original.json", "kind": "EXPERIMENT",
             "title": "NIH Phase 1 original", "state": "MOVE_WITH_WALL",
             "scope": "source-owned; not native execution",
             "boundary": "Native run unverified", "next": "", "walls": ["verify run"]},
        ],
        "documented_marks": [
            {"path": "research/nih_audit/notes.md", "kind": "DOCUMENTED_MOVEMENT",
             "line": 9, "heading": "Movement: comparison"},
        ],
        "totals": {"source_files": 2, "structured_records": 1,
                   "explicit_wall_entries": 1, "documented_wall_headings": 0,
                   "documented_movement_headings": 1},
    }


class TraceworksOscillation(unittest.TestCase):
    def test_repeatable_source_projection_keeps_evidence_class(self):
        source = original_snapshot()
        a = projection(source)
        b = projection(source)
        self.assertEqual(a, b)
        self.assertEqual(a["records"][0]["source_type"], "EXPERIMENT")
        self.assertEqual(a["movements"][0]["evidence"], "structured-source-state")
        self.assertEqual(a["movements"][1]["evidence"], "documented-heading-only")
        self.assertIn("not a native verified execution", a["movements"][1]["boundary"])
        self.assertIn("does not establish a causal relationship", a["boundary"])
        self.assertNotIn("native_execution", a)

    def test_duplicate_identity_rejected_at_projection_boundary(self):
        source = original_snapshot()
        source["source_records"].append(dict(source["source_records"][0]))
        with self.assertRaises(ValueError):
            projection(source)

    def test_unrecognized_source_schema_rejected(self):
        source = original_snapshot()
        source["schema"] = "unknown"
        with self.assertRaises(ValueError):
            projection(source)

    def test_oscillate_missing_valid_failed_and_recovered_receipts(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            empty = compare(root)
            self.assertEqual(empty["selection"], "UNDETERMINED")
            self.assertEqual(empty["candidates"]["frontier"]["status"], "UNKNOWN")
            path = root / "frontier" / CANDIDATES["frontier"][0]
            path.parent.mkdir()
            document = {"schema": CANDIDATES["frontier"][1]}
            document.update(dict(CANDIDATES["frontier"][2:]))
            path.write_text(json.dumps(document), encoding="utf-8")
            exit_file = path.parent / "exit-code.txt"
            exit_file.write_text("0", encoding="utf-8")
            valid = compare(root)
            self.assertEqual(valid["candidates"]["frontier"]["status"], "REPORTED_PASS")
            self.assertEqual(valid["selection"], "UNDETERMINED")
            exit_file.write_text("1", encoding="utf-8")
            failed = compare(root)
            self.assertEqual(failed["candidates"]["frontier"]["status"], "REPORTED_FAIL")
            exit_file.write_text("0", encoding="utf-8")
            restored = compare(root)
            self.assertEqual(restored["candidates"]["frontier"]["status"], "REPORTED_PASS")
            self.assertEqual(valid, restored)
            self.assertEqual(restored["selection"], "UNDETERMINED")

    def test_forged_schema_cannot_promote_to_pass(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "frontier" / CANDIDATES["frontier"][0]
            path.parent.mkdir()
            path.write_text('{"schema":"forged"}', encoding="utf-8")
            (path.parent / "exit-code.txt").write_text("0", encoding="utf-8")
            result = compare(root)
            self.assertEqual(result["candidates"]["frontier"]["status"], "REPORTED_FAIL")
            self.assertEqual(result["selection"], "UNDETERMINED")


if __name__ == "__main__":
    unittest.main()
