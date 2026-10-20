"""Falsify training/test leakage, unearned mixed-relation conclusions and score claims."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import ab_pharmkg_training_metapath_witness as meta
from systems.workspace import nih_p2_pharmkg_frozen_heterogeneous_trial as trial
from systems.workspace import nih_p2_external_pharmkg_heldout_trial as earlier

TRAIN=os.environ.get("PHARMKG_ORIGINAL_TRAIN")
TEST=os.environ.get("PHARMKG_ORIGINAL_TEST")
VALID=os.environ.get("PHARMKG_ORIGINAL_VALID")


class OriginalMixedSourceRelationTests(unittest.TestCase):
    def setUp(self):
        self.source=[
            ("a","I","b"),("b","GG","c"),("a","I","d"),
            ("d","GG","c"),("a","T","c"),("d","P","y"),
            ("a","GG","z"),("z","GG","c"),
        ]
        self.index=meta.training_graph(self.source)

    def test_01_original_two_different_relationship_codes_make_source_witness(self):
        w=meta.witness(self.index,head="a",target_rel="P",tail="c",
            frozen_patterns=(("I","GG"),))
        self.assertTrue(w["path_exists"])
        self.assertEqual(w["source_edge_triples"],
            [["a","I","b"],["b","GG","c"]])
        self.assertEqual(w["selected_pattern_rank"],1)
        self.assertIs(w["biomedical_entailment_established"],False)
        self.assertIs(w["temporal_fact_established"],False)
        self.assertTrue(all(len(x)==64 for x in w["source_edge_sha256"]))

    def test_02_training_target_direct_edge_cannot_be_called_heldout(self):
        with self.assertRaisesRegex(ValueError,"direct training edge"):
            meta.witness(self.index,head="a",target_rel="T",tail="c",
                frozen_patterns=(("I","GG"),))

    def test_03_unknown_or_reversed_edges_and_homogeneous_patterns_refused(self):
        self.assertFalse(meta.witness(self.index,head="c",target_rel="P",
            tail="a",frozen_patterns=(("I","GG"),))["path_exists"])
        self.assertFalse(meta.witness(self.index,head="a",target_rel="P",
            tail="unknown",frozen_patterns=(("I","GG"),))["path_exists"])
        with self.assertRaises(ValueError):
            meta.witness(self.index,head="a",target_rel="P",
                tail="c",frozen_patterns=(("GG","GG"),))
        with self.assertRaises(ValueError):
            meta.witness(self.index,head="a",target_rel="P",
                tail="c",frozen_patterns="I/GG")

    def test_04_duplicate_and_malformed_original_source_edges_rejected(self):
        with self.assertRaises(ValueError):
            meta.training_graph(self.source+[self.source[0]])
        with self.assertRaises(ValueError):
            meta.training_graph([("a","I","\nb")])

    def test_05_independent_static_oracle_not_ab_witness(self):
        g=trial.independent_static_graph(self.source)
        feature,mid=trial.independent_pattern_score(
            g,"a","c",(("I","GG"),("I","P")))
        self.assertEqual(feature,1)
        self.assertEqual(mid,"b")
        self.assertTrue(trial.static_any_twohop(g,"a","c"))
        self.assertEqual(trial.independent_pattern_score(
            g,"c","a",(("I","GG"),)),(0,None))

    def test_06_calibration_selector_fixed_from_training_and_distinct_test_salt(self):
        self.assertNotEqual(meta.TRAIN_SALT,meta.TEST_SALT)
        self.assertEqual(meta.CALIBRATION_PER_RELATION,64)
        self.assertEqual(meta.TOP_PATTERNS,3)
        self.assertEqual(meta.RELATIONS,("GG","T","P","I"))
        self.assertEqual(trial.NEW_SEED,26023)
        self.assertEqual(trial.QUESTIONS_PER_RELATION,16)

    @unittest.skipUnless(TRAIN and TEST and VALID,"requires immutable original source owner datasets")
    def test_07_source_splits_rechecked_and_frozen_rule_ranked_on_unseen(self):
        with TemporaryDirectory() as folder:
            report=trial.execute(train_file=TRAIN,test_file=TEST,valid_file=VALID)
        self.assertEqual(report["new_heldout_questions"],64)
        self.assertEqual(sum(x["questions"] for x in report["by_original_relation"].values()),64)
        self.assertTrue(report["calibration_before_heldout_selection"])
        self.assertTrue(report["training_calibration_only"])
        self.assertTrue(report["previously_scored_test_selection_excluded"])
        self.assertTrue(report["all_graph_features_use_original_training_rows_only"])
        self.assertEqual(report["mixed_A_B_proxy"],
                         report["independent_equal_strength_static_mixed_proxy"])
        self.assertEqual(report["A_B_vs_equal_strength_static_disagreements"],0)
        self.assertEqual(len(report["case_results"]),64)
        self.assertEqual(len(report["frozen_calibration_source_digest_sha256"]),64)
        self.assertEqual(len(report["untouched_new_heldout_selection_digest_sha256"]),64)
        for x in report["case_results"]:
            self.assertEqual(len(x["candidates"]),9)
            self.assertTrue(x["old_previously_scored_positive_excluded"])
            self.assertTrue(x["new_external_positive_excluded_from_graph"])
            self.assertEqual(x["mixed_rank"],x["equal_strength_independent_static_rank"])
            for c in x["candidates"]:
                self.assertEqual(c["A_B_mixed_metapath_rank_feature"],
                                 c["independent_static_frozen_metapath_feature"])
                self.assertFalse(c["biomedical_entailment_claim"])
        self.assertFalse(report["real_biomedical_temporal_event_dates"])
        self.assertFalse(report["clinical_entailment_demonstrated"])
        self.assertFalse(report["official_NIH_Phase2_benchmark_reproduced"])
        self.assertFalse(report["original_W13_runtime_modified"])
        self.assertFalse(report["original_source_file_bodies_redistributed"])

    @unittest.skipUnless(TRAIN and TEST and VALID,"requires immutable original source owner datasets")
    def test_08_second_original_evaluation_reproduces_frozen_digest_and_ranks(self):
        x=trial.execute(train_file=TRAIN,test_file=TEST,valid_file=VALID)
        y=trial.execute(train_file=TRAIN,test_file=TEST,valid_file=VALID)
        self.assertEqual(x["frozen_calibration_source_digest_sha256"],
                         y["frozen_calibration_source_digest_sha256"])
        self.assertEqual(x["untouched_new_heldout_selection_digest_sha256"],
                         y["untouched_new_heldout_selection_digest_sha256"])
        self.assertEqual(x["mixed_A_B_proxy"],y["mixed_A_B_proxy"])


if __name__=="__main__":
    unittest.main()
