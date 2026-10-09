"""Construction-first A/B: nonlinear gauge closure vs a genuine new relation."""
from itertools import product
import unittest

from work.arc_like_maze.inverse_limit import TowerPoint
from work.arc_like_maze.math import World
from work.arc_like_maze.gauge_construction import (
    GaugedWorld, GaugedTower, SplitCouplingWorld, construct_boundary,
    fixed_B, gauge, gauge_alignment,
)


class GaugeConstructionTests(unittest.TestCase):
    def test_three_different_world_laws_return_under_the_same_rule(self):
        base = GaugedWorld(4)
        orbit = [base]
        for _ in range(3):
            orbit.append(orbit[-1].construct_next())
        self.assertEqual(orbit[3], orbit[0])
        self.assertEqual([w.coefficient for w in orbit], [0, 1, 2, 0])
        worlds_states = tuple(product(range(3), repeat=4))
        signatures = {
            tuple(w.step(state, "B") for state in worlds_states)
            for w in orbit[:3]
        }
        self.assertEqual(len(signatures), 3)

    def test_every_concrete_transition_is_conjugated_at_all_tested_depths(self):
        phi = (0, 1, 2)
        for depth in range(3, 7):
            worlds = tuple(GaugedWorld(depth, phi, c) for c in range(3))
            for state in product(range(3), repeat=depth):
                for action in "AB":
                    for before in worlds:
                        for after in worlds:
                            mapped = gauge_alignment(state, before.coefficient, after.coefficient)
                            self.assertEqual(
                                gauge_alignment(before.step(state, action),
                                                before.coefficient, after.coefficient),
                                after.step(mapped, action),
                            )

    def test_gauge_is_invertible_and_projectively_compatible(self):
        for depth in range(3, 8):
            for state in product(range(3), repeat=depth):
                for coefficient in range(3):
                    self.assertEqual(gauge(gauge(state, coefficient),
                                           (-coefficient) % 3), state)
                    if depth >= 4:
                        self.assertEqual(gauge(state, coefficient)[:-1],
                                         gauge(state[:-1], coefficient))

    def test_tower_construction_preserves_all_finite_prefix_alignments(self):
        seeds = (TowerPoint.zeros(), TowerPoint.finite_support((0, 1, 2, 1, 2, 0)))
        for base in seeds:
            for word in ("", "BBB", "ABABB", "BAAAB"):
                prior = base
                for action in word:
                    prior = prior.move(action)
                gauges = [GaugedTower(prior, coefficient) for coefficient in range(3)]
                for depth in range(3, 13):
                    for source in gauges:
                        for target in gauges:
                            self.assertEqual(
                                gauge_alignment(source.prefix(depth),
                                                source.coefficient, target.coefficient),
                                target.prefix(depth),
                            )
                            for action in "AB":
                                self.assertEqual(
                                    source.move(action).prefix(depth),
                                    GaugedWorld(depth, prior.phi, source.coefficient).step(
                                        source.prefix(depth), action),
                                )

    def test_parameter_variation_alone_does_not_claim_new_class(self):
        for depth in range(3, 7):
            original = GaugedWorld(depth, (0, 1, 2), 0)
            for c in (1, 2):
                variant = GaugedWorld(depth, (0, 1, 2), c)
                self.assertEqual(fixed_B(original), fixed_B(variant))

    def test_new_coupling_breaks_finite_projective_conjugacy_at_depth_four(self):
        before = GaugedWorld(4, (0, 1, 2), 0)
        after = SplitCouplingWorld(4, (0, 1, 2))
        self.assertEqual(fixed_B(before), 3)
        self.assertEqual(fixed_B(after), 6)
        self.assertEqual(construct_boundary().status, "NEW_RELATION_AT_DEPTH_FOUR")

    def test_obstruction_is_not_visible_at_depth_three(self):
        before = GaugedWorld(3)
        changed = SplitCouplingWorld(3)
        self.assertEqual(fixed_B(before), fixed_B(changed))
        for state in product(range(3), repeat=3):
            for action in "AB":
                self.assertEqual(before.step(state, action), changed.step(state, action))

    def test_split_coupling_projection_commutes_all_tested_dimensions(self):
        for depth in range(3, 7):
            higher = SplitCouplingWorld(depth + 1)
            lower = SplitCouplingWorld(depth)
            for state in product(range(3), repeat=depth + 1):
                for action in "AB":
                    self.assertEqual(higher.step(state, action)[:-1],
                                     lower.step(state[:-1], action))

    def test_split_rule_is_still_reversible_even_when_not_conjugate(self):
        for depth in range(3, 7):
            w = SplitCouplingWorld(depth)
            for state in product(range(3), repeat=depth):
                for action in "AB":
                    self.assertEqual(w.inverse(w.step(state, action), action), state)
                    self.assertEqual(w.step(w.inverse(state, action), action), state)

    def test_zero_phi_has_no_gauge_variation_but_split_still_breaks_relation(self):
        result = construct_boundary((0, 0, 0))
        self.assertEqual(result.status, "NEW_RELATION_AT_DEPTH_FOUR")
        self.assertFalse(result.three_concrete_B_rules)
        self.assertEqual((result.base_fixed_B, result.split_fixed_B), (9, 18))

    def test_bad_input_rejected(self):
        with self.assertRaises(ValueError):
            GaugedWorld(2)
        with self.assertRaises(ValueError):
            GaugedWorld(4, (0, 1, 2), 3)
        with self.assertRaises(ValueError):
            gauge((0, 0, 0, 0), -1)
        with self.assertRaises(ValueError):
            SplitCouplingWorld(4).inverse((0, 0, 0, 0), "Z")


if __name__ == "__main__":
    unittest.main(verbosity=2)
