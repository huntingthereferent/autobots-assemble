from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class CategoryContractTests(unittest.TestCase):
    def test_every_registered_layer_has_one_explicit_axis(self):
        data = json.loads((ROOT / "category_axes.json").read_text(encoding="utf-8"))
        expected = {"current_problem", "capability", "dependency", "artifact", "witness", "goal_lane", "view"}
        self.assertEqual(set(data["layers"]), expected)
        for name, layer in data["layers"].items():
            self.assertTrue(layer.get("axis"), name)
            self.assertTrue(layer.get("question"), name)

    def test_artifact_type_and_witness_depth_are_separate_axes(self):
        axes = json.loads((ROOT / "category_axes.json").read_text(encoding="utf-8"))["layers"]
        self.assertEqual(axes["artifact"]["axis"], "preserved_relation")
        self.assertEqual(axes["witness"]["axis"], "evidence_depth")

        categories = json.loads((ROOT / "artifacts" / "categories.json").read_text(encoding="utf-8"))
        category_text = json.dumps(categories)
        for witness in axes["witness"]["ordered_values"]:
            self.assertNotIn(f'"{witness}"', category_text)

    def test_contract_forbids_mixed_sibling_axes(self):
        text = (ROOT / "CATEGORY_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("siblings must answer the same question", text)
        self.assertIn("One axis per sibling set", text)
        self.assertIn("Status is not type", text)
        self.assertIn("A child remains decomposable", text)


if __name__ == "__main__":
    unittest.main()
