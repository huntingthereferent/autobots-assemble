from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AbilityMapTests(unittest.TestCase):
    def test_ability_evidence_paths_exist(self):
        ability_map = json.loads(
            (ROOT / "foundation" / "ABILITY_MAP.json").read_text(encoding="utf-8")
        )

        for ability in ability_map["abilities"]:
            for evidence in ability.get("evidence", []):
                self.assertTrue((ROOT / evidence).exists(), f"{ability['ability']}: {evidence}")

    def test_unwitnessed_categories_have_no_evidence(self):
        ability_map = json.loads(
            (ROOT / "foundation" / "ABILITY_MAP.json").read_text(encoding="utf-8")
        )

        for ability in ability_map["abilities"]:
            if ability["state"] == "unwitnessed":
                self.assertEqual(ability.get("evidence", []), [])

    def test_ability_map_does_not_select_development(self):
        ability_map = json.loads(
            (ROOT / "foundation" / "ABILITY_MAP.json").read_text(encoding="utf-8")
        )

        self.assertNotIn("next_project_selection", ability_map)
        self.assertIn("Read-only projection", ability_map["purpose"])


if __name__ == "__main__":
    unittest.main()
