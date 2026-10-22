"""Source-level checks for the isolated Pony Trail browser game."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "docs/live/pony-trail.html"
WORK = ROOT / "docs/live/work.html"

class PonyTrailUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = GAME.read_text(encoding="utf-8")
        cls.work = WORK.read_text(encoding="utf-8")

    def test_workstation_nav_links_to_game(self):
        self.assertIn('href="pony-trail.html"', self.work)

    def test_touch_and_keyboard_controls_exist(self):
        for token in ('id="jump"', 'id="start"', 'id="pause"', 'id="sound"',
                      '"Space"', '"ArrowUp"', '"ArrowLeft"', '"ArrowRight"',
                      '"KeyP"', '"KeyR"'):
            with self.subTest(token=token):
                self.assertIn(token, self.page)

    def test_self_contained_and_source_boundary(self):
        self.assertIn('canvas id="game"', self.page)
        self.assertIn('requestAnimationFrame(frame)', self.page)
        self.assertIn('work.html', self.page)
        for token in ('<script src=', 'fetch(', 'XMLHttpRequest', 'WebSocket', '<iframe'):
            with self.subTest(token=token):
                self.assertNotIn(token, self.page)

    def test_play_options(self):
        for horse in ('data-horse="cocoa"', 'data-horse="blossom"', 'data-horse="moon"'):
            self.assertIn(horse, self.page)
        for trail in ('value="meadow"', 'value="sunset"', 'value="night"'):
            self.assertIn(trail, self.page)

if __name__ == "__main__":
    unittest.main()
