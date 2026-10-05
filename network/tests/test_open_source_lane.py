from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class OpenSourceArchitectureTests(unittest.TestCase):
    def test_open_source_protocol_registered(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("opensource.contribution", index["protocols"])

    def test_goal_lanes_remain_explicit_why_metadata(self):
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("## Goal lanes", arch)
        self.assertIn("Research, open source, and paid work answer **why**", arch)
        self.assertIn("`research/`", arch)
        self.assertIn("`open_source/`", arch)
        self.assertIn("`money/` and `jobs/`", arch)

    def test_open_source_registry_is_separate_from_jobs(self):
        reg = json.loads((ROOT / "open_source" / "contributions" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(reg["next_id"], 1)
        self.assertEqual(reg["contributions"], [])
        protocol = (ROOT / "protocols" / "open_source" / "contribution.md").read_text(encoding="utf-8")
        self.assertIn("merged ≠ paid", protocol)


if __name__ == "__main__":
    unittest.main()
