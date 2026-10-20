"""Reproducible tests for the local Engine 2 bounded Boundary Math experiment."""
from collections import Counter
from itertools import product
import unittest
from engine_two_boundary_experiment import (
    Engine2Embryo, CouplingLaw, RULES, ZERO, IDENTITY,
)


class EngineTwoBoundaryMathTests(unittest.TestCase):
    def test_exhaustive_research_spaces(self):
        engine = Engine2Embryo()
        results = [engine.construct_and_classify(n) for n in (1, 2, 3, 4)]
        self.assertEqual([s.descriptions for s in results], [9, 81, 729, 6561])
        self.assertEqual([s.rooted_classes for s in results], [5, 21, 85, 341])
        self.assertEqual([s.distribution for s in results], [
            ((1, 1), (2, 4)),
            ((2, 4), (4, 16), (9, 1)),
            ((4, 16), (8, 64), (18, 4), (81, 1)),
            ((8, 64), (16, 256), (36, 16), (162, 4), (729, 1)),
        ])
        for s in results:
            self.assertEqual(sum(size * count for size, count in s.distribution), s.descriptions)

    def test_boundary_earned_from_full_state_transition_membership(self):
        e = Engine2Embryo()
        witness = e.watch_rule_change((IDENTITY,), ZERO, IDENTITY)
        self.assertEqual(witness.status, 'BOUNDARY')
        self.assertEqual((witness.before_count, witness.after_count,
                          len(witness.lost), len(witness.gained), len(witness.surviving)),
                         (9, 3, 6, 0, 3))
        self.assertEqual(len(witness.unresolved_before), 0)
        self.assertEqual(witness.delta_s, -6)
        self.assertEqual(witness.correspondence, tuple((x, x) for x in witness.surviving))
        self.assertTrue(any("does not establish A/B conjugacy" in o for o in witness.omissions))
        self.assertEqual(witness.comparison_rule, 'native exact B transition and state-set membership')
        a, b = CouplingLaw(witness.source_rules), CouplingLaw(witness.target_rules)
        for state in witness.lost:
            self.assertEqual(a.step(state, 'B'), state)
            self.assertNotEqual(b.step(state, 'B'), state)

    def test_mathematical_result_can_be_reentered_without_builder(self):
        e = Engine2Embryo()
        first = e.watch_rule_change((IDENTITY,))
        second = e.follow_witness_into_next_space(0)
        third = e.follow_witness_into_next_space(1)
        fourth = e.follow_witness_into_next_space(2)
        self.assertEqual([len(w.source_rules) for w in e.witnesses], [2, 3, 4, 5])
        self.assertEqual([w.parent_witness for w in e.witnesses], [None, 0, 1, 2])
        self.assertTrue(all(w.status == 'BOUNDARY' for w in e.witnesses))
        self.assertEqual(len(e.witnesses), 4)
        self.assertEqual(fourth.target_rules[:4], third.target_rules)

    def test_shape_of_rooted_space_can_hide_full_state_boundary(self):
        dormant = CouplingLaw((ZERO, ZERO))
        active = CouplingLaw((ZERO, IDENTITY))
        self.assertEqual(dormant.rooted_signature(), active.rooted_signature())
        self.assertNotEqual(dormant.count_fixed_B(), active.count_fixed_B())
        w = Engine2Embryo().watch_rule_change((ZERO,), ZERO, IDENTITY)
        self.assertEqual((w.before_count, w.after_count, len(w.lost)), (27, 9, 18))
        self.assertEqual(w.status, 'BOUNDARY')

    def test_earned_zero_does_not_mean_globally_identical_laws(self):
        e = Engine2Embryo()
        w = e.watch_rule_change((IDENTITY,), IDENTITY, (0, 2, 1))
        self.assertEqual(w.status, 'EARNED_ZERO_FOR_FIXED_B_WATCH')
        self.assertEqual(w.before_count, w.after_count)
        self.assertEqual(w.delta_s, 0)
        self.assertNotEqual(w.source_rules, w.target_rules)
        self.assertEqual(w.lost, ())
        self.assertEqual(w.gained, ())
        a, b = CouplingLaw(w.source_rules), CouplingLaw(w.target_rules)
        self.assertTrue(any(a.step(x, 'B') != b.step(x, 'B')
                            for x in product(range(3), repeat=a.depth)))

    def test_evidence_unknown_and_budget_walls_are_not_invented(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            Engine2Embryo(maximum_full_space=80).construct_and_classify(2)
        with self.assertRaisesRegex(ValueError, 'width 1..4'):
            Engine2Embryo().construct_and_classify(5)
        e = Engine2Embryo()
        with self.assertRaisesRegex(ValueError, 'witness does not exist'):
            e.follow_witness_into_next_space(42)
        with self.assertRaises(ValueError):
            e.watch_rule_change((IDENTITY,), (0, 0, 3), IDENTITY)

    def test_all_native_A_and_B_have_valid_exact_inverses(self):
        for rs in product(RULES, repeat=2):
            w = CouplingLaw(tuple(rs))
            for state in product(range(3), repeat=w.depth):
                for gen in 'AB':
                    self.assertEqual(w.inverse(w.step(state, gen), gen), state)

    def test_no_unearned_cross_grammar_equivalence(self):
        # An origin-preserving projection is NOT a full-space isomorphism.
        e = Engine2Embryo()
        result = e.watch_rule_change((IDENTITY,))
        self.assertIn('fixed-state membership', result.watch)
        self.assertNotIn('conjugacy', result.comparison_rule)
        self.assertEqual(result.source_rules[:-1], result.target_rules[:-1])

if __name__ == '__main__':
    unittest.main(verbosity=2)