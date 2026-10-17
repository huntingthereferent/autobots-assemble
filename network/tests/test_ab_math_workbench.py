"""Regression checks for the explicit finite A/B workbench and REA boundary."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.ab_math_workbench import (
    ClassifiedWindow,
    compare,
    inspect_rea_evidence,
    render_svg,
    survey,
    trace,
)


class AbMathWorkbenchTests(unittest.TestCase):
    def test_declared_family_summary_keeps_all_movements_and_walls(self):
        result = survey()
        self.assertEqual(result["certificate"]["status"],
                         "CLOSED_DECLARED_SHEAR_ORBITS_WITH_FOUR_FULL_STATE_CLASSES")
        self.assertEqual(len(result["worlds"]), 12)
        self.assertEqual(len(result["movements"]), 21)
        self.assertEqual(len(result["walls"]), 3)
        self.assertEqual(len(result["unordered_pair_comparisons"]), 66)
        self.assertEqual(
            sum(x["witness_shear"] is not None
                for x in result["unordered_pair_comparisons"]), 12)
        self.assertEqual(
            {x["fixed_B_depth_3"] for x in result["worlds"]}, {0, 3, 6, 9})

    def test_comparison_preserves_witness_and_obstruction(self):
        preserving = compare(ClassifiedWindow(1, 0), ClassifiedWindow(1, 2))
        self.assertEqual(preserving["status"], "ALL_DEPTH_FULL_STATE_CONJUGACY")
        self.assertEqual(preserving["witness_shear"], 2)
        obstruction = compare(ClassifiedWindow(1, 0), ClassifiedWindow(2, 0))
        self.assertEqual(obstruction["status"], "INEQUIVALENT_FIXED_B_AT_DEPTH_THREE")
        self.assertEqual(obstruction["obstruction_depth"], 3)
        self.assertIsNone(obstruction["witness_shear"])

    def test_trace_checks_inverse_at_each_step(self):
        output = trace(ClassifiedWindow(2, 1), "ABABBABA", 5)
        self.assertEqual(len(output["steps"]), 8)
        self.assertTrue(output["all_steps_reversible"])
        self.assertEqual(output["origin"], (0, 0, 0, 0, 0))
        with self.assertRaises(ValueError):
            trace(ClassifiedWindow(0, 0), "ABX", 3)
        with self.assertRaises(ValueError):
            trace(ClassifiedWindow(0, 0), "A", 9)

    def test_svg_displays_actual_family_and_walls(self):
        svg = render_svg(survey())
        self.assertIn("<svg", svg)
        self.assertIn("k3 c2", svg)
        self.assertIn("fixed B: 0", svg)
        self.assertEqual(svg.count("WALL ↓"), 3)
        self.assertNotIn("<script", svg)

    def test_rea_projection_keeps_digest_and_unknowns_without_math_claim(self):
        original = {
            "evidence_id": "ev-test-only",
            "analysis_profile": None,
            "normalized_result": {
                "coverage": {"status": "unknown"},
                "limitations": ["not run"],
                "unknowns": [{"reason": "dynamic property"}],
            },
        }
        with TemporaryDirectory() as d:
            path = Path(d) / "evidence.json"
            raw = json.dumps(original, sort_keys=True).encode()
            path.write_bytes(raw)
            output = inspect_rea_evidence(path)
            self.assertEqual(output["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(output["coverage"]["status"], "unknown")
            self.assertEqual(output["unknowns"], [{"reason": "dynamic property"}])
            self.assertEqual(output["status"], "IMPORTED_NOT_MATH_WITNESSED")
            path.write_text('{"arbitrary":true}', encoding="utf-8")
            with self.assertRaises(ValueError):
                inspect_rea_evidence(path)



class ReaBridgeTests(unittest.TestCase):
    def test_explicit_rea_scan_preserves_real_output_without_math_proof(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from tools.rea_ab_bridge import scan_javascript_target

        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "chosen-app"
            target.mkdir()
            evidence = root / "rea-evidence.json"
            reference = root / "rea-reference.json"
            sample = {
                "evidence_id": "ev-test",
                "analysis_profile": None,
                "normalized_result": {
                    "coverage": {"status": "unknown"},
                    "unknowns": ["dynamic edge"],
                    "limitations": ["static only"],
                },
            }

            def fake_run(argv, *, stdout, stderr, timeout, check):
                self.assertEqual(argv[1], "analyze-javascript-application")
                self.assertEqual(argv[-1], "--json")
                stdout.write(json.dumps(sample).encode("utf-8"))
                return SimpleNamespace(returncode=0, stderr=b"")

            with patch("tools.rea_ab_bridge.shutil.which", return_value="/mock/rea"), \
                    patch("tools.rea_ab_bridge.subprocess.run", side_effect=fake_run):
                report = scan_javascript_target(target, evidence, reference)

            self.assertTrue(evidence.exists())
            self.assertTrue(reference.exists())
            self.assertEqual(report["status"], "REA_EVIDENCE_SAVED_MATH_WITNESS_OPEN")
            self.assertIsNone(report["mathematical_correspondence"])
            self.assertEqual(json.loads(evidence.read_text())["evidence_id"], "ev-test")
            self.assertEqual(json.loads(reference.read_text())["sha256"],
                             hashlib.sha256(evidence.read_bytes()).hexdigest())

    def test_missing_rea_and_existing_output_are_explicit_walls(self):
        from unittest.mock import patch
        from tools.rea_ab_bridge import scan_javascript_target
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "app"
            target.mkdir()
            evidence, reference = root / "evidence.json", root / "reference.json"
            with patch("tools.rea_ab_bridge.shutil.which", return_value=None):
                with self.assertRaisesRegex(ValueError, "not installed"):
                    scan_javascript_target(target, evidence, reference)
            self.assertFalse(evidence.exists())
            evidence.write_text("existing")
            with self.assertRaisesRegex(ValueError, "must not already exist"):
                scan_javascript_target(target, evidence, reference)

if __name__ == "__main__":
    unittest.main()
