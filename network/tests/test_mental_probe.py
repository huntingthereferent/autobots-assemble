from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from placement import placement_plan
from weekly_itinerary import generate_week


class MentalProbeTests(unittest.TestCase):
    def adult(self):
        return {
            "id": "james",
            "display_name": "James",
            "age": 40,
            "grade_context": "",
            "placement": {
                "status": "complete",
                "completed_subjects": ["mathematics", "reading", "writing", "science-research"],
                "results": {
                    "mathematics": {
                        "start_band": "arithmetic",
                        "first_wall": {
                            "domain": "multiplication",
                            "prompt": "6 x 4",
                            "wall": "stuck",
                        },
                    }
                },
            },
        }

    def test_adult_math_starts_with_mental_arithmetic(self):
        section = placement_plan(self.adult())[0]
        diagnostic = section["diagnostic"]
        self.assertEqual(section["title"], "Mental math probe")
        self.assertEqual(diagnostic["kind"], "mental-probe")
        self.assertEqual(diagnostic["bands"][0]["id"], "arithmetic")
        self.assertEqual(
            [item["prompt"] for item in diagnostic["items"]],
            ["7 + 8", "15 - 6", "6 x 4", "24 / 6", "18 + 27"],
        )

    def test_recorded_wall_drives_week_focus(self):
        week = generate_week(self.adult(), "2026-10-06")
        math_tasks = [
            task for task in week["tasks"]
            if task["category"] == "mathematics"
            and (task.get("meta") or {}).get("week_phase") == "learn"
        ]
        self.assertTrue(math_tasks)
        self.assertTrue(all("6 x 4" in task["notes"] for task in math_tasks))
        self.assertTrue(all("multiplication" in task["notes"] for task in math_tasks))


if __name__ == "__main__":
    unittest.main()
