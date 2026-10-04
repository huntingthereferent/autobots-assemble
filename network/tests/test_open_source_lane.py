from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class OpenSourceArchitectureTests(unittest.TestCase):
    def test_open_source_protocol_registered(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("opensource.contribution", index["protocols"])

    def test_three_lanes_are_explicit(self):
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("THEORY / RESEARCH", arch)
        self.assertIn("OPEN SOURCE", arch)
        self.assertIn("MONEY / JOBS", arch)

    def test_open_source_registry_is_separate_from_jobs(self):
        reg = json.loads((ROOT / "open_source" / "contributions" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(reg["next_id"], 1)
        self.assertEqual(reg["contributions"], [])
        protocol = (ROOT / "protocols" / "open_source" / "contribution.md").read_text(encoding="utf-8")
        self.assertIn("merged ≠ paid", protocol)


if __name__ == "__main__":
    unittest.main()
