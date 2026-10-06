from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"


class SchoolLayerBoundaryTests(unittest.TestCase):
    def read(self, name):
        return (APP / name).read_text(encoding="utf-8")

    def test_learning_engine_does_not_import_missouri_or_recordkeeping(self):
        text = self.read("weekly_itinerary.py").lower()
        self.assertNotIn("missouri", text)
        self.assertNotIn("recordkeeping", text)

    def test_recordkeeping_does_not_import_missouri_or_learning_engine(self):
        text = self.read("recordkeeping.py").lower()
        self.assertNotIn("missouri", text)
        self.assertNotIn("weekly_itinerary", text)

    def test_missouri_comparison_cannot_drive_week_generation(self):
        text = self.read("missouri_comparison.py").lower()
        self.assertIn("missouri_curriculum", text)
        self.assertNotIn("weekly_itinerary", text)
        self.assertNotIn("generate_week", text)

    def test_teaching_view_does_not_import_missouri(self):
        text = self.read("school_view.py").lower()
        self.assertNotIn("missouri_curriculum", text)
        self.assertNotIn("path_for_grade", text)

    def test_server_exposes_distinct_record_and_comparison_surfaces(self):
        text = self.read("server.py")
        self.assertIn('"/api/record"', text)
        self.assertIn('"/api/comparison"', text)
        self.assertIn('"/api/comparison/progress"', text)


if __name__ == "__main__":
    unittest.main()
