from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "companies" / "online-school" / "app" / "schedule_engine.py"

spec = importlib.util.spec_from_file_location("online_school_schedule_engine", ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class OnlineSchoolAppTests(unittest.TestCase):
    def test_full_monday_schedule_fits(self):
        tasks = engine.generate_tasks_for_day("2026-10-05")
        self.assertEqual(len(tasks), 11)
        titles = [t["title"] for t in tasks]
        for required in (
            "independent reading",
            "writing",
            "phonics workbook",
            "core academic workbook",
            "guided reading",
            "beginning writing",
            "mathematics",
            "science documentary / guided science study",
            "art / creative work",
            "history / social studies",
            "physical education outing",
        ):
            self.assertIn(required, titles)

    def test_wednesday_adds_three_hour_project(self):
        tasks = engine.generate_tasks_for_day("2026-10-07")
        self.assertEqual(len(tasks), 12)
        project = next(t for t in tasks if t["title"] == "shared hands-on science project")
        self.assertEqual(project["planned_minutes"], 180)

    def test_dated_theme_flows_into_generated_tasks(self):
        tasks = engine.generate_tasks_for_day("2026-10-05")
        math = next(t for t in tasks if t["title"] == "mathematics")
        self.assertEqual(math["notes"], "Whole, half, and quarter measurements")
        self.assertEqual(math["meta"]["math_mode"], "direct lesson")
        self.assertEqual(math["meta"]["theme"], "Recipes, kitchen safety, and measuring tools")

    def test_generation_is_idempotent(self):
        generated = engine.generate_tasks("2026-10-05", "2026-10-09")
        once, added_once = engine.merge_generated([], generated)
        twice, added_twice = engine.merge_generated(once, generated)
        self.assertEqual(added_once, len(generated))
        self.assertEqual(added_twice, 0)
        self.assertEqual(len(once), len(twice))

    def test_weekend_does_not_invent_recurring_school_tasks(self):
        self.assertEqual(engine.generate_tasks_for_day("2026-10-10"), [])

    def test_arbitrary_task_shape_can_extend_schedule(self):
        task = engine.validate_task({
            "date": "2026-10-05",
            "title": "Library research trip",
            "planned_minutes": 75,
            "learner_ids": ["track_a"],
            "kind": "outing",
            "scope": "individual",
            "notes": "Bring notebook",
            "meta": {"location_type": "library", "evidence": ["notes"]},
        })
        self.assertEqual(task["planned_minutes"], 75)
        self.assertEqual(task["kind"], "outing")
        self.assertEqual(task["meta"]["location_type"], "library")

    def test_http_surface_exposes_task_monitor_routes(self):
        server = (ROOT / "companies" / "online-school" / "app" / "server.py").read_text(encoding="utf-8")
        for route in (
            '"/api/state"',
            '"/api/tasks"',
            '"/api/today"',
            '"/api/generate"',
        ):
            self.assertIn(route, server)


if __name__ == "__main__":
    unittest.main()
