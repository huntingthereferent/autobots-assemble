"""Guard shared 13-provider/21-lane CI against accidental per-study fanout."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "research-source-admission.yml"

SHARED_PATHS = {
    "research/testing_lanes/registry.json",
    "research/testing_lanes/sources/**",
    "research/testing_lanes/source_admission.py",
    "research/testing_lanes/lane_activation.py",
    "research/testing_lanes/lane_registry.py",
    ".github/workflows/research-source-admission.yml",
}


class ResearchSourceCIScopeTests(unittest.TestCase):
    def test_expensive_live_source_matrix_has_exact_core_path_triggers(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        pr = text.split("  pull_request:", 1)[1].split("  workflow_dispatch:", 1)[0]
        paths = set(re.findall(r'^\s+-\s+"([^"]+)"\s*$', pr, flags=re.MULTILINE))
        self.assertEqual(paths, SHARED_PATHS)

    def test_all_child_source_and_study_scripts_are_excluded(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        pr = text.split("  pull_request:", 1)[1].split("  workflow_dispatch:", 1)[0]
        self.assertNotIn("research/testing_lanes/*.py", pr)
        self.assertNotIn("research/testing_lanes/**", pr)
        self.assertNotIn("research/testing_lanes/observations/**", pr)
        self.assertNotIn("research/testing_lanes/neuro_public/**", pr)
        self.assertNotIn("research/testing_lanes/ml_iris_v1.py", pr)


if __name__ == "__main__":
    unittest.main()
