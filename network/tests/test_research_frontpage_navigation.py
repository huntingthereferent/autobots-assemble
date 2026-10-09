"""Research homepage must provide reachable entrances without invented native apps."""
from pathlib import Path
import re
import unittest
import json

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "runtime/http/index.html").read_text(encoding="utf-8")
JS = (ROOT / "runtime/http/app.js").read_text(encoding="utf-8")
CATALOG = json.loads((ROOT / "runtime/http/site_catalog.json").read_text(encoding="utf-8"))


class ResearchFrontpageNavigationTests(unittest.TestCase):
    def test_related_system_entries_are_real_links_with_existing_targets(self):
        targets = set(re.findall(r'data-related-system="[^"]+" href="#area-([^"]+)"', HTML))
        self.assertEqual(len(re.findall(r'data-related-system=', HTML)), 13)
        self.assertEqual(targets, {"learn", "organize", "work", "explore", "build"})
        available = {x["id"] for x in CATALOG["areas"]}
        self.assertTrue(targets <= available)
        self.assertNotIn('data-source="school"', HTML)
        self.assertIn('window.addEventListener("hashchange", function()', JS)
        self.assertIn('updateNavigationState();', JS)
        self.assertIn('details.open = true', JS)

    def test_native_article_link_never_waits_on_trace_write(self):
        self.assertIn('titleLink.href = href', JS)
        self.assertIn('titleLink.target = "_blank"', JS)
        self.assertIn('titleLink.rel = "noopener noreferrer"', JS)
        self.assertIn('recordLiveTouch(item).catch(showError)', JS)
        self.assertNotIn('window.open("about:blank"', JS)
        self.assertNotIn('popup.location = item.url', JS)

    def test_variable_local_content_never_injected_as_markup(self):
        self.assertIn('label.textContent = title', JS)
        self.assertIn('description.textContent = meta', JS)
        self.assertIn('marker.textContent = value', JS)
        self.assertNotIn('el.innerHTML =', JS)
        self.assertIn('acknowledge.dataset.id = x.id', JS)
        self.assertIn('extra.dataset.id = t.task_id', JS)

    def test_current_research_a_b_survives(self):
        self.assertIn('id="research-index"', HTML)
        self.assertIn('id="ticker-expanded"', HTML)
        self.assertIn('id="mobile-live-sources"', HTML)
        self.assertIn('id="live-feed"', HTML)
        self.assertIn('id="trail-bar"', HTML)
        self.assertIn('aria-label="Start James daily operations"', HTML)
        self.assertIn('liveFeedFilter = "latest";', JS)
        self.assertIn('lastRenderedSourceSnapshot !== liveFeedState', JS)


if __name__ == "__main__":
    unittest.main()
