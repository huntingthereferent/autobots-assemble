import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "companies" / "online-school" / "app" / "worksheet_engine.py"
spec = importlib.util.spec_from_file_location("worksheet_engine_test", ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)


class WorksheetEngineTests(unittest.TestCase):
    def test_arithmetic_is_deterministic_and_has_answers(self):
        payload = {
            "template": "arithmetic",
            "operation": "mixed",
            "level": "standard",
            "count": 12,
            "seed": 42,
        }
        a = engine.generate_worksheet(payload)
        b = engine.generate_worksheet(payload)
        self.assertEqual(a["items"], b["items"])
        self.assertEqual(len(a["items"]), 12)
        self.assertTrue(all(item["answer"] for item in a["items"]))

    def test_levels_change_spelling_movement(self):
        common = {"template": "spelling", "words": "because, friend", "seed": 2}
        support = engine.generate_worksheet({**common, "level": "support"})
        standard = engine.generate_worksheet({**common, "level": "standard"})
        challenge = engine.generate_worksheet({**common, "level": "challenge"})
        self.assertIn("Copy the word", support["items"][0]["prompt"])
        self.assertIn("_", standard["items"][0]["prompt"])
        self.assertIn("sentence", challenge["items"][0]["prompt"])

    def test_reading_uses_source_and_builds_rubric_key(self):
        ws = engine.generate_worksheet({
            "template": "reading",
            "level": "challenge",
            "passage": "Evaporation happens when liquid water gains enough energy to become water vapor.",
            "knowledge_goal": "Explain a state change using evidence.",
        })
        self.assertTrue(ws["passage"].startswith("Evaporation"))
        self.assertGreaterEqual(len(ws["items"]), 4)
        self.assertTrue(all(item["answer"] for item in ws["items"]))
        self.assertEqual(ws["knowledge_goal"], "Explain a state change using evidence.")

    def test_vocabulary_requires_definitions_and_keeps_answers(self):
        ws = engine.generate_worksheet({
            "template": "vocabulary",
            "terms": "evaporation: liquid to gas\ncondensation: gas to liquid",
            "level": "standard",
        })
        answers = {item["answer"] for item in ws["items"]}
        self.assertEqual(answers, {"liquid to gas", "gas to liquid"})

    def test_custom_rows_round_trip_into_editable_items(self):
        ws = engine.generate_worksheet({
            "template": "custom",
            "custom_items": "What is 2 + 2? :: 4\nName a mammal :: Teacher review",
            "response_lines": 3,
        })
        self.assertEqual(ws["items"][0]["lines"], 3)
        saved = engine.validate_saved_worksheet(ws)
        self.assertEqual(saved["worksheet_id"], ws["worksheet_id"])
        self.assertEqual(len(saved["items"]), 2)

    def test_empty_required_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "requires"):
            engine.generate_worksheet({"template": "reading", "passage": ""})


if __name__ == "__main__":
    unittest.main()
