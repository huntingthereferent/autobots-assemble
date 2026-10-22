"""Research source browser is read-only, source-loaded and properly linked."""
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]
VIEW = ROOT / "docs" / "live" / "research-sources.html"
WORK = ROOT / "docs" / "live" / "work.html"


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._in = True
            self.scripts.append("")

    def handle_data(self, text):
        if self._in:
            self.scripts[-1] += text

    def handle_endtag(self, tag):
        if tag == "script":
            self._in = False


class ResearchSourceUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = VIEW.read_text(encoding="utf-8")
        cls.work = WORK.read_text(encoding="utf-8")

    def test_workstation_has_direct_source_navigation(self):
        self.assertIn('href="research-sources.html">SOURCES</a>', self.work)

    def test_catalog_uses_original_source_not_invented_counts(self):
        self.assertIn("api.github.com/repos/huntingthereferent/autobots-assemble/contents/research/testing_lanes/registry.json?ref=main", self.page)
        self.assertIn('id="source-count">—</strong>', self.page)
        self.assertIn('id="lane-count">—</strong>', self.page)
        self.assertIn('id="source-state"', self.page)
        self.assertIn("SOURCE NOT AVAILABLE · NO COUNTS INFERRED", self.page)

    def test_lane_selection_only_filters_source_dependencies(self):
        self.assertIn("lane.source_ids", self.page)
        self.assertIn("Select a lane to inspect dependencies", self.page)
        self.assertIn("candidate tests, not running scientific experiments", self.page)

    def test_provider_docs_and_provenance_are_linked(self):
        self.assertIn("Provider documentation ↗", self.page)
        self.assertIn("Source contract ↗", self.page)
        self.assertIn("science", self.page.lower())
        self.assertIn("body_sha256", (ROOT / "research/testing_lanes/source_admission.py").read_text(encoding="utf-8"))

    def test_no_fake_scientific_passes_or_automatic_remote_execution(self):
        self.assertNotIn("setInterval(", self.page)
        self.assertNotIn("eval(", self.page)
        self.assertNotIn("innerHTML =", self.page)
        self.assertNotIn('>100%<', self.page)
        self.assertIn("scientific", self.page.lower())

    def test_script_is_inline_and_nonempty(self):
        parser = ScriptParser()
        parser.feed(self.page)
        self.assertEqual(len(parser.scripts), 1)
        self.assertIn("async function load()", parser.scripts[0])


if __name__ == "__main__":
    unittest.main()
