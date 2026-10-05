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

    def test_selected_next_project_targets_an_unclosed_gap(self):
        ability_map = json.loads(
            (ROOT / "foundation" / "ABILITY_MAP.json").read_text(encoding="utf-8")
        )
        selection = ability_map["next_project_selection"]["selected_gap"]
        selected = next(
            ability for ability in ability_map["abilities"]
            if ability["ability"] == selection
        )
        self.assertIn(selected["state"], {"unwitnessed", "partial"})


if __name__ == "__main__":
    unittest.main()
