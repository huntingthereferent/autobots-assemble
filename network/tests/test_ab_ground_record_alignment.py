"""Keep the historical ground distinct from bounded mathematics and canonical naming.

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
            "not a definition of A/B, a universal binary complement law",
            "engineering hypothesis remains unverified",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, note)

    def test_entry_protocol_and_contract_reach_grounding(self):
        for path in (
            "README.md",
            "ENTRY.md",
            "AB_LANGUAGE.md",
            "AB_CONTRACT.md",
            "LANGUAGE_REFERENT_GROUND_2026-10-13.md",
        ):
            with self.subTest(path=path):
                self.assertIn(NOTE, self.read(path))
        contract = self.read("LANGUAGE_REFERENT_CONTRACT.md")
        self.assertIn("same referent", self.read("LANGUAGE_REFERENT.md"))
        self.assertIn("language for recognizing, describing, and continuing relationships", contract)
        self.assertIn("Particular generators formally labeled A and B", contract)
        self.assertIn("**formal mathematical representations**", contract)
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
