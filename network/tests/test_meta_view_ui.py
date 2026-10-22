"""Meta viewer is a single combined instrument; placement stays in the pipeline."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
VIEW = ROOT / "docs/live/meta.html"


class MetaControlDeckTests(unittest.TestCase):
    def test_aggregate_view_hides_node_allocation(self):
        page = VIEW.read_text(encoding="utf-8")
        self.assertIn("<h1>Research workstation</h1>", page)
        self.assertIn('id="running"', page)
        self.assertIn('id="queued"', page)
        self.assertIn('id="chart"', page)
        self.assertIn('id="runs"', page)
        self.assertIn('id="source-boundaries"', page)
        self.assertIn('aria-label="Combined observed workflow-run counts"', page)
        self.assertNotIn('class="nodes"', page)
        self.assertNotIn('class="node b"', page)
        self.assertNotIn("Dessy", page)
        self.assertNotIn("DESSY", page)

    def test_observations_stay_source_owned(self):
        page = VIEW.read_text(encoding="utf-8")
        self.assertIn("/actions/runs", page)
        self.assertIn("meta-observations/history.json", page)
        self.assertIn("meta-observations/routing.json", page)
        self.assertIn("Promise.allSettled", page)
        self.assertIn("Missing source", page if "Missing source" in page else
                      "missing work is unknown")
        self.assertIn("sample", page.lower())

    @unittest.skipUnless(shutil.which("node"), "Requires Node.js")
    def test_inline_script_has_valid_javascript(self):
        page = VIEW.read_text(encoding="utf-8")
        scripts = re.findall(r"<script>(.*?)</script>", page, re.S)
        self.assertEqual(len(scripts), 1)
        subprocess.run(["node", "--check", "-"], input=scripts[0],
                       text=True, check=True, capture_output=True, timeout=15)


if __name__ == "__main__":
    unittest.main()
