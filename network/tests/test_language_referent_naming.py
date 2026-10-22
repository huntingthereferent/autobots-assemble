"""Check canonical non-mathematical naming and compatibility aliases."""
import unittest
from pathlib import Path
from runtime import ab_loop, ab_information, referent_traversal, evidence_refinement
from runtime.observed_evaluator import NativeABEvaluator, NativeReferentEvaluator

ROOT = Path(__file__).resolve().parents[2]

class LanguageReferentNamingTests(unittest.TestCase):
    def test_canonical_language_documents(self):
        language = (ROOT / "LANGUAGE_REFERENT.md").read_text(encoding="utf-8")
        self.assertIn("same referent", language.lower())
        self.assertIn("mathematics is a human formal language", language.lower())
        for name in ("LANGUAGE_REFERENT_CONTRACT.md", "LANGUAGE_REFERENT_GROUND_2026-10-13.md"):
            self.assertTrue((ROOT / name).is_file())

    def test_regrounding_kept_across_language_surfaces(self):
        ground = (ROOT / "language/REGROUNDING.md").read_text(encoding="utf-8")
        index = (ROOT / "language/README.md").read_text(encoding="utf-8")
        self.assertNotIn("yes surfing :)", ground)
        self.assertIn("the same referent", ground.lower())
        self.assertIn("James is James at every layer", index)
        for path in (
            "LANGUAGE_REFERENT.md",
            "language/README.md",
            "language/SHAPE_CONTRACT.md",
            "language/PRAGMATICS.md",
            "language/english/README.md",
            "language/english/decoder.md",
            "language/english/renderer.md",
            "language/english/operator_phrases.md",
            "language/english/handoff.md",
            "language/words/README.md",
            "language/handoff/README.md",
            "protocols/language/decode.md",
            "protocols/language/render.md",
            "protocols/ai/session.md",
        ):
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("REGROUNDING.md", text)

    def test_retired_quote_material_absent(self):
        timeline = (ROOT / "language/HUMAN_DRIFT.md").read_text(encoding="utf-8")
        language_index = (ROOT / "language/README.md").read_text(encoding="utf-8")
        regrounding = (ROOT / "language/REGROUNDING.md").read_text(encoding="utf-8")
        self.assertIn("HUMAN_DRIFT.md", language_index)
        self.assertIn("HUMAN_DRIFT.md", regrounding)
        self.assertIn("Regrounding", regrounding)
        for doc in (timeline, language_index, regrounding):
            self.assertNotIn("LANGUAGE_AND_OBSERVATION.md", doc)
            self.assertNotIn("yes surfing :)", doc)
            self.assertNotIn("moving around your missunderstand", doc)

    def test_legacy_runtime_imports_remain_compatible(self):
        self.assertIs(ab_loop.ABFrame, referent_traversal.ReferentFrame)
        self.assertIs(ab_loop.ABMove, referent_traversal.ReferentMove)
        self.assertIs(ab_loop.ABLoop, referent_traversal.ReferentTraversal)
        self.assertIs(ab_information.ABOccurrence, evidence_refinement.EvidenceOccurrence)
        self.assertIs(ab_information.ABProof, evidence_refinement.EvidenceProof)
        self.assertIs(ab_information.ABInformationState, evidence_refinement.EvidenceRefinementState)
        self.assertIs(NativeABEvaluator, NativeReferentEvaluator)

if __name__ == "__main__":
    unittest.main()
