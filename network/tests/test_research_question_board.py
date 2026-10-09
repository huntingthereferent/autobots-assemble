"""Read-only checkpoint board contract, independent of site deployment."""
import json
import tempfile
import unittest
from pathlib import Path

from runtime.research_board import load_research_board


class ResearchQuestionBoardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entry = {
            "schema_version": 1,
            "current": "freeze-one",
            "checkpoints": [
                {"id": "freeze-one", "label": "Freeze one", "file": "freeze-one.json"},
                {"id": "followup", "label": "Follow-up", "file": "followup.json"},
            ],
        }
        self.row = {
            "id": "Q-001",
            "question": "Which relations survive?",
            "status": "REVIEW",
            "answer": "",
            "scope": "",
            "boundary": "Not yet reviewed",
            "witnesses": [],
            "derived_from": [],
            "next_question_ids": [],
            "origin": "https://github.com/example/research/blob/main/README.md",
        }
        self.initial = {
            "schema_version": 1,
            "checkpoint_id": "freeze-one",
            "frozen_date": "2026-10-09",
            "questions": [self.row],
        }
        self.write()

    def write(self):
        (self.root / "index.json").write_text(json.dumps(self.entry), encoding="utf-8")
        (self.root / "freeze-one.json").write_text(json.dumps(self.initial), encoding="utf-8")

    def test_freeze_is_read_only_and_status_not_inferred(self):
        before = (self.root / "freeze-one.json").read_bytes()
        result = load_research_board(root=self.root)
        self.assertTrue(result["available"])
        self.assertEqual(result["counts"]["REVIEW"], 1)
        self.assertEqual(result["counts"]["ANSWERED"], 0)
        self.assertEqual(result["questions"][0]["question"], self.row["question"])
        self.assertEqual(before, (self.root / "freeze-one.json").read_bytes())

    def test_unknown_checkpoint_refuses_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "unknown research checkpoint"):
            load_research_board(checkpoint="../../other", root=self.root)

    def test_registered_file_must_be_local_basename(self):
        self.entry["checkpoints"][0]["file"] = "../secret.json"
        self.write()
        with self.assertRaisesRegex(ValueError, "invalid registered checkpoint filename"):
            load_research_board(root=self.root)

    def test_duplicate_questions_do_not_count_twice(self):
        self.initial["questions"] = [self.row, dict(self.row)]
        self.write()
        with self.assertRaisesRegex(ValueError, "duplicate question ID"):
            load_research_board(root=self.root)

    def test_answered_requires_witness_and_exact_scope(self):
        self.initial["questions"][0]["status"] = "ANSWERED"
        self.initial["questions"][0]["answer"] = "Yes, in a bounded case."
        self.write()
        with self.assertRaisesRegex(ValueError, "require answer, scope, and witnesses"):
            load_research_board(root=self.root)

    def test_partial_unknown_and_next_question_keep_old_freeze(self):
        initial_bytes = (self.root / "freeze-one.json").read_bytes()
        later = json.loads(json.dumps(self.initial))
        later["checkpoint_id"] = "followup"
        later["questions"] = [
            {
                **self.row,
                "status": "PARTIAL",
                "answer": "Established in a declared finite family.",
                "scope": "Named 81-state B-invariant fiber only",
                "boundary": "General case remains open.",
                "next_question_ids": ["Q-002"],
                "witnesses": [
                    {"label":"Research case",
                     "url":"https://github.com/example/research/blob/main/CASE.md"}
                ],
            },
            {
                **self.row, "id":"Q-002",
                "question":"Which wider transformations still preserve the relation?",
                "status":"OPEN", "derived_from":["Q-001"],
                "next_question_ids":[],
            },
        ]
        (self.root / "followup.json").write_text(json.dumps(later),encoding="utf-8")
        self.entry["current"] = "followup"
        self.write()
        updated = load_research_board(root=self.root)
        self.assertEqual(updated["counts"]["PARTIAL"], 1)
        self.assertEqual(updated["counts"]["OPEN"], 1)
        old = load_research_board(checkpoint="freeze-one",root=self.root)
        self.assertEqual(old["counts"]["REVIEW"], 1)
        self.assertEqual(initial_bytes, (self.root / "freeze-one.json").read_bytes())

    def test_unavailable_is_explicit(self):
        (self.root / "index.json").unlink()
        result = load_research_board(root=self.root)
        self.assertFalse(result["available"])
        self.assertEqual(result["questions"], [])

    def test_real_frozen_snapshot(self):
        result = load_research_board()
        self.assertTrue(result["available"])
        self.assertEqual(result["counts"]["REVIEW"], 6)
        self.assertEqual(result["counts"]["ANSWERED"], 0)
        self.assertEqual(len(result["checkpoints"]), 1)


if __name__ == "__main__":
    unittest.main()
