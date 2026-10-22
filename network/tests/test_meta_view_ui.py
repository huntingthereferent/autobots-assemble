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
        self.assertIn('id="trend"', page)
        self.assertIn('id="runs"', page)
        self.assertIn('<details class="more" id="source-details">', page)
        self.assertIn('aria-label="Combined source-observed workflow counts"', page)
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
        self.assertTrue("unknown work is not zero" in page or "missing work is unknown" in page)
        self.assertIn("sample", page.lower())

    def test_professional_layout_links_real_work_and_retains_semantics(self):
        page = VIEW.read_text(encoding="utf-8")
        self.assertIn('id="beads-queue"', page)
        self.assertIn('id="beads-running"', page)
        self.assertIn('id="beads-done"', page)
        self.assertIn('id="show-more"', page)
        self.assertIn('id="list-range"', page)
        self.assertIn('class="panel journal"', page)
        self.assertIn('id="routing-note"', page)
        self.assertIn('id="status-note"', page)
        self.assertIn('get(root+"?per_page=100")', page)
        self.assertIn('a.href=r.url', page)
        self.assertIn('a.setAttribute("aria-label"', page)
        self.assertIn('showLimit+=25', page)
        self.assertIn('meta-observations/history.json', page)
        self.assertNotIn('class="work-layout"', page)
        self.assertNotIn('DESSY', page)

    @unittest.skipUnless(shutil.which("node"), "Requires Node.js")
    def test_inline_script_has_valid_javascript(self):
        page = VIEW.read_text(encoding="utf-8")
        scripts = re.findall(r"<script>(.*?)</script>", page, re.S)
        self.assertEqual(len(scripts), 1)
        subprocess.run(["node", "--check", "-"], input=scripts[0],
                       text=True, check=True, capture_output=True, timeout=15)


    def test_observer_uses_current_registry_repositories(self):
        from tempfile import TemporaryDirectory
        import json
        from systems.workspace.meta_collect import repositories
        with TemporaryDirectory() as folder:
            path = Path(folder) / "meta-registry.json"
            path.write_text(json.dumps({
                "schema": "meta-workstation/registry-v1",
                "nodes": [
                    {"id": "A", "repo": "huntingthereferent/autobots-assemble"},
                    {"id": "B", "repo": "aeren-research/new-workstation-name"}
                ]
            }))
            self.assertEqual(repositories(path)["B"], "aeren-research/new-workstation-name")


if __name__ == "__main__":
    unittest.main()
