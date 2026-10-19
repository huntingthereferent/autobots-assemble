"""Review-only checks for the Phase 1 concept and separate OWL ontology.

These tests check draft completeness and parsability, NOT NIH acceptance,
scientific novelty, clinical correctness or official OWL entailment quality.
"""
from __future__ import annotations

from pathlib import Path
import unittest

from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS

DIR = Path(__file__).resolve().parents[2] / "submissions/nih_its_about_time_phase1"
DOC = DIR / "PHASE1_CONCEPT_DRAFT.md"
OWL_FILE = DIR / "phase1-temporal-ontology.ttl"
NIH = Namespace("https://example.org/nih-temporal-evidence/2026-10/")


class Phase1DraftReview(unittest.TestCase):
    def test_01_exact_review_artifacts_exist(self):
        self.assertTrue(DOC.is_file())
        self.assertTrue(OWL_FILE.is_file())
        self.assertGreater(DOC.stat().st_size, 5000)
        self.assertLess(OWL_FILE.stat().st_size, 3_000_000)

    def test_02_narrative_covers_real_nih_requirements_and_boundaries(self):
        text = DOC.read_text(encoding="utf8")
        for concept in (
            "Temporal Evidence Availability",
            "Source-qualified", "valid_from", "valid_to", "available_from",
            "OWL-Time", "PROV-O", "Biolink", "clinical-trial",
            "Independent", "source", "Feasibility",
            "Static", "functional", "uncertainty",
            "January 15, 2027", "NOT REGISTERED OR SUBMITTED",
            "2023", "HTTP 403",
        ):
            with self.subTest(concept=concept):
                self.assertIn(concept.lower(), text.lower())
        self.assertNotIn("has been approved by NIH", text.lower())

    def test_03_ontology_is_machine_parseable_and_has_logical_axioms(self):
        g = Graph()
        g.parse(OWL_FILE, format="turtle")
        self.assertGreater(len(g), 75)
        self.assertIn((NIH.TemporalAssertion, RDF.type, OWL.Class), g)
        self.assertIn((NIH.validDuring, RDF.type, OWL.FunctionalProperty), g)
        self.assertIn((NIH.knownFrom, RDF.type, OWL.FunctionalProperty), g)
        self.assertIn((NIH.statusValue, RDF.type, OWL.FunctionalProperty), g)
        self.assertGreaterEqual(len(list(g.subjects(RDF.type, OWL.Restriction))), 3)
        self.assertIn((NIH.UnresolvedAvailabilityAssertion, OWL.disjointWith,
                       NIH.AuthenticatedPublicHistoryAssertion), g)
        for obs in (NIH.priorNote, NIH.delayedResult):
            self.assertIn((obs, RDF.type, NIH.AvailabilityWitnessedAssertion), g)
            self.assertEqual(len(list(g.objects(obs, NIH.knownFrom))), 1)
            self.assertEqual(len(list(g.objects(obs, NIH.validDuring))), 1)

    def test_03a_review_math_prior_art_and_unknown_evidence_are_explicit(self):
        text = DOC.read_text(encoding="utf8")
        for required in (
            "Checkable invariants and an explicit unknown state",
            "T(K1,V) subset T(K2,V)",
            "L(K,V) = S(V) minus T(K,V)",
            "L <= K < U",
            "bitemporal databases",
            "HyTE",
            "No such embedding experiment",
            "Independent reviewer falsification plan",
            "source bytes or authenticated release receipts",
        ):
            with self.subTest(required=required):
                self.assertIn(required.lower(), text.lower())

    def test_03b_updated_evidence_cannot_be_promoted_to_historical_publication(self):
        text = DOC.read_text(encoding="utf8")
        inspection = (DIR / "INSPECTION.md").read_text(encoding="utf8")
        for token in ("PR #130", "PR #132", "PR #135", "PR #136",
                      "PR #141", "PR #145", "PR #151", "PR #154",
                      "2022-11-04", "V94", "V105", "NOT YET WITNESSED"):
            with self.subTest(token=token):
                self.assertIn(token.lower(), text.lower())
        self.assertIn("neither the status field nor per-version public posting date", inspection.lower())
        self.assertIn("2023 deposit date is not a 2023 extraction witness", text.lower())
        self.assertIn("https://www.nih.gov/challenges/its-about-time-temporal-reasoning-biomedical-knowledge-graphs-challenge", inspection)

    def test_04_no_authenticated_real_historical_claims_in_ttl(self):
        g = Graph()
        g.parse(OWL_FILE, format="turtle")
        self.assertEqual(list(g.subjects(RDF.type,
                         NIH.AuthenticatedPublicHistoryAssertion)), [])
        self.assertEqual(list(g.subjects(RDF.type,
                         NIH.RegistryStatusAssertion)), [])
        self.assertGreaterEqual(len(list(g.subjects(RDF.type,
                                NIH.EvidenceClass))), 5)


if __name__ == "__main__":
    unittest.main()
