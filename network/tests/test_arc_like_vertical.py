"""Cross-dimensional construction witnesses, projected loops, and alignments."""
import unittest

from work.arc_like_maze.math import World, inverse_candidates
from work.arc_like_maze.nonlinear import nonlinear_lifts
from work.arc_like_maze.vertical import (
    project, shortest_hidden_loop, verify_alignment_square, verify_extension,
)


class VerticalConstructionTests(unittest.TestCase):
    def test_projection_commutes_across_all_reachable_edges_depths_three_six(self):
        for depth in range(3, 7):
            for prototype in inverse_candidates():
                lower = World(depth, prototype.phi)
                upper = World(depth + 1, prototype.phi)
                witness = verify_extension(lower, upper)
                self.assertEqual(witness.commute_edges_checked, 2 * witness.upper_states)
                self.assertIsNone(witness.failure)
                self.assertEqual(witness.fiber_sizes,
                                 (1,) if prototype.phi == (0, 0, 0) else (3,))
                self.assertEqual(witness.upper_states,
                                 witness.lower_states * witness.fiber_sizes[0])

    def test_nonzero_fibers_grow_without_being_identical_worlds(self):
        sizes = []
        for depth in range(3, 7):
            witness = verify_extension(World(depth), World(depth + 1))
            self.assertEqual(witness.status, "PROJECTED_NOT_BIJECTIVE")
            sizes.append((witness.lower_states, witness.upper_states))
        self.assertEqual(sizes, [(27, 81), (81, 243), (243, 729), (729, 2187)])

    def test_zero_phi_extension_has_no_new_reachable_fiber(self):
        for depth in range(3, 7):
            witness = verify_extension(World(depth, (0, 0, 0)),
                                       World(depth + 1, (0, 0, 0)))
            self.assertEqual((witness.status, witness.fiber_sizes),
                             ("TRIVIAL_FIBER", (1,)))

    def test_hidden_fiber_loop_repeats_three_times_with_different_states(self):
        for depth in range(3, 7):
            loop = shortest_hidden_loop(World(depth + 1))
            self.assertEqual(loop.status, "THREE_TURN_FIBER_LOOP")
            self.assertEqual(loop.after_three, loop.start)
            self.assertEqual(len({loop.start, loop.after_one, loop.after_two}), 3)
            self.assertEqual(project(loop.start), project(loop.after_one))
            self.assertEqual(project(loop.start), project(loop.after_two))

    def test_specific_depth_three_fiber_witness_is_BBB(self):
        witness = shortest_hidden_loop(World(4))
        self.assertEqual(witness.action_word, "BBB")
        self.assertEqual(witness.after_one, (0, 0, 0, 1))
        self.assertEqual(witness.after_two, (0, 0, 0, 2))

    def test_zero_phi_has_no_hidden_loop(self):
        for depth in range(4, 7):
            loop = shortest_hidden_loop(World(depth, (0, 0, 0)))
            self.assertEqual(loop.status, "TRIVIAL_FIBER")
            self.assertEqual(loop.after_one, loop.start)

    def test_alignment_squares_for_scaling_pairs_across_depth(self):
        for depth in range(3, 7):
            for phi in ((0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2)):
                other = tuple((2 * val) % 3 for val in phi)
                square = verify_alignment_square(World(depth, phi), World(depth, other))
                self.assertEqual(square.status, "COMMUTING_SQUARE")

    def test_inequivalent_base_cannot_falsely_complete_square(self):
        result = verify_alignment_square(World(3, (0, 1, 0)), World(3, (0, 1, 1)))
        self.assertEqual(result.status, "OPEN")

    def test_hidden_loops_for_all_eight_nonzero_constructed_relations(self):
        for depth in range(3, 7):
            for prototype in inverse_candidates():
                if prototype.phi == (0, 0, 0):
                    continue
                result = shortest_hidden_loop(World(depth + 1, prototype.phi))
                self.assertEqual(result.status, "THREE_TURN_FIBER_LOOP")

    def test_all_384_parameter_constructors_commute_with_depth_extension(self):
        for operation in nonlinear_lifts():
            for prototype in inverse_candidates():
                for depth in range(3, 7):
                    lower = World(depth, prototype.phi)
                    before_extend = World(depth + 1, operation(lower).phi)
                    after_extend = operation(World(depth + 1, lower.phi))
                    self.assertEqual(before_extend, after_extend)

    def test_invalid_projection_and_extension_remain_unknown(self):
        with self.assertRaises(ValueError):
            project((0, 0))
        w = verify_extension(World(3), World(5))
        self.assertEqual(w.status, "UNKNOWN")


if __name__ == '__main__':
    unittest.main(verbosity=2)
