"""Direct behavioral tests of two previously measured NIH Phase 2-style gaps."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from rdflib import Graph,URIRef
from systems.workspace import nih_phase2_direct_reproduction as old
from systems.workspace import nih_phase2_time_respecting_chain_trial as parent
from systems.workspace import nih_phase2_source_revision_rdf_trial as trial
from systems.workspace import ab_source_revision_relation as revisions
from systems.workspace import ab_bounded_rdf_source_composition as rdf


def claim(rows=old.BIOMED,known="2026-01-12",target="2026-01-12",
          subject="fictional-paper",object="claim-z"):
    return revisions.observe(rows,subject=subject,claim_object=object,
        support_predicate="supports-claim",revision_predicate="retracts-claim",
        known_at=known,target_at=target)


class Phase2RevisionRDFTests(unittest.TestCase):
    def test_01_source_revision_with_original_history_retained(self):
        r=claim()
        self.assertEqual(r["outcome"],"SUPERSEDED")
        self.assertIs(r["currently_supported"],False)
        self.assertEqual(r["source_statement_ids_still_in_history"],["claim-original"])
        self.assertEqual(r["source_revision_ids_still_in_history"],["claim-correction"])
        self.assertEqual(r["effective_supersession_witnesses"][0]["source_ids"],
                         ["claim-original","claim-correction"])
        self.assertTrue(r["not_silently_deleted"])
        self.assertFalse(r["clinical_truth_claimed"])

    def test_02_before_revision_source_claim_remains_supported(self):
        r=claim(known="2026-01-07")
        self.assertEqual(r["outcome"],"SUPPORTED")
        self.assertIs(r["currently_supported"],True)
        self.assertEqual(r["source_revision_ids_still_in_history"],[])
        self.assertEqual(r["source_statement_ids_still_in_history"],["claim-original"])

    def test_03_cross_subject_and_wrong_claim_are_not_retractions(self):
        for field,val in (("subject","different-paper"),("object","other-claim")):
            data=deepcopy(old.BIOMED)
            for row in data:
                if row["id"]=="claim-correction":row[field]=val
            with self.subTest(field=field):
                self.assertEqual(claim(data)["outcome"],"SUPPORTED")

    def test_04_same_known_day_conflict_is_ambiguous_not_supported_or_superseded(self):
        data=deepcopy(old.BIOMED)
        for row in data:
            if row["id"]=="claim-correction":row["known_at"]="2026-01-02"
        result=claim(data)
        self.assertEqual(result["outcome"],"AMBIGUOUS")
        self.assertIsNone(result["currently_supported"])
        self.assertTrue(result["unresolved_ties"])

    def test_05_missing_or_not_yet_valid_revision_and_prior_revision(self):
        self.assertEqual(claim(known="2026-01-01")["outcome"],"NOT_AVAILABLE")
        data=deepcopy(old.BIOMED)
        next(r for r in data if r["id"]=="claim-correction")["valid_from"]="2026-01-20"
        self.assertEqual(claim(data)["outcome"],"SUPPORTED")
        data=deepcopy(old.BIOMED)
        next(r for r in data if r["id"]=="claim-correction")["known_at"]="2026-01-01"
        self.assertEqual(claim(data)["outcome"],"SUPPORTED")

    def test_06_bounded_RDF_actual_triples_are_present_and_parseable(self):
        r=rdf.infer(old.BIOMED,parent.STAGES,
            known_at="2026-01-11",target_at="2026-01-11",
            subject="fictional-cohort")
        self.assertEqual(r["new_triple_count"],1)
        self.assertTrue(r["inference_exists"])
        graph=Graph().parse(data=r["rdf_graph_ntriples"],format="nt")
        self.assertEqual(len(graph),r["entailed_graph_triple_count"])
        a,b,c=(rdf.EX["event-"+x] for x in (
            "therapy-alpha","response-poor","therapy-beta"))
        self.assertIn((a,rdf.EX.observedThen,b),graph)
        self.assertIn((b,rdf.EX.observedThen,c),graph)
        self.assertIn((a,rdf.EX.observedBefore,c),graph)
        self.assertFalse(r["actual_owl_property_chain_axiom_evaluated"])
        self.assertFalse(r["owl_unsatisfiable_classes_measured"])

    def test_07_RDF_graph_inference_requires_chronological_original_source(self):
        early=rdf.infer(old.BIOMED,parent.STAGES,
            known_at="2026-01-07",target_at="2026-01-11",
            subject="fictional-cohort")
        self.assertFalse(early["inference_exists"])
        backdated=rdf.infer(old.BIOMED,parent.STAGES,
            known_at="2026-01-11",target_at="2026-01-07",
            subject="fictional-cohort")
        self.assertFalse(backdated["inference_exists"])
        wrong=deepcopy(old.BIOMED)
        next(x for x in wrong if x["id"]=="therapy-beta")["subject"]="another-cohort"
        self.assertFalse(rdf.infer(wrong,parent.STAGES,
            known_at="2026-01-11",target_at="2026-01-11")["inference_exists"])

    def test_08_RDF_finite_bounds_not_a_general_OWL_reasoner(self):
        with self.assertRaises(ValueError):
            rdf.infer(old.BIOMED,parent.STAGES[:2],
                known_at="2026-01-11",target_at="2026-01-11")
        r=rdf.infer(old.BIOMED,parent.STAGES,
            known_at="2026-01-11",target_at="2026-01-11")
        self.assertIs(r["original_W13_temporal_engine_modified"],False)
        self.assertIs(r["clinical_causality_entailment"],False)

    @classmethod
    def setUpClass(cls):
        with TemporaryDirectory() as td:cls.report=trial.evaluate(output_dir=Path(td))
        cls.by_id={x["task"]:x for x in cls.report["questions"]}

    def test_09_original_scores_preserved_new_two_gaps_measured(self):
        r=self.report
        self.assertEqual(r["original_W13"],{"W13":8,"static":6,"cases":13})
        self.assertEqual(r["source_chain_only_pass"],11)
        self.assertEqual(r["source_revision_and_RDF_composition_pass"],13)
        self.assertEqual(r["source_revision_and_RDF_composition_fail"],0)
        self.assertEqual(r["practice_question_count"],13)
        self.assertFalse(r["official_NIH_Phase2_reproduction_completed"])
        self.assertFalse(r["real_OWL_property_chain_axiom_engine_implemented"])
        self.assertFalse(r["OWL_inconsistency_check_implemented"])
        self.assertFalse(r["original_W13_temporal_python_modified"])
        self.assertFalse(r["original_W13_journal_modified"])

    def test_10_new_successes_have_originally_measured_failures(self):
        for key in ("superseded-claim-not-current","rdf-property-chain-inference"):
            x=self.by_id[key]
            self.assertFalse(x["original_native_pass"])
            self.assertTrue(x["new_pass"])
            self.assertTrue(x["new_answer_supported"])
            self.assertIsNone(x["original_native_answer"] if key.startswith("rdf") else None)

    def test_11_160_unseen_revisions_independently_oracled(self):
        d=self.report["unseen_revision_cases"]
        self.assertEqual(d["cases"],160)
        self.assertEqual(d["independent_oracle_cases"],160)
        self.assertEqual(sum(d["outcomes"].values()),160)
        for name in ("SUPPORTED","SUPERSEDED","AMBIGUOUS","NOT_AVAILABLE"):
            self.assertGreater(d["outcomes"][name],0,name)
        self.assertTrue(all(x["outcome"]==x["independent_outcome"] for x in d["rows"]))
        self.assertTrue(all(x["source_history_retained"] for x in d["rows"]))

    def test_12_160_unseen_RDF_graphs_and_independent_product_oracle(self):
        d=self.report["unseen_RDF_cases"]
        self.assertEqual(d["cases"],160)
        self.assertEqual(d["independent_oracle_cases"],160)
        self.assertGreaterEqual(d["positive"],40)
        self.assertGreaterEqual(d["negative"],80)
        self.assertEqual(d["positive"]+d["negative"],160)
        self.assertEqual({x["domain"] for x in d["rows"]},{"care","surveillance"})
        self.assertTrue(all(x["inference"]==x["independent_inference"]
                            for x in d["rows"]))

    def test_13_fictional_practice_success_does_not_promote_clinical_claims(self):
        d=self.report
        for key in ("real_historical_biomedical_KG_data_tested",
                    "official_NIH_Phase2_shared_benchmark_used",
                    "official_NIH_Phase2_reproduction_completed",
                    "clinical_effectiveness_inferred","World48_required"):
            self.assertIs(d[key],False,key)


if __name__=="__main__":
    unittest.main()
