from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class CompanyLayerTests(unittest.TestCase):
    def test_online_school_is_company_not_product(self):
        company = json.loads((ROOT / "companies" / "online-school" / "company.json").read_text(encoding="utf-8"))
        self.assertEqual(company["id"], "COMPANY-001")
        self.assertEqual(company["name"], "Online School")
        self.assertEqual(company["state"], "operating_model")
        self.assertIn("not_claimed", company["legal_status"])

    def test_schedule_preserves_core_operating_cadence(self):
        schedule = json.loads((ROOT / "companies" / "online-school" / "operations" / "schedule_template.json").read_text(encoding="utf-8"))
        shared = {x["activity"]: x["minutes"] for x in schedule["shared_weekday_blocks"]}
        self.assertEqual(shared["mathematics"], 60)
        self.assertEqual(shared["science documentary / guided science study"], 90)
        self.assertEqual(shared["art / creative work"], 60)
        self.assertEqual(schedule["wednesday_blocks"][0]["minutes"], 180)

    def test_public_company_layer_excludes_minor_names(self):
        company_root = ROOT / "companies" / "online-school"
        forbidden = {"Rose", "Myla", "Luna", "Kian"}
        for path in company_root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".json"}:
                continue
            text = path.read_text(encoding="utf-8")
            for name in forbidden:
                self.assertNotIn(name, text, f"{name} leaked into {path.relative_to(ROOT)}")

    def test_company_record_does_not_upgrade_legal_status(self):
        text = (ROOT / "companies" / "online-school" / "COMPANY.md").read_text(encoding="utf-8")
        self.assertIn("not represented here as incorporated, accredited, licensed", text)


if __name__ == "__main__":
    unittest.main()
