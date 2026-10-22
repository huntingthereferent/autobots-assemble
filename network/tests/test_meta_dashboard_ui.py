"""Meta viewer exposes a single source-backed workload; node placement belongs to routing."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "docs" / "live" / "meta.html"
REGISTRY = ROOT / "docs" / "live" / "meta-registry.json"


class MetaDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = META.read_text(encoding="utf-8")

    def test_one_viewer_not_node_inventory(self):
        page = self.page
        self.assertIn("Research workstation</h1>", page)
        self.assertIn('id="trend"', page)
        self.assertIn('id="runs"', page)
        self.assertIn('id="queued"', page)
        self.assertIn('id="running"', page)
        self.assertNotIn('class="nodes"', page)
        self.assertNotIn('id="lane-rows"', page)
        self.assertNotIn("AEREN", page)
        self.assertNotIn("Dessy", page)
        self.assertNotIn("DESSY", page)

    def test_visual_parity_with_work_without_fabricating_source_counts(self):
        page=self.page
        style=(ROOT / "docs/live/meta-work-parity.css").read_text(encoding="utf-8")
        self.assertIn('href="meta-work-parity.css"',page)
        self.assertIn('class="hero overview"',page)
        self.assertIn('GITHUB OBSERVATION / COMBINED',page)
        self.assertIn('href="work.html#executions"',page)
        self.assertIn('class="metric-top"',page)
        self.assertIn('class="flow-level"',page)
        self.assertIn('function updateMetric(id,value,available=true)',page)
        self.assertIn('12 visual markers maximum',page)
        self.assertIn('.metrics .metric.followup',style)
        self.assertIn('prefers-reduced-motion:reduce',style)

    def test_real_source_counts_not_demo_animation(self):
        page = self.page
        self.assertIn('ROOT="https://api.github.com/repos/"', page)
        self.assertIn('status="+s+"&per_page=1"', page)
        self.assertIn("workflow_runs", page)
        self.assertIn("ab-meta-observations/v1", page)
        self.assertIn("a?.observed", page)
        self.assertIn("No paired observations", page)
        self.assertIn("unknown work is not zero", page)
        self.assertNotIn("Math.random", page)
        self.assertNotIn("canvas", page)

    def test_readable_mobile_layout_and_recorded_pipeline_link(self):
        page = self.page
        self.assertIn("@media(max-width:660px)", page)
        self.assertIn("<details class=\"more\">", page)
        self.assertIn("meta-registry.json", page)
        self.assertIn("meta-observations/routing.json", page)
        self.assertIn("a.href=r.url", page)
        self.assertIn("1200000", page)
        self.assertIn("source-linked", page.lower())


if __name__ == "__main__":
    unittest.main()
