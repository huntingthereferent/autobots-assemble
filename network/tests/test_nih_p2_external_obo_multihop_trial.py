"""Falsify fabricated paths and compare original OBO to RDFLib SPARQL+."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import unittest

from systems.workspace import ab_finite_original_uri_multihop as ab
from systems.workspace import nih_p2_external_obo_multihop_trial as external
from systems.workspace import nih_phase2_external_obo_graph_trial as old

RO=os.environ.get("NIH_ORIGINAL_RO_BASE_OWL")
CORE=os.environ.get("NIH_ORIGINAL_RO_CORE_OWL")
P="http://www.w3.org/2000/01/rdf-schema#subPropertyOf"
BASE="https://example.org/test/"


def edge(a,b,known="2026-01-02"):
    s,p,o=BASE+a,P,BASE+b
    return {
        "s":s,"p":p,"o":o,"domain":"relation-types",
        "known_at":known,
        "valid_from":"2026-01-01","valid_to":"2026-02-02",
        "source_relation_sha256":old.digest("|".join((s,p,o)).encode()),
    }


def query(rows,max_hops=6,known="2026-01-20"):
    return ab.traverse(
        rows,start=BASE+"a",end=BASE+"d",
        predicate=P,known_at=known,target_at="2026-01-20",
        max_hops=max_hops
    )


class FiniteOriginalSourceTraversalTests(unittest.TestCase):
    def test_01_genuine_three_source_edge_path_with_intermediates(self):
        rows=[edge("a","b"),edge("b","c"),edge("c","d")]
        two=query(rows,2)
        self.assertFalse(two["path_exists"])
        self.assertTrue(two["exhaustive_within_hop_bound"])
        three=query(rows,3)
        self.assertTrue(three["path_exists"])
        self.assertEqual(three["path_hops"],3)
        self.assertEqual(three["source_witness_uris"],
                         [BASE+x for x in "abcd"])
        self.assertEqual(len(three["source_witness_edges"]),3)
        self.assertFalse(three["unbounded_reachability_proved"])
        self.assertTrue(external.corroborate(
            three,{x["source_relation_sha256"]:x for x in rows},
            known="2026-01-20",target="2026-01-20"))

    def test_02_independent_rdf_sparql_reachability_and_synthetic_future(self):
        rows=[edge("a","b"),edge("b","c"),
              edge("c","d",known="2026-01-17")]
        self.assertTrue(old.sparql_oracle(rows,BASE+"a",BASE+"d",P,
                                         "2026-01-05","2026-01-20",ignore_clocks=True))
        self.assertFalse(old.sparql_oracle(rows,BASE+"a",BASE+"d",P,
                                          "2026-01-05","2026-01-20",ignore_clocks=False))
        self.assertFalse(query(rows,3,"2026-01-05")["path_exists"])
        self.assertTrue(query(rows,3,"2026-01-20")["path_exists"])

    def test_03_cycle_cannot_fabricate_short_original_path(self):
        rows=[edge("a","b"),edge("b","a"),edge("b","c"),edge("c","d")]
        r=query(rows)
        self.assertTrue(r["path_exists"])
        self.assertEqual(r["source_witness_uris"],
                         [BASE+"a",BASE+"b",BASE+"c",BASE+"d"])
        self.assertEqual(len(set(r["source_witness_uris"])),4)

    def test_04_subject_object_direction_and_missing_edge_not_invented(self):
        rows=[edge("b","a"),edge("b","c"),edge("c","d")]
        self.assertFalse(query(rows)["path_exists"])
        rows=[edge("a","b"),edge("x","c"),edge("c","d")]
        self.assertFalse(query(rows)["path_exists"])
        self.assertTrue(query(rows)["exhaustive_within_hop_bound"])

    def test_05_negative_is_scoped_by_declared_hop_limit(self):
        rows=[edge("a","b"),edge("b","c"),edge("c","d")]
        self.assertFalse(query(rows,2)["path_exists"])
        self.assertTrue(query(rows,3)["path_exists"])
        for hops in (0,7,-1,None,True):
            with self.subTest(hops=hops),self.assertRaises(ValueError):
                query(rows,hops)

    def test_06_unknown_source_timestamps_and_duplicate_edge_fail_closed(self):
        rows=[edge("a","b"),edge("b","c"),edge("c","d")]
        for changed in (
            rows+[rows[0]],
            [{**rows[0],"known_at":"2026-02-30"},*rows[1:]],
            [{**rows[0],"valid_to":"2026-01-01"},*rows[1:]],
            [{**rows[0],"source_relation_sha256":"fabricated"},*rows[1:]],
            [{**rows[0],"s":"not-a-uri"},*rows[1:]],
            [{**rows[0],"unsupported":"new"},*rows[1:]],
        ):
            with self.assertRaises(ValueError):
                query(changed)
        with self.assertRaises(ValueError):
            query(rows,known="2026-01")

    def test_07_witness_cannot_spoof_independently_observed_edge(self):
        rows=[edge("a","b"),edge("b","c"),edge("c","d")]
        report=query(rows)
        original_index={x["source_relation_sha256"]:x for x in rows}
        modified=deepcopy(report)
        modified["source_witness_edges"][0]["source_object"]=BASE+"fake"
        with self.assertRaises(ValueError):
            external.corroborate(modified,original_index,
                                 known="2026-01-20",target="2026-01-20")
        modified=deepcopy(report)
        modified["source_witness_edges"][1]["source_relation_sha256"]="f"*64
        with self.assertRaises(ValueError):
            external.corroborate(modified,original_index,
                                 known="2026-01-20",target="2026-01-20")

    @unittest.skipUnless(RO and CORE,"requires original two pinned OBO source OWL files")
    def test_08_exact_external_original_graph_recovers_longer_source_paths(self):
        d=external.execute({"ro-base.owl":RO,"core.owl":CORE})
        self.assertEqual(d["original_external_benchmark_cases"],402)
        self.assertEqual(d["original_source_rdf_triples"],8319)
        self.assertEqual(d["original_hierarchy_edges"],802)
        self.assertEqual(d["original_two_hop_exact_oracle_mismatches"],0)
        self.assertEqual(d["previously_exposed_three_hop_only_static_reachable_misses"],87)
        self.assertGreater(d["recovered_real_source_longer_temporal_paths"],0)
        self.assertGreater(d["recovered_real_source_longer_temporal_paths_at_latest_cutoff"],0)
        self.assertEqual(d["latest_cutoff_source_cases"],134)
        self.assertEqual(d["source_original_publication_clocks_known"],False)
        self.assertFalse(d["official_NIH_Phase2_benchmark_reproduced"])
        self.assertFalse(d["original_W13_emitted_temporal_python_modified"])

    @unittest.skipUnless(RO and CORE,"requires original two pinned OBO source OWL files")
    def test_09_independent_real_graph_reasoner_comparison_tracks_remaining_gaps(self):
        d=external.execute({"ro-base.owl":RO,"core.owl":CORE})
        self.assertEqual(d["original_external_benchmark_cases"],len(d["cases"]))
        self.assertEqual(d["unresolved_or_out_of_scope_spaql_reachability_cases"],
                         sum(not x["agrees_with_independent_temporal_SPARQL"]
                             for x in d["cases"]))
        for row in d["cases"]:
            if row["new_AB_finite_multihop"]:
                self.assertGreaterEqual(row["path_hops"],1)
                self.assertLessEqual(row["path_hops"],6)
                self.assertEqual(len(row["original_source_edge_receipts"]),row["path_hops"])
                self.assertEqual(len(row["source_path_uri_witness"]),row["path_hops"]+1)
        self.assertFalse(d["real_clinical_temporal_validity_inferred"])
        self.assertFalse(d["full_OWL_reasoning_implemented"])
        self.assertFalse(d["World48_required"])


if __name__=="__main__":
    unittest.main()
