"""A/B witnesses across a non-diagonal coordinate change of marked worlds."""
import unittest
from itertools import product

from work.arc_like_maze.marked_operator_system import (
    BoundaryGauge, MarkedArrow, MarkedObject, same_arrow,
)
from work.arc_like_maze.root_transport import (
    Process, ZERO, IDENTITY, NONLINEAR, find,
)
from work.arc_like_maze.nondiagonal_transport import (
    shear, ShearedMarkedWorld, ShearedMarkedArrow,
    same_sheared_arrow, shear_interchange, certify_shear,
)


class NonDiagonalTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Process.repeat(ZERO, (0, 0, 1))
        q = Process.repeat(ZERO, (0, 1, 0))
        cls.base = MarkedArrow(
            MarkedObject(p, 1), MarkedObject(q, 1), find(p, q))
        cls.arrow = ShearedMarkedArrow(cls.base, 1, 2)

    def test_three_concrete_world_laws_close_after_three_constructions(self):
        source = MarkedObject(Process.repeat(ZERO), 1)
        worlds = [ShearedMarkedWorld(source, 0)]
        for _ in range(3):
            worlds.append(worlds[-1].construct_next())
        self.assertEqual(worlds[3], worlds[0])
        self.assertEqual([w.coefficient for w in worlds], [0, 1, 2, 0])
        self.assertEqual(
            [w.step((0, 0, 0), "B") for w in worlds],
            [(0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 1, 0)])

    def test_shear_is_invertible_and_projection_compatible(self):
        for depth in range(3, 8):
            for state in product(range(3), repeat=depth):
                for coefficient in (0, 1, 2):
                    self.assertEqual(shear(shear(state, coefficient),
                                           (-coefficient) % 3), state)
                    if depth >= 4:
                        self.assertEqual(
                            shear(state, coefficient)[:-1],
                            shear(state[:-1], coefficient))

    def test_all_states_and_B_actions_conjugate_across_three_shears(self):
        p = MarkedObject(Process.repeat(IDENTITY, NONLINEAR), 1)
        for depth in range(3, 7):
            worlds = [ShearedMarkedWorld(p, c) for c in (0, 1, 2)]
            for state in product(range(3), repeat=depth):
                for operation in "AB":
                    for source in range(3):
                        for target in range(3):
                            scale = (target - source) % 3
                            self.assertEqual(
                                shear(worlds[source].step(state, operation), scale),
                                worlds[target].step(shear(state, scale), operation))

    def test_new_B_relation_cannot_be_encoded_as_any_native_process(self):
        # For EVERY existing Process rule, P_0(0)=0. Consequently native
        # B(origin) changes x1 but NEVER x2. The shear violates this.
        for table in (ZERO, IDENTITY, NONLINEAR, (0, 0, 1)):
            for gain in (1, 2):
                base = MarkedObject(Process.repeat(table), gain)
                origin = (0, 0, 0)
                self.assertEqual(base.world().step(origin, "B")[2], 0)
                for c in (1, 2):
                    self.assertEqual(
                        ShearedMarkedWorld(base, c).step(origin, "B")[2], c)
        # Schema failure is not evidence of A/B inequivalence:
        self.assertEqual(certify_shear().status,
                         "CLOSED_SHEAR_CONJUGACY_OUTSIDE_NATIVE_PROCESS_SCHEMA")

    def test_conjugate_sheared_laws_are_reversible_on_all_states(self):
        for depth in range(3, 7):
            world = ShearedMarkedWorld(
                MarkedObject(Process.repeat(IDENTITY, ZERO), 2), 2)
            for state in product(range(3), repeat=depth):
                for operation in "AB":
                    self.assertEqual(world.inverse(world.step(state, operation),
                                                   operation), state)
                    self.assertEqual(world.step(world.inverse(state, operation),
                                                operation), state)

    def test_full_marked_arrow_survives_non_diagonal_transport(self):
        for depth in range(3, 8):
            self.assertTrue(self.arrow.verify_depth(depth))
            for state in product(range(3), repeat=depth):
                aligned = self.arrow.map_state(state)
                self.assertEqual(
                    self.arrow.inverse().map_state(aligned), state)

    def test_sheared_arrow_composition_and_inverse_retain_witness(self):
        inverted = self.arrow.inverse()
        composed = self.arrow.compose(inverted)
        for depth in range(3, 7):
            self.assertTrue(composed.verify_depth(depth))
            for state in product(range(3), repeat=depth):
                self.assertEqual(composed.map_state(state), state)
        self.assertEqual(composed.source, composed.target)
        with self.assertRaises(ValueError):
            self.arrow.compose(self.arrow)

    def test_marked_shift_preserves_exact_sheared_witness(self):
        for turns in (0, 1, 2, 4, 7):
            shifted = self.arrow.shift(turns)
            for depth in range(3, 7):
                self.assertTrue(shifted.verify_depth(depth))
            # No arbitrary witness re-solve or loss of its root mark.
            self.assertEqual(shifted.base.witness.incoming,
                             self.base.witness.incoming if turns == 0
                             else self.base.witness.scale(turns - 1))
            for i in range(18):
                self.assertEqual(shifted.base.witness.scale(i),
                                 self.base.witness.scale(turns + i))

    def test_diagonal_gauge_and_shift_commute_in_sheared_frame(self):
        gauges = (
            BoundaryGauge(1, (1, 2)),
            BoundaryGauge(2, (2, 1)),
            BoundaryGauge(2, (1, 1)),
        )
        for source in gauges:
            for target in gauges:
                for turns in (0, 1, 2, 3, 5):
                    self.assertTrue(shear_interchange(
                        self.arrow, source, target, turns))

    def test_zero_rule_ambiguous_witness_is_preserved_not_rediscovered(self):
        p = Process.repeat(ZERO)
        from work.arc_like_maze.root_transport import Witness
        explicit = Witness("ALIGNED", 2, (1, 2), (2, 1))
        base = MarkedArrow(
            MarkedObject(p, 1), MarkedObject(p, 2), explicit)
        arrow = ShearedMarkedArrow(base, 2, 1)
        for turns in range(6):
            shifted = arrow.shift(turns)
            self.assertEqual(shifted.base.witness.incoming,
                             explicit.incoming if turns == 0
                             else explicit.scale(turns - 1))
            for i in range(15):
                self.assertEqual(shifted.base.witness.scale(i),
                                 explicit.scale(turns + i))
            self.assertTrue(shifted.verify_depth(4))

    def test_mathematical_certificate_counts_every_finite_edge(self):
        certificate = certify_shear()
        self.assertEqual(
            (certificate.distinct_depth_three_rules,
             certificate.group_order,
             certificate.native_representation_breaks,
             certificate.alignment_edges_checked),
            (3, 3, 2, 27 * 2 * 9))
        self.assertIsNone(certificate.failure)

    def test_bad_coordinates_and_operations_are_rejected(self):
        with self.assertRaises(ValueError):
            shear((0, 0), 1)
        with self.assertRaises(ValueError):
            shear((0, 0, 0), 3)
        with self.assertRaises(ValueError):
            ShearedMarkedWorld(self.base.source, -1)
        with self.assertRaises(ValueError):
            ShearedMarkedArrow(self.base, 1, 3)
        with self.assertRaises(ValueError):
            self.arrow.verify_depth(2)
        with self.assertRaises(ValueError):
            self.arrow.source.step((0, 0, 0), "C")


if __name__ == "__main__":
    unittest.main(verbosity=2)
