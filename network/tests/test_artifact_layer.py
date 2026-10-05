from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ArtifactLayerTests(unittest.TestCase):
    def test_artifact_layer_is_distinct_from_views(self):
        text = (ROOT / "artifacts" / "README.md").read_text(encoding="utf-8")
        self.assertIn("working representations", text)
        self.assertIn("They are not read-only views", text)
        self.assertIn("program", text)
        self.assertIn("CAD-like geometry", text)
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

    def test_machine_readable_schema_has_sibling_representation_types(self):
        schema = json.loads((ROOT / "artifacts" / "artifact.schema.json").read_text(encoding="utf-8"))
        values = set(schema["properties"]["representation_type"]["enum"])
        self.assertTrue({"program", "cad_like", "system_landscape", "math_model"}.issubset(values))
        self.assertIn("witness_depth", schema["required"])
        self.assertIn("provenance", schema["required"])


if __name__ == "__main__":
    unittest.main()
