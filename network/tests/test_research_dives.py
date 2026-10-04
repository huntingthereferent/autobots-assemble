from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ResearchDiveArchitectureTests(unittest.TestCase):
    def test_research_dive_protocol_registered(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("research.dive", index["protocols"])

    def test_dive_registry_starts_valid_and_separate_from_jobs(self):
        dive_index = json.loads((ROOT / "research" / "dives" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(dive_index["next_id"], 1)
        self.assertEqual(dive_index["dives"], [])
        arch = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertIn("THEORY / RESEARCH", arch)
        self.assertIn("MONEY / JOBS", arch)
        self.assertIn("explicit handoff", arch)

    def test_dive_protocol_does_not_force_monetization(self):
        text = (ROOT / "protocols" / "research" / "dive.md").read_text(encoding="utf-8")
        self.assertIn("Do not optimize the dive for monetization", text)
        self.assertIn("saving does **not** mean the dive is finished".lower(), text.lower())


if __name__ == "__main__":
    unittest.main()
