"""Research frontage interactions preserve native witnessed sources and visible expansion."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "runtime/http/index.html").read_text(encoding="utf-8")
JS = (ROOT / "runtime/http/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "runtime/http/styles.css").read_text(encoding="utf-8")


class ResearchFrontpageInteractionTests(unittest.TestCase):
    def test_moving_ticker_has_separate_expansion_not_clipped_by_strip(self):
        self.assertIn('id="feed-tickers"', HTML)
        self.assertIn('id="ticker-expanded"', HTML)
        self.assertLess(HTML.index('id="feed-tickers"'), HTML.index('id="ticker-expanded"'))
        self.assertIn('const expanded = $("#ticker-expanded");', JS)
        self.assertIn('expanded.replaceChildren(heading, card)', JS)
        self.assertIn('expanded.hidden = !selected', JS)
        self.assertIn('animation: continuity-ticker-shift', CSS)

    def test_ticker_motion_pauses_and_respects_reduced_motion(self):
        self.assertIn('.feed-tickers:is(:hover,:focus-within,.has-selection)', CSS)
        self.assertIn('@media (prefers-reduced-motion:reduce)', CSS)
        self.assertIn('animation:none !important;', CSS)
        self.assertIn('button.setAttribute("aria-expanded"', JS)

    def test_native_external_feed_is_expandable_with_real_provider_links(self):
        self.assertIn('const el = document.createElement("details");', JS)
        self.assertIn('const head = document.createElement("summary");', JS)
        self.assertIn('item.source_id === source.id', JS)
        self.assertIn('safeExternalSourceUrl(item.url)', JS)
        self.assertIn('safeExternalSourceUrl(pair[0])', JS)
        self.assertIn('"Native feed ↗"', JS)
        self.assertIn('link.rel = "noopener noreferrer"', JS)

    def test_mobile_exposes_source_index_and_can_filter_main_feed(self):
        self.assertIn('id="mobile-live-sources"', HTML)
        self.assertIn('class="mobile-source-chooser"', HTML)
        self.assertIn('[$("#live-sources"), $("#mobile-live-sources")]', JS)
        self.assertIn('sourceOnlyId = source.id', JS)
        self.assertIn('id="clear-source-filter"', HTML)
        self.assertIn('sourceOnlyId = ""', JS)
        self.assertIn('body.research-edition .mobile-source-chooser', CSS)


if __name__ == "__main__":
    unittest.main()
