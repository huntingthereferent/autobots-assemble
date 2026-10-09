"""Exact nonlinear construction quotient; no native ARC or game-layer claims."""
import unittest
from itertools import permutations

from work.arc_like_maze.affine_scan import scan_affine
from work.arc_like_maze.alignment import discover_alignment, equivalent_classes
from work.arc_like_maze.math import World, inverse_candidates
from work.arc_like_maze.nonlinear import (
    ConstructionMap, certify_nonlinear_group, class_action, collapse_to_zero,
    compose, nonlinear_lifts, pair_flip,
)


class NonlinearConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = inverse_candidates()
        cls.groups = equivalent_classes(cls.worlds)
        cls.maps = nonlinear_lifts()
        cls.keys = {operator.images for operator in cls.maps}
        cls.cert = certify_nonlinear_group()

    def test_five_classes_and_384_reversible_constructors(self):
        self.assertEqual(tuple(map(len, self.groups)), (1, 2, 2, 2, 2))
        self.assertEqual(len(self.maps), 384)
        self.assertEqual(len(self.keys), 384)
        self.assertTrue(all(operator.bijective for operator in self.maps))

    def test_exhaustive_independent_9_factorial_bijection_count(self):
        """Enumerate all 362,880 bijections, independently of the generator."""
        indices = {world: i for i, world in enumerate(self.worlds)}
        group_indices = tuple(tuple(indices[w] for w in group) for group in self.groups)
        class_of = {indices[w]: j for j, group in enumerate(self.groups) for w in group}
        compatible = set()
        for mapping in permutations(range(9)):
            if all(len({class_of[mapping[k]] for k in group}) == 1
                   for group in group_indices):
                compatible.add(mapping)
        self.assertEqual(len(compatible), 384)
        self.assertEqual(compatible, self.keys)

    def test_all_384_constructors_preserve_A_B_alignment(self):
        for operator in self.maps:
            self.assertIsNotNone(class_action(operator, self.groups))
            for pair in self.groups[1:]:
                self.assertTrue(
                    discover_alignment(operator(pair[0]), operator(pair[1])).aligned
                )

    def test_maximal_closed_group_including_nonlinear(self):
        result = self.cert
        self.assertEqual(result.status, "CLOSED_FOR_NINE_WORLD_NONLINEAR_BIJECTIONS")
        self.assertEqual((result.reversible, result.affine, result.nonlinear), (384, 48, 336))
        self.assertEqual((result.quotient_actions, result.lifts_per_action,
                          result.composition_checked), (24, 16, 384 * 384))
        self.assertIsNone(result.failure)

    def test_one_pair_flip_is_nonlinear_involution(self):
        operator = pair_flip()
        self.assertNotEqual(operator.images, tuple(range(9)))
        affine = {
            tuple(self.worlds.index(other(w)) for w in self.worlds)
            for other in scan_affine().accepted
        }
        self.assertNotIn(operator.images, affine)
        self.assertEqual(compose(operator, operator).images, tuple(range(9)))
        self.assertEqual(class_action(operator, self.groups), tuple(range(5)))

    def test_nonlinear_class_four_cycle(self):
        target = (0, 2, 3, 4, 1)
        operator = next(
            operator for operator in self.maps
            if class_action(operator, self.groups) == target
        )
        current = self.groups[1][0]
        class_of = {world: i for i, group in enumerate(self.groups) for world in group}
        observed = [class_of[current]]
        for _ in range(4):
            current = operator(current)
            observed.append(class_of[current])
        self.assertEqual(observed, [1, 2, 3, 4, 1])
        self.assertEqual(current, self.groups[1][0])

    def test_sink_preserves_quotient_but_is_not_reversible_loop(self):
        sink = collapse_to_zero()
        self.assertIsNotNone(class_action(sink, self.groups))
        self.assertFalse(sink.bijective)
        self.assertFalse(self.cert.sink_is_loop)
        self.assertEqual(sink(self.groups[2][0]), self.groups[0][0])

    def test_translation_breaks_previous_equivalence(self):
        a, b = self.groups[2]

        def translate(world):
            x, y = world.phi[1:]
            return World(3, (0, (x + 1) % 3, y))

        self.assertTrue(discover_alignment(a, b).aligned)
        self.assertFalse(discover_alignment(translate(a), translate(b)).aligned)

    def test_depth_three_through_six_preserves_partition_shape(self):
        for depth in range(3, 7):
            family = tuple(World(depth, world.phi) for world in self.worlds)
            groups = equivalent_classes(family)
            self.assertEqual(tuple(map(len, groups)), (1, 2, 2, 2, 2))
            operation = pair_flip()
            self.assertTrue(all(
                discover_alignment(operation(pair[0]), operation(pair[1])).aligned
                for pair in groups if len(pair) == 2
            ))
        # A cross-depth bijection is *not* established by matching partitions.
        self.assertEqual(discover_alignment(World(3), World(4)).status, "OPEN")

    def test_invalid_and_out_of_family_inputs_rejected(self):
        with self.assertRaises(ValueError):
            ConstructionMap("bad", (0,) * 8)
        with self.assertRaises(ValueError):
            ConstructionMap("", tuple(range(9)))
        with self.assertRaises(ValueError):
            pair_flip()(World(2))
        with self.assertRaises(ValueError):
            pair_flip()(World(3, (1, 1, 2)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
