from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]

class AllWorkScanTests(unittest.TestCase):
    def test_protocol_registered(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("work.all-work-scan", index["protocols"])

    def test_frontier_work_is_in_scope(self):
        text = (ROOT / "protocols" / "work" / "all-work-scan.md").read_text(encoding="utf-8")
        self.assertIn("Frontier academic work", text)
        self.assertIn("Self-initiated work", text)
        self.assertIn("no task owner", text)

    def test_repeat_results_are_not_suppressed(self):
        text = (ROOT / "protocols" / "work" / "all-work-scan.md").read_text(encoding="utf-8")
        self.assertIn("Do not suppress a candidate merely because it appeared in a prior scan", text)

    def test_credentials_are_separated_from_other_walls(self):
        text = (ROOT / "protocols" / "work" / "all-work-scan.md").read_text(encoding="utf-8")
        self.assertIn("age minimum", text)
        self.assertIn("citizenship/residency", text)
        self.assertIn("equipment/tool access", text)

if __name__ == "__main__":
    unittest.main()
