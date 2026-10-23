"""Exact finite-state checks for the two-predecessor local rule schema."""
import unittest
from itertools import product

from work.arc_like_maze.marked_operator_system import MarkedObject
from work.arc_like_maze.root_transport import Process, ZERO, IDENTITY, NONLINEAR
from work.arc_like_maze.nondiagonal_transport import ShearedMarkedWorld
from work.arc_like_maze.two_predecessor_schema import (
    TwoPredecessorWorld, verify_conjugacy,
)


class TwoPredecessorSchemaTests(unittest.TestCase):
    BASES = (
        Process.repeat(ZERO),
        Process.repeat(IDENTITY),
        Process.repeat(NONLINEAR),
        Process.repeat(ZERO, IDENTITY, NONLINEAR),
    )

    def test_table_matches_direct_shear_for_every_state(self):
        for process in self.BASES:
            for gain in (1, 2):
                base = MarkedObject(process, gain)
                for coefficient in (0, 1, 2):
                    for depth in (3, 4, 5):
                        world = TwoPredecessorWorld(base, coefficient, depth)
                        direct = ShearedMarkedWorld(base, coefficient)
                        for state in product(range(3), repeat=depth):
                            for action in "AB":
                                self.assertEqual(
                                    world.step(state, action),
                                    direct.step(state, action),
                                    (process, gain, coefficient, depth, state, action),
                                )

    def test_native_process_is_embedded_at_zero_shear(self):
        for process in self.BASES:
            for gain in (1, 2):
                world = TwoPredecessorWorld(MarkedObject(process, gain), 0, 6)
                self.assertTrue(all(
                    world.is_native_one_input_rule(i) for i in range(2, 6)
                ))

    def test_nonzero_shear_has_exact_one_input_schema_obstruction(self):
        for process in self.BASES:
            for gain in (1, 2):
                for coefficient in (1, 2):
                    world = TwoPredecessorWorld(
                        MarkedObject(process, gain), coefficient, 3
                    )
                    # At right input x1=0, q_2(0,0)=c*g^2=c while
                    # q_2(2,0)=0. A function of x1 alone cannot do both.
                    self.assertEqual(world.increment(2, 0, 0), coefficient)
                    self.assertEqual(world.increment(2, 2, 0), 0)
                    self.assertFalse(world.is_native_one_input_rule(2))

    def test_two_input_conjugacy_holds_for_every_state(self):
        for process in self.BASES:
            for gain in (1, 2):
                base = MarkedObject(process, gain)
                for depth in (3, 4, 5):
                    worlds = [
                        TwoPredecessorWorld(base, coefficient, depth)
                        for coefficient in (0, 1, 2)
                    ]
                    for source in worlds:
                        for target in worlds:
                            self.assertTrue(verify_conjugacy(source, target))

    def test_wrong_depth_or_base_is_not_silently_compared(self):
        base = MarkedObject(Process.repeat(ZERO), 1)
        other = MarkedObject(Process.repeat(ZERO), 2)
        with self.assertRaises(ValueError):
            verify_conjugacy(
                TwoPredecessorWorld(base, 0, 3),
                TwoPredecessorWorld(base, 1, 4),
            )
        with self.assertRaises(ValueError):
            verify_conjugacy(
                TwoPredecessorWorld(base, 0, 3),
                TwoPredecessorWorld(other, 1, 3),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
