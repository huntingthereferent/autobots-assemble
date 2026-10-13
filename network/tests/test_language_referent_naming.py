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
        self.assertIn("yes surfing :)", ground)
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

    def test_human_drift_preserves_dated_quotes_and_distinctions(self):
        timeline = (ROOT / "language/HUMAN_DRIFT.md").read_text(encoding="utf-8")
        language_index = (ROOT / "language/README.md").read_text(encoding="utf-8")
        regrounding = (ROOT / "language/REGROUNDING.md").read_text(encoding="utf-8")
        for quote in (
            "Grounding and oscillating should be the same here",
            "it not where did we start its more how do we merge this acquird data with the start",
            'yes if ever you "DONT KNOW" just reground :)',
            'we are talking about "HUMAN DRIFT"',
            "i was moving around your missunderstand essentially",
        ):
            with self.subTest(quote=quote):
                self.assertIn(quote, timeline)
        self.assertIn("### September 18", timeline)
        self.assertIn("### September 25", timeline)
        self.assertIn("### September 29", timeline)
        self.assertIn("### October 13", timeline)
        self.assertIn("HUMAN_DRIFT.md", language_index)
        self.assertIn("HUMAN_DRIFT.md", regrounding)
        self.assertIn("Regrounding", regrounding)
        self.assertIn("Surfing was one image", regrounding)

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
