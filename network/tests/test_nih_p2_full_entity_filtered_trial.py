"""Exact full-entity PharmKG evaluation negative tests and original-source gate."""
from __future__ import annotations
import os
from pathlib import Path
import unittest

from systems.workspace import nih_p2_full_entity_filtered_trial as trial

TRAIN=os.environ.get("PHARMKG_ORIGINAL_TRAIN")
TEST=os.environ.get("PHARMKG_ORIGINAL_TEST")
VALID=os.environ.get("PHARMKG_ORIGINAL_VALID")


class FullSourceEntityRankingTests(unittest.TestCase):
    def test_independent_source_paths_are_scored_once(self):
        graph={
            "forward":{"a":[("I","mid"),("GG","x")],
                       "mid":[("GG","candidate"),("GG","a")]},
            "triples":{("a","I","mid"),("a","GG","x"),
                       ("mid","GG","candidate"),("mid","GG","a")},
        }
        out=trial.ab_scores_for_head(graph,"a",(("I","GG"),),{"candidate","a","x"})
        self.assertEqual(out,{"candidate":1.0})

    def test_ties_do_not_create_fake_best_rank(self):
        self.assertEqual(trial.tie_aware_rank(0,[0,0,0]),2)
        self.assertEqual(trial.tie_aware_rank(1,[1,0,0]),1)
        self.assertEqual(trial.tie_aware_rank(0,[0,1,0]),2.5)
        with self.assertRaises(ValueError):
            trial.tie_aware_rank(1,[0,0])

    def test_full_universe_contains_source_nodes_but_no_fabricated_nodes(self):
        rows=[("a","GG","b"),("b","GG","c")]
        universe=trial.original_entity_universe(rows,[("d","T","e")],[])
        self.assertEqual(universe,["a","b","c","d","e"])

    def test_sample_cap_and_malformed_frozen_rules_rejected(self):
        with self.assertRaises(ValueError):
            trial.ab_scores_for_head({"forward":{},"triples":set()},
                                     "h",(("GG","GG"),),{"tail"})
        with self.assertRaises(ValueError):
            trial.original_entity_universe(
                [(str(i),"GG",str(i+1)) for i in range(trial.MAX_ENTITIES+1)],
                [],[])

    @unittest.skipUnless(TRAIN and TEST and VALID,"needs all three source-owner original files")
    def test_real_full_entity_filtered_ranking_with_independent_static_scores(self):
        r=trial.run(train_file=Path(TRAIN),test_file=Path(TEST),
                    valid_file=Path(VALID))
        self.assertEqual(r["schema"],trial.SCHEMA)
        self.assertEqual(r["A_B_source_label_filtered"]["n"],64)
        self.assertGreater(r["original_source_entities_from_all_splits"],128)
        self.assertEqual(r["independent_equal_strength_static_feature_disagreements"],0)
        self.assertTrue(r["equally_capable_static_scores_identical"])
        self.assertTrue(r["test_valid_labels_used_only_to_filter_other_known_positives"])
        self.assertFalse(r["test_valid_labels_used_for_model_or_rule_selection"])
        self.assertFalse(r["actual_negative_labels_known"])
        self.assertFalse(r["official_NIH_benchmark"])
        self.assertFalse(r["original_W13_journal_modified"])
        for row in r["cases"]:
            self.assertEqual(row["independent_static_all_candidate_disagreements"],0)
            self.assertGreaterEqual(row["full_unfiltered_tie_aware_rank"],
                                    row["full_filtered_tie_aware_rank"])

if __name__=="__main__":
    unittest.main()
