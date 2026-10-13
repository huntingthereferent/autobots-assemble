"""Check canonical non-mathematical naming and compatibility aliases."""
import unittest
from pathlib import Path
from runtime import ab_loop, ab_information, referent_traversal, evidence_refinement

ROOT = Path(__file__).resolve().parents[2]

class LanguageReferentNamingTests(unittest.TestCase):
    def test_canonical_language_documents(self):
        language = (ROOT / "LANGUAGE_REFERENT.md").read_text(encoding="utf-8")
        self.assertIn("same referent", language.lower())
        self.assertIn("mathematics is a human formal language", language.lower())
        for name in ("LANGUAGE_REFERENT_CONTRACT.md", "LANGUAGE_REFERENT_GROUND_2026-10-13.md"):
            self.assertTrue((ROOT / name).is_file())

    def test_legacy_runtime_imports_remain_compatible(self):
        self.assertIs(ab_loop.ABFrame, referent_traversal.ReferentFrame)
        self.assertIs(ab_loop.ABMove, referent_traversal.ReferentMove)
        self.assertIs(ab_loop.ABLoop, referent_traversal.ReferentTraversal)
        self.assertIs(ab_information.ABOccurrence, evidence_refinement.EvidenceOccurrence)
        self.assertIs(ab_information.ABProof, evidence_refinement.EvidenceProof)
        self.assertIs(ab_information.ABInformationState, evidence_refinement.EvidenceRefinementState)

if __name__ == "__main__":
    unittest.main()
