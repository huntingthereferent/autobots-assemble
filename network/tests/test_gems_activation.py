from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
GEMS = ROOT / "money" / "challenges" / "GEMS-001_hidden-fault-mapping"


class GemsActivationTests(unittest.TestCase):
    def test_active_referent(self):
        state = json.loads((ROOT / "state" / "current.json").read_text(encoding="utf-8"))
        self.assertIn("GEMS-001", state["preferred_referent"])

    def test_record_tracks_received_data_and_remaining_compliance_wall(self):
        rec = json.loads((GEMS / "challenge.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["data_evidence"]["state"], "RECEIVED_IN_SESSION")
        self.assertTrue(any("third-party" in w.lower() for w in rec["walls"]))

    def test_unmapped_is_not_negative(self):
        text = (GEMS / "BASELINE_DISSECTION.md").read_text(encoding="utf-8")
        self.assertIn("not mapped", text)
        self.assertIn("negative", text)

    def test_metric_contract_is_present(self):
        text = (GEMS / "metric.py").read_text(encoding="utf-8")
        self.assertIn("distance_weighted_tversky", text)
        self.assertIn("alpha: float = 0.2", text)
        self.assertIn("beta: float = 0.8", text)
        self.assertIn("radius_pixels: float = 3.0", text)


if __name__ == "__main__":
    unittest.main()
