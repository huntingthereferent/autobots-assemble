from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from weekly_itinerary import generate_week, generate_all_weeks


class WeeklyItineraryTests(unittest.TestCase):
    def learner(self):
        return {
            "id": "james",
            "display_name": "James",
            "age": 40,
            "grade_context": "",
            "placement": {
                "status": "complete",
                "completed_subjects": [
                    "mathematics", "reading", "writing", "science-research"
                ],
                "results": {
                    "mathematics": {"start_band": "secondary"},
                    "reading": {"submitted": True},
                    "writing": {"submitted": True},
                    "science-research": {"submitted": True},
                },
            },
        }

    def test_completed_placement_generates_one_bounded_week(self):
        week = generate_week(self.learner(), "2026-10-06")
        self.assertTrue(week["ready"])
        self.assertEqual(week["week_start"], "2026-10-05")
        self.assertEqual(week["week_end"], "2026-10-09")
        self.assertEqual(week["retest_date"], "2026-10-09")
        self.assertTrue(week["tasks"])

    def test_friday_is_retest(self):
        week = generate_week(self.learner(), "2026-10-06")
        friday = [task for task in week["tasks"] if task["date"] == "2026-10-09"]
        self.assertEqual(len(friday), 4)
        self.assertTrue(all((task.get("meta") or {}).get("week_phase") == "retest" for task in friday))
        self.assertTrue(all(task["source"] == "placement" for task in friday))

    def test_calendar_mirrors_generated_week(self):
        week = generate_week(self.learner(), "2026-10-06")
        self.assertEqual(len(week["calendar"]), len(week["tasks"]))

    def test_next_week_waits_for_previous_retest(self):
        learner = self.learner()
        state = {"learners": [learner], "tasks": []}
        first_tasks, _ = generate_all_weeks(state, "2026-10-06")
        state["tasks"] = first_tasks
        blocked, _ = generate_all_weeks(state, "2026-10-12")
        self.assertEqual(blocked, [])
        for task in state["tasks"]:
            if (task.get("meta") or {}).get("week_phase") == "retest":
                task["status"] = "done"
        next_tasks, _ = generate_all_weeks(state, "2026-10-12")
        self.assertTrue(next_tasks)


if __name__ == "__main__":
    unittest.main()
