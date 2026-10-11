"""Keep A/B language-level Ground Record separate from bounded formal models.

This is a static repository contract check, not proof of mathematical or
physical truth or proof of AI behavior outside the files under inspection.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
NOTE = "AB_Ground_Record_Current_Note_2026-10-11.md"


class ABGroundingTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_ground_record_exists_and_preserves_distinctions(self):
        note = self.read(NOTE)
        for clause in (
            "language for describing, recognizing, and continuing relationships",
            "same referent from the other side",
            "Existing: 1 0 1",
            "A/B:      0 1 0",
            "couplesense",
            "demonstrable **two-step**",
            "not a universal binary complement law",
            "engineering hypothesis remains unverified",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, note)

    def test_entry_protocol_and_contract_reach_grounding(self):
        for path in (
            "README.md",
            "ENTRY.md",
            "AB_CONTRACT.md",
            "COMPLETE_STACK.md",
            "protocols/ai/session.md",
            "work/arc_like_maze/README.md",
            "work/arc_like_maze/TERMINOLOGY.md",
            "work/arc_like_maze/RELATION_PROBE.md",
        ):
            with self.subTest(path=path):
                self.assertIn(NOTE, self.read(path))
        contract = self.read("AB_CONTRACT.md")
        self.assertIn("language for recognizing, describing, and continuing relationships", contract)
        self.assertIn("particular formal mathematical representations", contract)
        self.assertNotIn("A/B is the recursively reusable mathematical operation.", contract)
        self.assertNotIn("A/B remains the recursively reusable mathematical operation", self.read("COMPLETE_STACK.md"))
        self.assertNotIn("A/B remains the mathematical referent", self.read("protocols/ai/session.md"))

    def test_proof_claims_not_promoted_by_language_correction(self):
        note = self.read(NOTE)
        self.assertIn("not a new mathematical proof", note)
        self.assertIn("Not established", note)
        self.assertIn("historical source evidence", note)
        entry = self.read("ENTRY.md")
        self.assertIn("not** a replacement for the user's explicit current question", entry)
        math_scope = self.read("work/arc_like_maze/TERMINOLOGY.md")
        self.assertIn("full-state conjugacy", math_scope)
        self.assertIn("proof", math_scope.lower())


if __name__ == "__main__":
    unittest.main()
