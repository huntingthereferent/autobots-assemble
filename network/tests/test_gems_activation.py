from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]

class GemsActivationTests(unittest.TestCase):
    def test_active_referent(self):
        state=json.loads((ROOT/"state/current.json").read_text(encoding="utf-8"))
        self.assertIn("GEMS-001", state["preferred_referent"])

    def test_record_has_data_wall(self):
        rec=json.loads((ROOT/"money/challenges/GEMS-001_hidden-fault-mapping/challenge.json").read_text(encoding="utf-8"))
        self.assertTrue(any("data page" in w.lower() for w in rec["walls"]))

    def test_unmapped_is_not_negative(self):
        text=(ROOT/"money/challenges/GEMS-001_hidden-fault-mapping/BASELINE_DISSECTION.md").read_text(encoding="utf-8")
        self.assertIn("not mapped", text)
        self.assertIn("negative", text)

if __name__=="__main__":
    unittest.main()
