"""Original held-out biomedical graph probes and source leakage controls."""
from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import ab_heldout_biomedical_relation_paths as ab
from systems.workspace import nih_p2_external_pharmkg_heldout_trial as h

TRAIN=os.environ.get("PHARMKG_ORIGINAL_TRAIN")
TEST=os.environ.get("PHARMKG_ORIGINAL_TEST")
VALID=os.environ.get("PHARMKG_ORIGINAL_VALID")


class ExternalPharmKGHeldoutTest(unittest.TestCase):
    def test_01_exact_source_edges_retain_2_and_3_hop_relationships(self):
        rows=[
            ("gene-a","GG","gene-b"),
            ("gene-b","GG","gene-c"),
            ("gene-c","GG","gene-d"),
            ("drug-e","T","condition-f"),
        ]
        idx=ab.build(rows)
        second=ab.witness(idx,head="gene-a",relation="GG",tail="gene-c")
        self.assertEqual(second["source_path_nodes"],["gene-a","gene-b","gene-c"])
        self.assertEqual(second["source_path_hops"],2)
        third=ab.witness(idx,head="gene-a",relation="GG",tail="gene-d")
        self.assertEqual(third["source_path_hops"],3)
        self.assertEqual(third["source_path_nodes"],
                         ["gene-a","gene-b","gene-c","gene-d"])
        self.assertEqual(third["source_edge_sha256"],
                         [ab.edge_hash(a,"GG",b) for a,b in zip(
                             third["source_path_nodes"],third["source_path_nodes"][1:])])
        self.assertEqual(h.static_shortest_path(idx,"gene-a","GG","gene-d"),3)

    def test_02_not_an_unearned_drug_treatment_inference(self):
        idx=ab.build([("drug-x","T","disease-y"),("disease-y","T","gene-z")])
        r=ab.witness(idx,head="drug-x",relation="T",tail="gene-z")
        self.assertTrue(r["path_exists"])
        self.assertIs(r["source_path_as_biomedical_truth"],False)
        self.assertFalse(ab.witness(idx,head="gene-z",relation="T",
                                    tail="drug-x")["path_exists"])
        self.assertFalse(ab.witness(idx,head="drug-x",relation="GG",
                                    tail="gene-z")["path_exists"])

    def test_03_original_direct_training_edge_cannot_be_called_heldout_prediction(self):
        idx=ab.build([("g1","GG","g2")])
        r=ab.witness(idx,head="g1",relation="GG",tail="g2")
        self.assertFalse(r["path_exists"])
        self.assertTrue(r["direct_training_edge_exists"])

    def test_04_tie_aware_rank_and_missing_path_scores(self):
        self.assertEqual(h.rank_scores([0,0,0]),2)
        self.assertEqual(h.rank_scores([1/2,1/2,0]),1.5)
        self.assertEqual(h.rank_scores([0,1/2,1/3]),3)
        self.assertEqual(h.candidate_score(None),0)

    def test_05_source_tampering_and_wrong_splits_refused(self):
        with TemporaryDirectory() as td:
            path=Path(td)/"test.tsv"
            path.write_text("g1\tGG\tg2\n")
            with self.assertRaises(ValueError):
                h.read_source(path,"test.tsv")
        with self.assertRaises(ValueError):
            ab.build([("g1","GG","g2"),("g1","GG","g2")])
        with self.assertRaises(ValueError):
            ab.witness(ab.build([]),head="a",relation="GG",tail="b",
                       max_hops=12)

    @unittest.skipUnless(TRAIN and TEST and VALID,
                         "requires actual immutable original external train/test/valid files")
    def test_06_actual_external_unseen_questions_no_train_test_contamination(self):
        result=h.execute(train_file=TRAIN,test_file=TEST,valid_file=VALID)
        self.assertEqual(result["original_source_commit"],h.COMMIT)
        self.assertEqual(result["heldout_test_questions"],64)
        self.assertEqual(len(result["case_results"]),64)
        self.assertEqual(result["source_path_result_mismatches_vs_static_reasoner"],0)
        self.assertEqual(result["independent_full_training_static_3hop_hits_at_1"],
                         result["AB_link_proxy_hits_at_1"])
        self.assertFalse(result["static_training_graph_fed_test_or_validation_data"])
        self.assertFalse(result["source_split_is_chronological"])
        self.assertFalse(result["observed_original_event_known_at"])
        self.assertFalse(result["source_path_proves_direct_heldout_biomedical_relation"])
        self.assertFalse(result["official_NIH_Phase2_benchmark_reproduced"])
        self.assertFalse(result["original_W13_journal_modified"])
        self.assertTrue(all(x["test_positive_excluded_from_training"]
                            for x in result["case_results"]))
        self.assertTrue(all(len(x["candidate_results"])==9
                            for x in result["case_results"]))
        self.assertTrue(all(c["AB_path_hops"]==c["independent_static_path_hops"]
                            for x in result["case_results"] for c in x["candidate_results"]))
        for split,expected in h.SOURCE_FILES.items():
            source={"train.tsv":"train","test.tsv":"test","valid.tsv":"valid"}[split]
            self.assertEqual(result["real_original_split_identity"][source]["git_blob_sha1"],
                             expected)

    def test_07_positive_gold_does_not_make_corruptions_validated_negatives(self):
        self.assertEqual(h.CONTROLS,8)
        self.assertEqual(h.RELATIONS,("GG","T","P","I"))
        self.assertEqual(h.PER_RELATION,16)
        self.assertEqual(h.SEED,26022)


if __name__=="__main__":
    unittest.main()
