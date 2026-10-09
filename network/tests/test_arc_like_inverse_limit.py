"""Inverse-limit witnesses distinguish coherent recursion from exact cycle closure."""
import unittest

from work.arc_like_maze.alignment import discover_alignment
from work.arc_like_maze.math import World, inverse_candidates
from work.arc_like_maze.inverse_limit import (
    TowerPoint, align_point, alignment_scalar, audit_prefixes, check_phi,
    prefix_inverse, step_prefix, tower_class,
)


class InverseLimitTests(unittest.TestCase):
    def test_full_prefix_tower_and_actions_commute_with_every_tested_projection(self):
        seeds = (TowerPoint.zeros(), TowerPoint.finite_support((2, 1, 2, 0, 1)))
        for seed in seeds:
            for word in ("", "ABBABA", "BBB", "BAABBAA"):
                point = seed
                for action in word:
                    point = point.move(action)
                for depth in range(3, 11):
                    self.assertEqual(point.prefix(depth + 1)[:-1], point.prefix(depth))
                    for action in "AB":
                        self.assertEqual(
                            point.move(action).prefix(depth),
                            World(depth, seed.phi).step(point.prefix(depth), action),
                        )

    def test_inverse_A_B_are_exact_at_each_finite_depth(self):
        for phi in ((0, 0, 0), (0, 1, 2), (0, 2, 1), (0, 1, 1)):
            for depth in range(3, 9):
                for state in (tuple(range(depth)), tuple((2 * i + 1) % 3 for i in range(depth))):
                    finite = tuple(v % 3 for v in state)
                    for forward, backward in (("A", "a"), ("B", "b")):
                        advanced = step_prefix(finite, phi, forward)
                        self.assertEqual(step_prefix(advanced, phi, backward), finite)
                        self.assertEqual(step_prefix(step_prefix(finite, phi, backward), phi, forward), finite)

    def test_infinite_point_reverses_actions_in_every_tested_prefix(self):
        seed = TowerPoint.finite_support((1, 2, 0, 2, 1))
        for forward, backward in (("A", "a"), ("B", "b")):
            moved = seed.move(forward).move(backward)
            for depth in range(3, 12):
                self.assertEqual(seed.prefix(depth), moved.prefix(depth))

    def test_false_BBB_cycle_is_broken_by_next_dimension(self):
        zero = TowerPoint.zeros()
        moved = zero.move("B").move("B").move("B")
        self.assertEqual(zero.prefix(3), moved.prefix(3))
        self.assertNotEqual(zero.prefix(4), moved.prefix(4))
        result = audit_prefixes(deepest=9, word="BBB")
        self.assertEqual(result.status, "FINITE_PREFIX_VERIFIED")
        self.assertEqual((result.false_closure_depth, result.break_depth), (3, 4))
        self.assertGreater(result.commuting_edges, 0)

    def test_finite_agreement_never_proves_infinite_equality(self):
        left = TowerPoint.zeros()
        right = TowerPoint((0, 1, 2), lambda index: 1 if index == 13 else 0)
        self.assertTrue(left.agree_through(right, 13))
        self.assertFalse(left.agree_through(right, 14))

    def test_exact_all_depth_scaling_construction_equivalence(self):
        phi = (0, 1, 2)
        target = (0, 2, 1)
        self.assertEqual(alignment_scalar(phi, target), 2)
        seed = TowerPoint.finite_support((1, 1, 2, 1, 0), phi)
        for word in ("", "BBAAB", "BAAABBaB"):
            point = seed
            for action in word:
                point = point.move(action)
            aligned = align_point(point, target)
            for depth in range(3, 12):
                before = point.prefix(depth)
                expected = before[:2] + tuple((2 * val) % 3 for val in before[2:])
                self.assertEqual(aligned.prefix(depth), expected)
                self.assertEqual(aligned.prefix(depth + 1)[:-1], aligned.prefix(depth))

    def test_projective_classes_are_exactly_five_under_scaling(self):
        families = inverse_candidates()
        groups = {}
        for world in families:
            groups.setdefault(tower_class(world.phi), []).append(world)
        self.assertEqual(sorted(map(len, groups.values())), [1, 2, 2, 2, 2])
        for members in groups.values():
            for left in members:
                for right in members:
                    self.assertIsNotNone(alignment_scalar(left.phi, right.phi))
                    self.assertTrue(discover_alignment(left, right).aligned)

    def test_incompatible_towers_have_depth_three_counterexample(self):
        left, right = (0, 1, 2), (0, 1, 1)
        self.assertIsNone(alignment_scalar(left, right))
        base = discover_alignment(World(3, left), World(3, right))
        self.assertEqual(base.status, "OPEN")
        self.assertIsNotNone(base.conflicting_words)
        with self.assertRaises(ValueError):
            align_point(TowerPoint.zeros(left), right)

    def test_constant_orbit_reachable_is_not_the_full_inverse_limit(self):
        phi = (0, 0, 0)
        self.assertEqual(len(World(6, phi).reachable()), 9)
        self.assertEqual(3**6, 729)
        # Full inverse limit contains points that are not in the orbit of zero.
        alien = TowerPoint.finite_support((0, 0, 0, 0, 0, 1), phi)
        self.assertNotIn(alien.prefix(6), World(6, phi).reachable())

    def test_nonbreak_prefix_result_does_not_claim_global_closure(self):
        result = audit_prefixes((0, 0, 0), deepest=8, word="BBB")
        self.assertEqual(result.status, "FINITE_PREFIX_VERIFIED")
        self.assertIsNone(result.break_depth)
        self.assertIsNone(result.false_closure_depth)

    def test_unsupported_infinite_data_is_not_silently_admitted(self):
        with self.assertRaises(ValueError):
            check_phi((1, 1, 2))
        with self.assertRaises(ValueError):
            TowerPoint.zeros().move("C")
        with self.assertRaises(ValueError):
            TowerPoint((0, 1, 2), lambda i: 4).prefix(3)
        with self.assertRaises(ValueError):
            TowerPoint.zeros().prefix(2)
        with self.assertRaises(ValueError):
            prefix_inverse((0, 0, 0), (0, 1, 2), "X")
        self.assertEqual(audit_prefixes(deepest=2).status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
