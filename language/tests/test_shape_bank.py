from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from language.english.bank import candidates, load_bank, render


class EnglishShapeBankTests(unittest.TestCase):
    def test_ids_unique_and_all_registers_present(self):
        bank = load_bank()
        ids = [item["id"] for item in bank["shapes"]]
        self.assertEqual(len(ids), len(set(ids)))
        registers = {"standard","plain","casual","slang","internet","caveman","technical"}
        for item in bank["shapes"]:
            self.assertEqual(set(item["surfaces"]), registers)
            self.assertTrue(all(item["surfaces"][r] for r in registers))

    def test_send_it_remains_ambiguous(self):
        ids = {m["shape"] for m in candidates("send it")}
        self.assertIn("MOVE.CONTINUE", ids)
        self.assertIn("WORK.SUBMIT", ids)

    def test_internet_and_caveman_render_same_shape(self):
        self.assertEqual(render("MOVE.CONTINUE", "internet"), "continue")
        self.assertEqual(render("MOVE.CONTINUE", "caveman"), "keep go")

    def test_dissect_is_break_apart_and_connect(self):
        item = next(x for x in load_bank()["shapes"] if x["id"] == "ANALYZE.DISSECT")
        self.assertEqual(item["canonical"], "dissect")
        self.assertIn("decompose", item["movement_sequence"])
        self.assertIn("connect_supported_relations", item["movement_sequence"])
        ids = {m["shape"] for m in candidates("dissect this")}
        self.assertIn("ANALYZE.DISSECT", ids)


if __name__ == "__main__":
    unittest.main()
