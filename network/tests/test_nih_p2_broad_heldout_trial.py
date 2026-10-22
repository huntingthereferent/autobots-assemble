"""Independent controls for broader PharmKG heldout link-ranking proxy."""
from __future__ import annotations

import os
from pathlib import Path
import unittest

from systems.workspace import nih_p2_broad_heldout_trial as trial

TRAIN = os.environ.get("PHARMKG_ORIGINAL_TRAIN")
TEST = os.environ.get("PHARMKG_ORIGINAL_TEST")
VALID = os.environ.get("PHARMKG_ORIGINAL_VALID")


class BroadHeldoutControls(unittest.TestCase):
    def test_rank_handles_ties_and_nontrivial_order(self):
        self.assertEqual(trial.rank([1, 0, 0]), 1)
        self.assertEqual(trial.rank([0, 0, 0]), 2)
        self.assertEqual(trial.rank([0, 1, 0, 0]), 3)
        self.assertEqual(trial.rank([0.5, 0.5, 1, 0]), 2.5)
        for bad in ([], [1, -1], [0, "x"]):
            with self.assertRaises(ValueError):
                trial.rank(bad)

    def test_pool_is_deterministic_and_has_no_train_direct_edges(self):
        vocab = {"T": {"a", "b", "c", "d", "e", "f"}}
        training = {("h", "T", "a")}
        a = trial.choose_pool("h", "T", "z", vocab, training, 3)
        b = trial.choose_pool("h", "T", "z", vocab, training, 3)
        self.assertEqual(a, b)
        self.assertEqual(a[0], "z")
        self.assertEqual(len(a), 4)
        self.assertNotIn("a", a)
        self.assertEqual(len(set(a)), len(a))

    def test_pool_underflow_and_unbounded_population_refused(self):
        with self.assertRaisesRegex(ValueError, "too few"):
            trial.choose_pool("h", "T", "z", {"T": {"a"}}, set(), 2)
        with self.assertRaisesRegex(ValueError, "bounded"):
            trial.choose_pool("h", "T", "z", {"T": {"a"}}, set(), 513)

    def test_new_question_selection_rejects_precedent_when_source_too_small(self):
        with self.assertRaises(ValueError):
            trial.choose_new([("h", "GG", "t")], [])

    @unittest.skipUnless(TRAIN and TEST and VALID,
                         "immutable original PharmKG source files required")
    def test_actual_new_original_heldout_source_and_equal_static_oracle(self):
        result = trial.evaluate(train_file=Path(TRAIN), test_file=Path(TEST),
                                valid_file=Path(VALID))
        self.assertEqual(result["schema"], trial.SCHEMA)
        self.assertEqual(result["A_B_and_static_same_information_metrics"]["cases"], 64)
        self.assertEqual(result["equally_capable_static_rank_disagreements"], 0)
        self.assertEqual(len(result["all_cases"]), 64)
        self.assertFalse(result["candidate_pool_is_full_entity_ranking"])
        self.assertFalse(result["unlabeled_alternatives_confirmed_false"])
        self.assertFalse(result["test_and_valid_labels_used_for_training_or_scoring"])
        self.assertFalse(result["original_splits_are_temporal"])
        self.assertFalse(result["official_NIH_benchmark"])
        self.assertTrue(all(c["candidate_count"]==129 for c in result["all_cases"]))
        self.assertTrue(all(c["raw_tie_midrank"] == c["static_same_information_midrank"]
                            for c in result["all_cases"]))
        self.assertTrue(all(c["candidate_selection_train_vocabulary_only"]
                            for c in result["all_cases"]))


if __name__=="__main__":
    unittest.main()
