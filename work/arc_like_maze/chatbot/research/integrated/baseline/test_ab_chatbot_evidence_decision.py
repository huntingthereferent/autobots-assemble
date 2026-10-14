"""Standalone regression tests for evidence strength, independence and walls."""
import unittest
from itertools import product

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_admission_probe import OffOrbitAlteration
from ab_chatbot_evidence_decision import assess


class EvidenceDecisionTests(unittest.TestCase):
    def test_cheap_behavioral_question_never_uses_full_state_oracle(self):
        target = FiniteSystem((0, 1, 2))
        def forbid_step(*_):
            raise AssertionError("full-state oracle should not be called")
        result = assess(target.equal_ends, forbid_step, requested_claim="behavioral_class")
        self.assertEqual(result.status, "CONDITIONAL_BEHAVIORAL_CLASS")
        self.assertIsNone(result.admission)
        self.assertIn(target.phi, result.behavioral_candidates)
        self.assertIn(len(result.rooted_observations), (2, 3))

    def test_rooted_observations_never_prove_full_state_law(self):
        for params in product(range(3), repeat=3):
            target = FiniteSystem(params)
            result = assess(target.equal_ends)
            self.assertEqual(result.status, "UNKNOWN_FULL_STATE")
            self.assertFalse(result.full_state_verified)
            self.assertGreaterEqual(len(result.behavioral_candidates), 1)

    def test_all_nine_full_state_verified(self):
        for a, b in product(range(3), repeat=2):
            target = FiniteSystem((0, a, b))
            result = assess(target.equal_ends, target.step)
            self.assertEqual(result.status, "VERIFIED_NINE_LAW")
            self.assertTrue(result.full_state_verified)
            self.assertEqual(result.admission.calls, 54)
            self.assertEqual(result.admission.inferred_phi, target.phi)
            self.assertIn(target.phi, result.behavioral_candidates)

    def test_other_eighteen_are_verified_but_not_promoted_to_nine(self):
        for first, a, b in product((1, 2), range(3), range(3)):
            target = FiniteSystem((first, a, b))
            result = assess(target.equal_ends, target.step)
            self.assertEqual(result.status, "VERIFIED_OTHER_27_LAW")
            self.assertTrue(result.full_state_verified)
            self.assertNotIn(target.phi, result.behavioral_candidates)

    def test_full_state_budget_under_54_cannot_certify(self):
        target = FiniteSystem((0, 1, 2))
        for max_calls in (0, 1, 3, 53):
            result = assess(target.equal_ends, target.step,
                            max_full_state_calls=max_calls)
            self.assertEqual(result.status, "UNKNOWN_FULL_STATE")
            self.assertFalse(result.full_state_verified)
            self.assertEqual(result.admission.calls, max_calls)

    def test_unobserved_mutation_rejected_by_full_state_inspection(self):
        target = OffOrbitAlteration()
        result = assess(target.equal_ends, target.step)
        self.assertEqual(result.status, "REJECTED_27_GRAMMAR")
        self.assertEqual(result.admission.mismatch[0], (0, 0, 1))
        self.assertFalse(result.full_state_verified)

    def test_cross_oracle_disagreement_blocks_positive_claim(self):
        rooted = FiniteSystem((0, 1, 2))
        conflicting = FiniteSystem((1, 0, 0))
        result = assess(rooted.equal_ends, conflicting.step)
        self.assertEqual(result.status, "INCONSISTENT_OBSERVERS")
        self.assertFalse(result.full_state_verified)

    def test_bad_budget_rejected(self):
        target = FiniteSystem((0, 1, 2))
        with self.assertRaises(ValueError):
            assess(target.equal_ends, target.step, max_full_state_calls=-1)


if __name__ == "__main__":
    unittest.main()
