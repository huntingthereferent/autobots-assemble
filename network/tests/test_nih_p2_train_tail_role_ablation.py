"""TRAIN-only tail-role restrictions are graph diagnostics, not biology."""
from __future__ import annotations
import os
from pathlib import Path
import unittest
from systems.workspace import nih_p2_train_tail_role_ablation as ablate

TRAIN=os.environ.get("PHARMKG_ORIGINAL_TRAIN")
TEST=os.environ.get("PHARMKG_ORIGINAL_TEST")
VALID=os.environ.get("PHARMKG_ORIGINAL_VALID")


class SourceTailRoleTests(unittest.TestCase):
    def test_gold_not_in_train_role_set_is_unscorable_not_negative(self):
        scores={"x":1.0,"y":0.5}
        self.assertIsNone(ablate.rank("target",{"x","y"},scores))
        self.assertEqual(ablate.rank("target",{"x","target"},scores),2)

    def test_stable_ranks_for_source_role_and_full_universe(self):
        scores={"x":1,"target":0.5}
        self.assertEqual(ablate.rank("target",{"x","target"},scores),2)
        self.assertEqual(ablate.rank("target",{"x","target","v","u"},scores),3)

    def test_original_source_path_movement_is_not_fabricated(self):
        graph={"forward":{"h":[("I","mid")],"mid":[("GG","gold")]},
               "triples":{("h","I","mid"),("mid","GG","gold")}}
        self.assertEqual(ablate.score_map(graph,"h",(("I","GG"),)),{"gold":1})

    def test_homogeneous_pattern_does_not_pass_source_bound(self):
        with self.assertRaises(ValueError):
            ablate.score_map({"forward":{},"triples":set()},"a",(("GG","GG"),))

    @unittest.skipUnless(TRAIN and TEST and VALID,"pinned whole original PharmKG files required")
    def test_original_train_only_role_coverage_and_independent_static_oracle(self):
        result=ablate.execute(Path(TRAIN),Path(TEST),Path(VALID))
        self.assertEqual(result["schema"],ablate.SCHEMA)
        self.assertEqual(result["rank_full_source_entity_universe"]["total_questions"],64)
        self.assertEqual(result["rank_train_observed_relation_tail_role"]["total_questions"],64)
        self.assertTrue(result["candidate_restriction_is_source_structural_role_not_biomedical_class"])
        self.assertFalse(result["published_semantic_composition_verified"])
        self.assertFalse(result["test_valid_gold_admitted_to_training"])
        self.assertFalse(result["official_NIH_benchmark"])
        self.assertFalse(result["original_W13_modified"])
        self.assertTrue(all(c["independent_equal_capability_static_score_mismatches"]==0
                            for c in result["cases"]))

if __name__=="__main__":
    unittest.main()
