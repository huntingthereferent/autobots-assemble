"""Regression tests for structural A/B witness vs unverified black-box guesses."""
import unittest
from itertools import product

from ab_chatbot_admission_probe import OffOrbitAlteration
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_structural_witness import (
    ANCHORS, CovariantSource, check_covariances, reconstruct,
    reconstruct_known_a, reconstruct_full_table,
)


class StructuralWitnessTests(unittest.TestCase):
    def test_all_27_source_proven_laws_need_four_reads(self):
        for phi in product(range(3), repeat=3):
            with self.subTest(phi=phi):
                source = CovariantSource.for_law(phi)
                result = reconstruct(source.step, source=source)
                self.assertEqual(result.status, "VERIFIED_SOURCE_CONSTRUCTION")
                self.assertEqual(result.phi, phi)
                self.assertEqual(result.calls, 4)
                self.assertEqual(tuple((s, a) for s, a, _ in result.queries), ANCHORS)

    def test_all_54_transitions_recovered_per_law(self):
        for phi in product(range(3), repeat=3):
            target = FiniteSystem(phi)
            predictions = reconstruct_full_table(phi)
            self.assertEqual(len(predictions), 54)
            for (state, action), output in predictions.items():
                self.assertEqual(output, target.step(state, action))

    def test_external_black_box_not_certified_by_four_samples(self):
        for phi in product(range(3), repeat=3):
            result = reconstruct(FiniteSystem(phi).step)
            self.assertEqual(result.status, "CONDITIONAL_ON_COVARIANCE")
            self.assertEqual(result.phi, phi)
            self.assertEqual(result.calls, 4)

    def test_counterexample_preserves_anchors_but_breaks_structure(self):
        target = OffOrbitAlteration()
        result = reconstruct(target.step)
        self.assertEqual(result.status, "CONDITIONAL_ON_COVARIANCE")
        self.assertEqual(result.phi, (0, 0, 0))
        valid, witness, calls = check_covariances(target.step)
        self.assertFalse(valid)
        self.assertIsNotNone(witness)
        self.assertLessEqual(calls, 54)

    def test_bad_anchor_obstructs_grammar(self):
        def changed(state, action):
            if state == (0, 0, 0) and action == "A":
                return (0, 0, 0)
            return FiniteSystem((0, 0, 0)).step(state, action)
        result = reconstruct(changed)
        self.assertEqual(result.status, "OBSTRUCTED_BY_ANCHOR")
        self.assertEqual(result.calls, 1)
        self.assertEqual(result.counterexample[0:2], ((0, 0, 0), "A"))

    def test_budget_must_cover_four_anchors(self):
        target = FiniteSystem((0, 1, 2))
        for budget in range(4):
            with self.subTest(budget=budget):
                result = reconstruct(target.step, max_calls=budget)
                self.assertEqual(result.status, "UNKNOWN_BUDGET")
                self.assertEqual(result.calls, budget)
        self.assertEqual(reconstruct(target.step, max_calls=4).calls, 4)

    def test_unrelated_oracle_cannot_borrow_source_witness(self):
        source = CovariantSource.for_law((0, 1, 2))
        with self.assertRaisesRegex(ValueError, "does not own"):
            reconstruct(OffOrbitAlteration().step, source=source)

    def test_native_covariances_hold_everywhere(self):
        for phi in product(range(3), repeat=3):
            ok, witness, calls = check_covariances(CovariantSource.for_law(phi).step)
            self.assertTrue(ok)
            self.assertIsNone(witness)
            self.assertEqual(calls, 54)

    def test_known_a_three_b_anchors_are_sufficient_for_all_27(self):
        for phi in product(range(3), repeat=3):
            with self.subTest(phi=phi):
                source = CovariantSource.for_law(phi)
                result = reconstruct_known_a(source.step, source=source)
                self.assertEqual(result.status, "VERIFIED_SOURCE_CONSTRUCTION")
                self.assertEqual(result.phi, phi)
                self.assertEqual(result.calls, 3)
                self.assertTrue(all(action == "B" for _, action, _ in result.queries))
                self.assertEqual(
                    reconstruct_known_a(FiniteSystem(phi).step).status,
                    "CONDITIONAL_ON_KNOWN_A_AND_COVARIANCE",
                )

    def test_two_b_queries_cannot_determine_three_free_phi_entries(self):
        # Exhaustive: every B input observes only phi at its x1 coordinate.
        # Any two B inputs leave at least one of phi(0),phi(1),phi(2) unknown.
        inputs = tuple(product(range(3), repeat=3))
        parameters = tuple(product(range(3), repeat=3))
        for i, left in enumerate(inputs):
            for right in inputs[i + 1:]:
                signatures = {
                    (FiniteSystem(phi).step(left, "B"),
                     FiniteSystem(phi).step(right, "B"))
                    for phi in parameters
                }
                self.assertLess(len(signatures), 27)

    def test_known_a_rejects_incorrect_source_before_oracle_calls(self):
        source = CovariantSource((2, 0, 0),
                                 ((0, 1, 0), (0, 2, 1), (0, 0, 2)))
        result = reconstruct_known_a(source.step, source=source)
        self.assertEqual(result.status, "OBSTRUCTED_BY_SOURCE")
        self.assertEqual(result.calls, 0)

    def test_known_a_cannot_certify_unwitnessed_source(self):
        altered = OffOrbitAlteration()
        result = reconstruct_known_a(altered.step)
        self.assertEqual(result.status, "CONDITIONAL_ON_KNOWN_A_AND_COVARIANCE")
        self.assertEqual(result.phi, (0, 0, 0))
        with self.assertRaises(ValueError):
            reconstruct_known_a(altered.step, source=CovariantSource.for_law((0, 0, 0)))
        self.assertEqual(reconstruct_known_a(altered.step, max_calls=2).status,
                         "UNKNOWN_BUDGET")

    def test_source_rejects_non_field_anchors(self):
        with self.assertRaises(ValueError):
            CovariantSource((9, 0, 0), ((0, 1, 0), (0, 2, 0), (0, 0, 0)))


if __name__ == '__main__':
    unittest.main()
