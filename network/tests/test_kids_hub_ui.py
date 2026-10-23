"""Kids' hub links return to the canonical execution viewer."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "docs/live"
HUB = LIVE / "kids.html"
WORK = LIVE / "work.html"

class KidsHubTests(unittest.TestCase):
    def test_kids_hub_is_shipped_with_real_playable_destinations(self):
        html = HUB.read_text(encoding="utf-8")
        self.assertIn("<h1>Pick something", html)
        self.assertIn("Online School", html)
        self.assertIn("The full private school app and worksheet generator still use a local server.", html)
        for title, href in [
            ("Meow Lab 2", "cat-keyboard.html"),
            ("Rosey's Meow Machine", "roseys-cat-keyboard.html"),
            ("Pony Trail", "pony-trail.html"),
            ("WORLD48 Challenges", "../window48_challenges.html"),
        ]:
            self.assertIn(title, html)
            self.assertIn(f'href="{href}"', html)
            self.assertTrue((LIVE / href).resolve().is_file(), href)

    def test_kids_hub_returns_to_single_execution_viewer(self):
        kids = HUB.read_text(encoding="utf-8")
        work = WORK.read_text(encoding="utf-8")
        self.assertIn('href="work.html"', kids)
        self.assertNotIn('href="meta.html"', kids)
        self.assertIn('href="school.html"', kids)
        self.assertIn('href="school.html">ONLINE SCHOOL</a>', work)
        self.assertIn('id="executions-tab"', work)

if __name__ == "__main__":
    unittest.main()
