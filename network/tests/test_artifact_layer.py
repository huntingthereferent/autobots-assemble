from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


def collect_leaves(node):
    leaves = []
    children = node.get("children", {})
    if children:
        if not node.get("axis"):
            raise AssertionError("every sibling set must declare one axis")
        for child in children.values():
            leaves.extend(collect_leaves(child))
    if "leaf" in node:
        leaves.append(node["leaf"])
    return leaves


class ArtifactLayerTests(unittest.TestCase):
    def test_artifact_layer_is_distinct_from_views(self):
        text = (ROOT / "artifacts" / "README.md").read_text(encoding="utf-8")
        self.assertIn("working representations", text)
        self.assertIn("They are not read-only views", text)
        self.assertIn("program", text)
        self.assertIn("CAD-like", text)
        self.assertIn("system landscape", text)
        self.assertIn("math model", text)

    def test_cad_like_does_not_upgrade_to_physical_build(self):
        text = (ROOT / "artifacts" / "CAD_LIKE.md").read_text(encoding="utf-8")
        self.assertIn("decorative concept image is **not** CAD-like evidence", text)
        self.assertIn("fabricated: no", text)

    def test_landscape_requires_meaningful_relations(self):
        text = (ROOT / "artifacts" / "SYSTEM_LANDSCAPE.md").read_text(encoding="utf-8")
        self.assertIn("Every edge should mean something", text)
        self.assertIn("Prefer labeled relations", text)

    def test_math_model_preserves_input_lineage(self):
        text = (ROOT / "artifacts" / "MATH_MODEL.md").read_text(encoding="utf-8")
        self.assertIn("source of each input", text)
        self.assertIn("downstream consumers", text)
        self.assertIn("becomes stale and must be recomputed", text)

    def test_artifact_categories_are_recursive_single_axis_paths(self):
        categories = json.loads((ROOT / "artifacts" / "categories.json").read_text(encoding="utf-8"))
        self.assertEqual(categories["root"], "artifact")
        self.assertEqual(categories["axis"], "preserved_relation")
        leaves = collect_leaves(categories)
        self.assertEqual(len(leaves), len(set(leaves)))

        schema = json.loads((ROOT / "artifacts" / "artifact.schema.json").read_text(encoding="utf-8"))
        representation_types = set(schema["properties"]["representation_type"]["enum"])
        self.assertEqual(set(leaves), representation_types)
        self.assertNotIn("other", representation_types)

    def test_artifact_schema_requires_relational_category_path(self):
        schema = json.loads((ROOT / "artifacts" / "artifact.schema.json").read_text(encoding="utf-8"))
        self.assertIn("category_path", schema["required"])
        item = schema["properties"]["category_path"]["items"]
        self.assertEqual(set(item["required"]), {"axis", "value", "relation"})
        self.assertIn("witness_depth", schema["required"])
        self.assertIn("provenance", schema["required"])


if __name__ == "__main__":
    unittest.main()
