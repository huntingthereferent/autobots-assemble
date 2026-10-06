from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[3]
PROVENANCE = ROOT / "design" / "visual-provenance"


class VisualProvenanceTests(unittest.TestCase):
    def test_registry_templates_exist_and_match_ids(self):
        registry = json.loads((PROVENANCE / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["schema_version"], 1)
        self.assertTrue(registry["templates"])

        for item in registry["templates"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            template = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(template["template_id"], item["template_id"])
            self.assertEqual(template["status"], item["status"])
            self.assertTrue(template["witnesses"])
            self.assertTrue(template["grammar"])
            self.assertTrue(template["avoid"])
            self.assertTrue(template["adaptation_rules"])

    def test_note_gpt_template_keeps_source_as_witness_not_copy_contract(self):
        template = json.loads(
            (PROVENANCE / "templates" / "notegpt_math_generator_v1.json").read_text(
                encoding="utf-8"
            )
        )
        witness = template["witnesses"][0]
        self.assertEqual(witness["source"], "https://notegpt.io/ai-math-worksheet")
        combined = " ".join(template["adaptation_rules"]).lower()
        self.assertIn("do not imitate", combined)
        self.assertIn("branding", combined)

    def test_online_school_surface_binding_resolves_to_registered_template(self):
        binding_path = ROOT / "companies" / "online-school" / "app" / "visual-provenance.json"
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
        registry = json.loads((PROVENANCE / "registry.json").read_text(encoding="utf-8"))
        ids = {item["template_id"] for item in registry["templates"]}

        self.assertIn(binding["template_id"], ids)
        surface = ROOT / binding["surface_path"]
        self.assertTrue(surface.is_file())

        html = surface.read_text(encoding="utf-8")
        self.assertIn(
            f'<meta name="visual-template" content="{binding["template_id"]}">',
            html,
        )

    def test_surface_binding_preserves_local_domain_instead_of_flattening_it(self):
        binding = json.loads(
            (
                ROOT
                / "companies"
                / "online-school"
                / "app"
                / "visual-provenance.json"
            ).read_text(encoding="utf-8")
        )
        additions = " ".join(binding["local_additions"]).lower()
        self.assertIn("knowledge goal", additions)
        self.assertIn("curriculum", additions)
        self.assertIn("homework", additions)

    def test_education_workspace_has_its_own_visual_binding(self):
        binding = json.loads(
            (
                ROOT
                / "companies"
                / "online-school"
                / "app"
                / "visual-provenance"
                / "education-workspace.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(binding["template_id"], "education_workspace_v1")
        surface = ROOT / binding["surface_path"]
        html = surface.read_text(encoding="utf-8")
        self.assertIn(
            '<meta name="visual-template" content="education_workspace_v1">',
            html,
        )
        worksheet_binding = json.loads(
            (
                ROOT
                / "companies"
                / "online-school"
                / "app"
                / "visual-provenance.json"
            ).read_text(encoding="utf-8")
        )
        self.assertNotEqual(binding["template_id"], worksheet_binding["template_id"])

    def test_day_attention_surface_has_its_own_visual_binding(self):
        binding = json.loads(
            (ROOT / "runtime" / "http" / "visual-provenance.json").read_text(
                encoding="utf-8"
            )
        )
        registry = json.loads((PROVENANCE / "registry.json").read_text(encoding="utf-8"))
        ids = {item["template_id"] for item in registry["templates"]}
        self.assertIn(binding["template_id"], ids)

        surface = ROOT / binding["surface_path"]
        self.assertTrue(surface.is_file())
        html = surface.read_text(encoding="utf-8")
        self.assertIn(
            f'<meta name="visual-template" content="{binding["template_id"]}">',
            html,
        )
        preserve = " ".join(binding["preserve"]).lower()
        self.assertIn("three distinct attention streams", preserve)

    def test_schema_contracts_exist(self):
        for name in ("visual-template.schema.json", "surface-binding.schema.json"):
            schema = json.loads((PROVENANCE / "schema" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(schema["type"], "object")
            self.assertTrue(schema["required"])


if __name__ == "__main__":
    unittest.main()
