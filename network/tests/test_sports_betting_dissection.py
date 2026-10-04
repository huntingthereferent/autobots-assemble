from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class SportsBettingDissectionTests(unittest.TestCase):
    def test_domain_protocol_is_registered(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        self.assertIn("domain.sports-betting.decision", index["protocols"])

    def test_dissection_preserves_missing_uncertainty_as_nonzero_assumption(self):
        text = (ROOT / "domains" / "sports_betting" / "DISSECTION.md").read_text(encoding="utf-8")
        self.assertIn("Missing uncertainty is **not** evidence of zero uncertainty", text)
        protocol = (ROOT / "protocols" / "domain" / "sports-betting-decision.md").read_text(encoding="utf-8")
        self.assertIn("uncertainty missing", protocol)
        self.assertIn("Risk parameters are explicit, not silently defaulted", protocol)

    def test_lens_and_movement_are_separated(self):
        protocol = (ROOT / "protocols" / "domain" / "sports-betting-decision.md").read_text(encoding="utf-8")
        self.assertIn("assessment, not network mutation", protocol)
        self.assertIn("Rendering must not record or place the decision", protocol)


if __name__ == "__main__":
    unittest.main()
