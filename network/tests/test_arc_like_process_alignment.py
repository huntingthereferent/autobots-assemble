"""Coinductive process-level A/B closure; never infer global closure from prefixes."""
import unittest
from dataclasses import replace
from itertools import product

from work.arc_like_maze.process_alignment import (
    CoinductiveAlignment, IDENTITY, NEGATIVE, NONLINEAR, ZERO,
    PeriodicProcess, compare_shift, find_process_alignment, next_scales, verify_lasso,
)


class ProcessAlignmentTests(unittest.TestCase):
    def test_nonidentical_construction_turns_are_equivalent_for_all_depths(self):
        original = PeriodicProcess.repeat(IDENTITY, NEGATIVE)
        shifted = original.shift(1)
        self.assertNotEqual(original.rule(0), shifted.rule(0))
        certificate = compare_shift(original)
        self.assertEqual(certificate.status, "COINDUCTIVE_DIAGONAL_ALIGNMENT")
        self.assertTrue(verify_lasso(original, shifted, certificate))
        self.assertEqual([certificate.scale(i) for i in range(8)],
                         [2, 1, 2, 1, 2, 1, 2, 1])
        # Exhaustively check full state spaces rather than the rooted orbit.
        for depth in range(3, 8):
            for state in product(range(3), repeat=depth):
                mapped = certificate.map_state(state)
                for action in "AB":
                    self.assertEqual(
                        certificate.map_state(original.step(state, action)),
                        shifted.step(mapped, action),
                    )
                if depth > 3:
                    self.assertEqual(
                        certificate.map_state(state)[:-1],
                        certificate.map_state(state[:-1]),
                    )

    def test_actual_rule_by_rule_alignment_not_just_matching_counts(self):
        before = PeriodicProcess.repeat(IDENTITY)
        after = PeriodicProcess((IDENTITY,), (NEGATIVE,))
        witness = find_process_alignment(before, after)
        self.assertEqual(witness.status, "COINDUCTIVE_DIAGONAL_ALIGNMENT")
        self.assertEqual(witness.scale(0), 1)
        self.assertEqual(witness.scale(1), 2)
        self.assertEqual(witness.scale(2), 1)
        self.assertTrue(verify_lasso(before, after, witness))

    def test_different_nonzero_rule_shape_breaks_shift_alignment(self):
        construction = PeriodicProcess.repeat(IDENTITY, NONLINEAR)
        broken = compare_shift(construction)
        self.assertEqual(broken.status, "OPEN_DIAGONAL_ALIGNMENT")
        self.assertEqual(broken.first_impossible_depth, 3)
        self.assertFalse(verify_lasso(construction, construction.shift(1), broken))

    def test_no_finite_prefix_proves_future_alignment(self):
        late = 75
        left = PeriodicProcess.repeat(IDENTITY)
        right = PeriodicProcess((IDENTITY,) * late, (NONLINEAR,))
        witness = find_process_alignment(left, right)
        self.assertEqual(witness.status, "OPEN_DIAGONAL_ALIGNMENT")
        self.assertEqual(witness.first_impossible_depth, late + 3)
        for index in range(late):
            self.assertEqual(left.rule(index), right.rule(index))
        self.assertNotEqual(left.rule(late), right.rule(late))

    def test_periodic_greatest_fixed_point_find_or_reject_loop(self):
        a = PeriodicProcess((IDENTITY,), (NEGATIVE, IDENTITY, NEGATIVE))
        b = PeriodicProcess((IDENTITY,), (IDENTITY, NEGATIVE))
        result = find_process_alignment(a, b)
        self.assertEqual(result.status, "COINDUCTIVE_DIAGONAL_ALIGNMENT")
        self.assertTrue(verify_lasso(a, b, result))
        self.assertGreaterEqual(result.checked_phase_states, 2)

    def test_zero_rule_has_underdetermined_but_valid_scaling(self):
        a = PeriodicProcess.repeat(ZERO, ZERO)
        b = PeriodicProcess.repeat(ZERO)
        result = find_process_alignment(a, b)
        self.assertEqual(result.status, "COINDUCTIVE_DIAGONAL_ALIGNMENT")
        self.assertTrue(verify_lasso(a, b, result))
        self.assertTrue(all(result.scale(i) in (1, 2) for i in range(30)))

    def test_zero_to_nonzero_rule_is_not_even_diagonally_aligned(self):
        before = PeriodicProcess.repeat(ZERO)
        after = PeriodicProcess.repeat(IDENTITY)
        result = find_process_alignment(before, after)
        self.assertEqual(result.status, "OPEN_DIAGONAL_ALIGNMENT")
        self.assertEqual(result.first_impossible_depth, 3)
        # Stronger full-state B-fixed-set invariant, not just this search.
        def count_fixed(process):
            return sum(process.step(s, "B") == s
                       for s in product(range(3), repeat=3))
        self.assertEqual((count_fixed(before), count_fixed(after)), (9, 3))

    def test_delayed_mismatch_works_even_after_periodic_phase(self):
        # Many matching turns cannot hide a later structurally incompatible rule.
        a = PeriodicProcess((IDENTITY, NEGATIVE), (IDENTITY, NEGATIVE))
        b = PeriodicProcess((IDENTITY, NEGATIVE), (IDENTITY, NONLINEAR))
        result = find_process_alignment(a, b)
        self.assertEqual(result.status, "OPEN_DIAGONAL_ALIGNMENT")
        self.assertEqual(result.first_impossible_depth, 6)

    def test_shift_then_shift_two_is_same_process_blueprint(self):
        process = PeriodicProcess((IDENTITY,), (IDENTITY, NEGATIVE, IDENTITY))
        self.assertEqual(process.shift(1).shift(13), process.shift(14))
        self.assertEqual(process.shift(3).rule(0), process.rule(3))
        for k in range(1, 18):
            for offset in range(9):
                self.assertEqual(process.shift(k).rule(offset), process.rule(k + offset))

    def test_malformed_witness_rejected_without_claiming_closure(self):
        a = PeriodicProcess.repeat(IDENTITY, NEGATIVE)
        b = a.shift(1)
        good = find_process_alignment(a, b)
        invalid = replace(good, head=(1,), period=(1,))
        self.assertFalse(verify_lasso(a, b, invalid))
        with self.assertRaises(ValueError):
            CoinductiveAlignment("OPEN_DIAGONAL_ALIGNMENT").scale(0)

    def test_invalid_input_contract(self):
        with self.assertRaises(ValueError):
            PeriodicProcess.repeat()
        with self.assertRaises(ValueError):
            PeriodicProcess.repeat((1, 1, 1))
        with self.assertRaises(ValueError):
            PeriodicProcess.repeat(IDENTITY).shift(-1)
        with self.assertRaises(ValueError):
            PeriodicProcess.repeat(IDENTITY).rule(-1)
        with self.assertRaises(ValueError):
            next_scales(IDENTITY, IDENTITY, 0)
        with self.assertRaises(ValueError):
            PeriodicProcess.repeat(IDENTITY).step((0, 0, 0), "C")


if __name__ == "__main__":
    unittest.main(verbosity=2)
