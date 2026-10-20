"""Falsification controls for original OBO RDF structures and independently reasoned baseline."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest

from systems.workspace import nih_phase2_external_obo_graph_trial as a

REAL_RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
REAL_CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")


class IndependentExternalOBOTests(unittest.TestCase):
    def test_01_finite_actual_subject_object_join_not_same_subject_pattern(self):
        p="https://example.org/ro/test/subPropertyOf"
        rows=[
            dict(s="http://example.org/a",p=p,o="http://example.org/b",
                 domain="relation-types",known_at="2026-01-07",
                 valid_from="2026-01-03",valid_to="2026-02-02"),
            dict(s="http://example.org/b",p=p,o="http://example.org/c",
                 domain="relation-types",known_at="2026-01-10",
                 valid_from="2026-01-08",valid_to="2026-02-02"),
        ]
        x=a.ab_composed_query(rows,start="http://example.org/a",
             end="http://example.org/c",predicate=p,
             known="2026-01-11",valid="2026-01-15")
        self.assertTrue(x["path_exists"])
        self.assertEqual(x["middle_nodes"],["http://example.org/b"])
        self.assertFalse(x["causal_claim"])
        self.assertEqual(a.exact_two_hop_oracle(rows,"http://example.org/a",
             "http://example.org/c",p,"2026-01-11","2026-01-15"),
             ["http://example.org/b"])
        self.assertTrue(a.sparql_oracle(rows,"http://example.org/a",
             "http://example.org/c",p,"2026-01-11","2026-01-15",
             ignore_clocks=True))

    def test_02_original_graph_static_reasoner_leaks_deliberately_future_gate(self):
        p="https://example.org/ro/hasParentProperty"
        rows=[
            dict(s="http://example.org/a",p=p,o="http://example.org/b",
                known_at="2026-01-01",valid_from="2026-01-01",valid_to="2026-02-02"),
            dict(s="http://example.org/b",p=p,o="http://example.org/c",
                known_at="2026-01-19",valid_from="2026-01-01",valid_to="2026-02-02"),
        ]
        self.assertTrue(a.sparql_oracle(rows,"http://example.org/a",
            "http://example.org/c",p,"2026-01-03","2026-01-30",
            ignore_clocks=True))
        self.assertFalse(a.sparql_oracle(rows,"http://example.org/a",
            "http://example.org/c",p,"2026-01-03","2026-01-30",
            ignore_clocks=False))
        self.assertFalse(a.ab_composed_query(rows,start="http://example.org/a",
            end="http://example.org/c",predicate=p,known="2026-01-03",
            valid="2026-01-30")["path_exists"])

    def test_03_external_source_identity_and_unearned_historical_clock_not_promoted(self):
        self.assertEqual(a.COMMIT,"091f4761ec84657cc336d623e02006d6c351722c")
        self.assertEqual(a.VERSION,"2026-09-04")
        self.assertEqual(a.SOURCE_FILES,("ro-base.owl","core.owl"))

    @unittest.skipUnless(REAL_RO and REAL_CORE,"requires exact original OBO OWL files from pinned GitHub commit")
    def test_04_actual_external_graph_has_nontrivial_original_property_hierarchy(self):
        g,sources,edges=a.admit_sources({"ro-base.owl":REAL_RO,"core.owl":REAL_CORE})
        self.assertGreater(len(g),700)
        self.assertGreater(len(edges),400)
        self.assertEqual(set(sources),{"ro-base.owl","core.owl"})
        self.assertEqual({x["version"] for x in sources.values()},{"2026-09-04"})
        self.assertTrue(all(len(x["sha256"])==64 for x in sources.values()))
        self.assertTrue(any(x[3]=="biological-classes" for x in edges))
        self.assertTrue(any(x[3]=="relation-types" for x in edges))

    @unittest.skipUnless(REAL_RO and REAL_CORE,"requires exact original OBO OWL files")
    def test_05_actual_graph_independently_runs_RDF_property_paths_and_A_B(self):
        report=a.execute({"ro-base.owl":REAL_RO,"core.owl":REAL_CORE})
        self.assertGreaterEqual(report["scored_cases"],90)
        self.assertEqual(report["AB_equals_independent_exact_two_hop_cases"],
                         report["scored_cases"])
        self.assertGreater(report["full_static_true_cases"],0)
        self.assertGreater(report["static_future_leakage_cases"],0)
        self.assertTrue(report["synthetic_clock_overlay_only"])
        self.assertFalse(report["source_original_edge_publication_times_authenticated"])
        self.assertFalse(report["NIH_Phase2_reproduced"])
        self.assertFalse(report["original_W13_engine_modified"])
        self.assertFalse(report["original_raw_ontology_files_redistributed"])

    @unittest.skipUnless(REAL_RO and REAL_CORE,"requires exact original OBO OWL files")
    def test_06_explicit_original_OWL_disjointness_and_injected_probe_are_not_clinical_facts(self):
        g,_,_=a.admit_sources({"ro-base.owl":REAL_RO,"core.owl":REAL_CORE})
        result=a.ontology_disjoint_probe(g)
        self.assertEqual(len(result["original_external_disjoint_axiom"]),2)
        self.assertTrue(result["deliberately_injected_fixture"])
        self.assertGreater(result["owlrl_error_signal_count"],0)
        self.assertFalse(result["full_unsatisfiable_class_enumeration"])
        self.assertFalse(result["full_owl_dl_consistency_verified"])
        self.assertIsNone(result["original_biomedical_ontology_inconsistent"])

    def test_07_wrong_original_sources_and_missing_data_cannot_pass(self):
        with self.assertRaises(ValueError):
            a.admit_sources({})
        with self.assertRaises(FileNotFoundError):
            a.admit_sources({"ro-base.owl":"/missing", "core.owl":"/missing"})
        with TemporaryDirectory() as folder:
            p=Path(folder)
            f=p/"fake.owl";f.write_text("<html>invented graph</html>")
            with self.assertRaises(ValueError):
                a.admit_sources({"ro-base.owl":f,"core.owl":f})


if __name__=="__main__":
    unittest.main()
