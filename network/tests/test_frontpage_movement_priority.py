
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

    def test_live_filters_use_independent_roles_and_medium(self):
        app = (ROOT / "runtime" / "http" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("item.source_kind", app)
        self.assertIn("roles.includes(filter)", app)
        self.assertIn('item.medium === "video"', app)

    def test_source_action_is_clickable_title_not_large_button_row(self):
        app = (ROOT / "runtime" / "http" / "app.js").read_text(encoding="utf-8")
        self.assertIn('titleLink.className = "live-title-link"', app)
        self.assertNotIn('open.textContent = "Open source"', app)
        self.assertNotIn('open.textContent = item.medium === "video"', app)

    def test_inert_search_and_post_controls_are_not_presented(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertNotIn('id="hub-search"', html)
        self.assertNotIn('id="global-search"', html)
        self.assertNotIn('id="composer-post"', html)
        self.assertNotIn('id="composer-text"', html)
        self.assertNotIn(">Activity<", html)


if __name__ == "__main__":
    unittest.main()
