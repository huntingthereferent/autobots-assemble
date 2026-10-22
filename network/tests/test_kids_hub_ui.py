"""Kids' hub links and Meta launcher must point to real shipped pages."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "docs/live"
HUB = LIVE / "kids.html"
META = LIVE / "meta.html"

class KidsHubTests(unittest.TestCase):
    def test_kids_hub_is_shipped_with_real_playable_destinations(self):
        html = HUB.read_text(encoding="utf-8")
        self.assertIn("<h1>Pick something", html)
        self.assertIn("Online School", html)
        self.assertIn("separate app server", html)
        for title, href in [
            ("Meow Lab 2", "cat-keyboard.html"),
            ("Rosey's Meow Machine", "roseys-cat-keyboard.html"),
            ("Pony Trail", "pony-trail.html"),
            ("WORLD48 Challenges", "../window48_challenges.html"),
        ]:
            self.assertIn(title, html)
            self.assertIn(f'href="{href}"', html)
            self.assertTrue((LIVE / href).resolve().is_file(), href)

    def test_meta_has_accessible_kids_entry_without_replacing_workstation(self):
        html = META.read_text(encoding="utf-8")
        self.assertIn('href="kids.html">KIDS</a>', html)
        self.assertNotIn('class="kids-access"', html)
        self.assertNotIn('class="kids-main-link"', html)
        self.assertIn('href="kids.html">KIDS</a>', html)
        self.assertIn('id="queued"', html)
        self.assertIn('id="running"', html)
        self.assertIn('id="trend"', html)
        self.assertIn('id="runs"', html)

if __name__ == "__main__":
    unittest.main()
