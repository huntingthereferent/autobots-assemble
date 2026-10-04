from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
GEMS = ROOT / "money" / "challenges" / "GEMS-001_hidden-fault-mapping"


class GemsDownloadedContractTests(unittest.TestCase):
    def test_manifest_tracks_three_supplied_files(self):
        data=json.loads((GEMS/"data_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["files"]), 3)
        self.assertEqual(data["grid"]["width"], 3292)
        self.assertEqual(data["grid"]["height"], 3730)

    def test_output_contract_uses_exact_template_footprint(self):
        c=json.loads((GEMS/"output"/"contract.json").read_text(encoding="utf-8"))
        self.assertEqual(c["hard_requirements"]["dtype"], "float32")
        self.assertIn("exactly match", c["hard_requirements"]["footprint"])

    def test_example_is_not_treated_as_prediction_truth(self):
        text=(GEMS/"DATASET_INSPECTION.md").read_text(encoding="utf-8")
        self.assertIn("format/example scaffold", text)
        self.assertIn("exactly equal", text)


if __name__=="__main__":
    unittest.main()
