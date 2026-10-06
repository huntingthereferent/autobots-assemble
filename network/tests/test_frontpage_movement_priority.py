
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "runtime" / "http" / "index.html"


class FrontpageMovementPriorityTests(unittest.TestCase):
    def test_live_movement_precedes_area_directory(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertLess(html.index('id="live-feed"'), html.index('id="areas"'))

    def test_internal_systems_are_not_called_external_sources(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertIn("Your systems", html)
        self.assertIn("External feeds", html)
        self.assertNotIn("Connected sources", html)

    def test_current_trail_is_visible_before_live_items(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertLess(html.index('id="trail-bar"'), html.index('id="live-feed"'))


if __name__ == "__main__":
    unittest.main()
