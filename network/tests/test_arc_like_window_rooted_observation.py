"""Test the origin-marked A/B relation without confusing fixed counts and roots."""
import unittest
from collections import Counter
from itertools import combinations

from work.arc_like_maze.window_combined import family, classify_pair
from work.arc_like_maze.window_inverse_observation import Observation as FixedObservation, measured
from work.arc_like_maze.window_rooted_observation import (
    RootedInvestigation, RootEqualityObservation, rooted_equal,
    witness_catalog, certify_rooted_inverse,
)

class RootedInverseTests(unittest.TestCase):
    def test_catalog_replays_real_rooted_source_witnesses(self):
        catalog = witness_catalog()
        self.assertGreater(len(catalog), 0)
        laws = family()
        nonroot = [(a, b) for a, b in combinations(laws, 2)
                   if classify_pair(a, b).kind is not None
                   and not classify_pair(a, b).root_preserving]
        self.assertEqual(len(nonroot), 18)
        for a, b in nonroot:
            self.assertTrue(any(rooted_equal(a, pair) != rooted_equal(b, pair)
                                for pair in catalog))

    def test_all_48_source_laws_converge_to_exact_rooted_class(self):
        cert = certify_rooted_inverse()
        self.assertEqual(cert["mathematical_laws_checked"], 48)
        self.assertEqual(cert["distinct_rooted_classes"], 16)
        self.assertEqual(cert["maximum_root_probes_per_law"], 1)
        self.assertLessEqual(cert["maximum_fixed_probes_per_law"], 4)
        self.assertEqual(cert["root_probes_for_all_source_laws"], 12)
        for case in cert["synthetic_oracle_checks"]:
            self.assertEqual(len(case["surviving_rooted_class"]), 3)

    def test_every_source_oracle_uses_only_admitted_predicted_outcomes(self):
        final_classes = Counter()
        for oracle in family():
            state = RootedInvestigation()
            admitted = []
            for _ in range(8):
                candidate = state.next_fixed()
                if candidate is not None:
                    value = measured(oracle, candidate["word"])
                    self.assertIn(value, [r["count"] for r in candidate["predictions_NOT_admitted"]])
                    state = state.admit_fixed(FixedObservation(candidate["word"], value))
                    admitted.append("fixed")
                    continue
                root = state.next_root()
                if root is not None:
                    pair = tuple(root["words"])
                    result = rooted_equal(oracle, pair)
                    self.assertIn(result, [r["equal_at_origin"]
                                           for r in root["possible_equality_results_NOT_observed"]])
                    state = state.admit_root(RootEqualityObservation(pair, result))
                    admitted.append("root")
                    continue
                break
            self.assertEqual(state.receipt()["status"],
                             "ROOTED_CLASS_IDENTIFIED_WITHIN_DECLARED_FAMILY")
            self.assertIn(oracle, state.candidates)
            for a, b in combinations(state.candidates, 2):
                rel = classify_pair(a, b)
                self.assertIsNotNone(rel.kind)
                self.assertTrue(rel.root_preserving)
            final_classes[frozenset(state.candidates)] += 1
        self.assertEqual(len(final_classes), 16)
        self.assertEqual(sorted(final_classes.values()), [3]*16)

    def test_two_unpointed_sextuples_require_one_rooted_observation_each(self):
        for k in (0, 3):
            for oracle in [w for w in family()
                           if w.support == k and w.pulse == 1]:
                state = RootedInvestigation()
                for word in ("B", "BBB", "AABAB", "ABABAB"):
                    state = state.admit_fixed(FixedObservation(word, measured(oracle, word)))
                self.assertEqual(len(state.candidates), 6)
                proposal = state.next_root()
                self.assertIsNotNone(proposal)
                pair = tuple(proposal["words"])
                observed = rooted_equal(oracle, pair)
                final = state.admit_root(RootEqualityObservation(pair, observed))
                self.assertEqual(len(final.candidates), 3)
                self.assertIsNone(final.next_root())
                self.assertEqual(final.receipt()["status"],
                                 "ROOTED_CLASS_IDENTIFIED_WITHIN_DECLARED_FAMILY")

    def test_bad_or_conflicting_evidence_fails_closed(self):
        pair = witness_catalog()[0]
        with self.assertRaises(ValueError):
            RootEqualityObservation(("A", "B"), True)
        with self.assertRaises(ValueError):
            RootEqualityObservation(pair, 1)
        state = RootedInvestigation().admit_root(RootEqualityObservation(pair, True))
        self.assertIs(state.admit_root(RootEqualityObservation(pair, True)), state)
        with self.assertRaisesRegex(ValueError, "conflicting"):
            state.admit_root(RootEqualityObservation(pair, False))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            RootedInvestigation(rooted=(RootEqualityObservation(pair, True),
                                        RootEqualityObservation(pair, True)))
        contradictory = RootedInvestigation().admit_fixed(FixedObservation("B", 1))
        self.assertEqual(contradictory.receipt()["status"], "CONTRADICTION")
        self.assertEqual(contradictory.candidates, ())
        self.assertIsNone(contradictory.next_root())

if __name__ == "__main__":
    unittest.main()
