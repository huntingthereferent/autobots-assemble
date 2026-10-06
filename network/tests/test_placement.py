from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from placement import ADULT_MATH_BANDS, math_placement, placement_plan


class PlacementTests(unittest.TestCase):
    def test_adult_enters_four_part_placement(self):
        learner = {
            "id": "james",
            "display_name": "James",
            "age": 40,
            "grade_context": "",
        }
        plan = placement_plan(learner)
        self.assertEqual(
            [section["subject"] for section in plan],
            ["mathematics", "reading", "writing", "science-research"],
        )
        self.assertTrue(plan[0]["diagnostic"]["adult"])
        self.assertFalse(plan[0]["diagnostic"]["age_bounded"])
        self.assertFalse(plan[0]["diagnostic"]["grade_bounded"])

    def test_adult_math_placement_spans_learning_line(self):
        diagnostic = math_placement(40, "", seed=17)
        self.assertEqual(
            [band["id"] for band in diagnostic["bands"]],
            ["foundations", "secondary", "advanced", "higher"],
        )
        domains = {item["domain"] for item in diagnostic["items"]}
        expected = {
            domain
            for band in ADULT_MATH_BANDS
            for domain in band.domains
        }
        self.assertEqual(domains, expected)

    def test_child_math_placement_is_bounded_by_grade_context(self):
        diagnostic = math_placement(8, "3", seed=17)
        self.assertFalse(diagnostic["adult"])
        self.assertTrue(diagnostic["age_bounded"])
        self.assertTrue(diagnostic["grade_bounded"])
        self.assertEqual(len(diagnostic["bands"]), 1)
        self.assertLess(len(diagnostic["items"]), 10)


if __name__ == "__main__":
    unittest.main()
