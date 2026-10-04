from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
GEMS = ROOT / "money" / "challenges" / "GEMS-001_hidden-fault-mapping"

class GemsRulesSwallowTests(unittest.TestCase):
    def test_rules_are_evidence_not_new_protocol(self):
        text=(GEMS/"OFFICIAL_RULES_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("does **not** define a new protocol", text)
        self.assertIn("absorbed into the challenge record", text)

    def test_rules_evidence_is_partial(self):
        rec=json.loads((GEMS/"challenge.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["rules_evidence"]["state"], "PARTIAL")
        self.assertEqual(rec["rules_evidence"]["publication_number"], "NLR/OT-6A50-96647")

    def test_captain_not_upgraded_to_professional_credential(self):
        text=(GEMS/"GEMS.md").read_text(encoding="utf-8")
        self.assertIn("Nothing in the public eligibility summary adds a professional, academic, or licensing credential", text)

if __name__=="__main__":
    unittest.main()
