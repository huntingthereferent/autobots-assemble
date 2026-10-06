import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"
sys.path.insert(0, str(APP))
ENGINE_PATH = APP / "worksheet_engine.py"
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

    def test_notegpt_published_example_addition_subtraction_within_20_first_grade(self):
        ws = engine.generate_worksheet({
            "template": "arithmetic",
            "math_prompt": "Addition and subtraction within 20 for 1st grade",
            "grade": "auto",
            "math_topic": "auto",
            "question_type": "mixed",
            "count": 10,
            "seed": 9,
        })
        spec = ws["source"]["resolved_math_spec"]
        self.assertEqual(spec["grade"], 1)
        self.assertEqual(spec["within"], 20)
        self.assertEqual(len(ws["items"]), 10)
        for item in ws["items"]:
            nums = [int(x) for x in __import__("re").findall(r"\d+", item["prompt"])]
            self.assertTrue(all(n <= 20 for n in nums[:2]))
            self.assertIn("Why:", item["answer"])

    def test_math_breadth_exceeds_basic_arithmetic(self):
        cases = [
            ("Fractions for 4th grade", "fractions"),
            ("Geometry area and perimeter for 5th grade", "geometry"),
            ("Money word practice for 2nd grade", "money"),
            ("One-step algebra equations for 6th grade", "algebra"),
            ("Decimal practice for 5th grade", "decimals"),
            ("Word problems for 3rd grade", "word-problems"),
        ]
        for prompt, topic in cases:
            ws = engine.generate_worksheet({
                "template": "arithmetic",
                "math_prompt": prompt,
                "math_topic": "auto",
                "grade": "auto",
                "question_type": "short-answer",
                "count": 5,
                "seed": 4,
            })
            self.assertEqual(ws["source"]["resolved_math_spec"]["topic"], topic)
            self.assertEqual(len(ws["items"]), 5)
            self.assertTrue(all("Why:" in item["answer"] for item in ws["items"]))

    def test_math_question_types_are_real_not_labels(self):
        single = engine.generate_worksheet({
            "template": "arithmetic",
            "math_prompt": "fractions for 4th grade",
            "question_type": "single-choice",
            "count": 4,
            "seed": 3,
        })
        self.assertTrue(all("A." in item["prompt"] for item in single["items"]))
        fill = engine.generate_worksheet({
            "template": "arithmetic",
            "math_prompt": "addition within 20 for 1st grade",
            "question_type": "fill-blank",
            "count": 4,
            "seed": 3,
        })
        self.assertTrue(all("____" in item["prompt"] for item in fill["items"]))


if __name__ == "__main__":
    unittest.main()
