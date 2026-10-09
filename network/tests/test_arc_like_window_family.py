"""Four complete full-state relational classes in twelve two-input A/B worlds.

Tests work from the independently declared q0 table plus the existing
window_two interpreter. The exhaustive checks here validate bounded depths;
explicit shear conjugacy and fixed-point formula justify the all-depth claim.
"""
import unittest
from itertools import product

from work.arc_like_maze.window_family import (
    ClassifiedWindow, ZERO_WINDOW, family, scalar_invariant,
    classify_pair, certify_family,
)
from work.arc_like_maze.window_two import compile_native, compile_shear
from work.arc_like_maze.nondiagonal_transport import shear
from work.arc_like_maze.marked_operator_system import MarkedObject
from work.arc_like_maze.root_transport import Process, ZERO


class WindowFamilyTests(unittest.TestCase):
    def test_twelve_distinct_transition_laws(self):
        worlds = family()
        self.assertEqual(len(worlds), 12)
        self.assertEqual(len(set(worlds)), 12)
        signatures = {
            tuple(world.step(state, "B")
                  for state in product(range(3), repeat=3))
            for world in worlds
        }
        self.assertEqual(len(signatures), 12)

    def test_exact_four_full_state_classes(self):
        certificate = certify_family()
        self.assertEqual(
            certificate.status,
            "CLOSED_DECLARED_SHEAR_ORBITS_WITH_FOUR_FULL_STATE_CLASSES",
        )
        self.assertEqual((certificate.concrete_worlds, certificate.full_state_classes),
                         (12, 4))
        self.assertEqual(certificate.class_sizes, (3, 3, 3, 3))
        self.assertEqual(certificate.fixed_B_by_class, (9, 6, 3, 0))
        self.assertEqual((certificate.aligned_ordered_pairs,
                          certificate.obstructed_ordered_pairs), (36, 108))
        self.assertEqual(certificate.first_obstruction_depth, 3)

    def test_full_state_B_fixed_invariant_exact_at_each_depth(self):
        for world in family():
            for depth in range(3, 7):
                self.assertEqual(world.fixed_B(depth),
                                 scalar_invariant(depth, world.support))
                self.assertEqual(world.fixed_B(depth),
                                 (3 - world.support) * 3 ** (depth - 2))

    def test_all_pairwise_conjugacies_or_concrete_obstructions(self):
        for source in family():
            for target in family():
                relation = classify_pair(source, target)
                if source.support != target.support:
                    self.assertEqual(relation.status,
                                     "INEQUIVALENT_FIXED_B_AT_DEPTH_THREE")
                    self.assertNotEqual(relation.source_B_fixed,
                                        relation.target_B_fixed)
                    self.assertEqual(relation.obstruction_depth, 3)
                    with self.assertRaises(ValueError):
                        relation.map_state((0, 0, 0))
                else:
                    self.assertEqual(relation.status,
                                     "ALL_DEPTH_FULL_STATE_CONJUGACY")
                    self.assertEqual(relation.witness_shear,
                                     (target.coefficient-source.coefficient) % 3)
                    for depth in range(3, 7):
                        for state in product(range(3), repeat=depth):
                            image = relation.map_state(state)
                            for action in "AB":
                                self.assertEqual(
                                    relation.map_state(source.step(state, action)),
                                    target.step(image, action))

    def test_every_transition_has_an_exact_inverse(self):
        for world in family():
            for depth in range(3, 7):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        self.assertEqual(world.inverse(world.step(state, action),
                                                       action), state)
                        self.assertEqual(world.step(world.inverse(state, action),
                                                    action), state)

    def test_all_worlds_are_projection_coherent(self):
        for world in family():
            for depth in range(4, 8):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        self.assertEqual(
                            world.step(state, action)[:-1],
                            world.step(state[:-1], action))

    def test_base_shear_family_compiles_earlier_proven_worlds(self):
        old = MarkedObject(Process.repeat(ZERO), 1)
        for coefficient in range(3):
            earlier = compile_shear(old, coefficient)
            now = ClassifiedWindow(0, coefficient).world()
            self.assertEqual(now.gain, earlier.gain)
            self.assertEqual(now.rule(0), earlier.rule(0))
            for index in range(1, 10):
                self.assertEqual(now.rule(index), earlier.rule(index))
            for depth in range(3, 6):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        self.assertEqual(now.step(state, action),
                                         earlier.step(state, action))

    def test_independent_support_construction_really_changes_relation(self):
        for coefficient in range(3):
            previous = ClassifiedWindow(0, coefficient)
            for support in range(3):
                changed = previous.support_next()
                self.assertIsNotNone(changed)
                self.assertEqual(changed.support, previous.support + 1)
                self.assertEqual(changed.coefficient, coefficient)
                self.assertEqual(changed.fixed_B(), previous.fixed_B() - 3)
                self.assertIsNone(classify_pair(previous, changed).witness_shear)
                previous = changed
            self.assertIsNone(previous.support_next())

    def test_construction_square_commutes_but_does_not_close_support_axis(self):
        for world in family():
            self.assertEqual(world.shear_next().shear_next().shear_next(), world)
            self.assertNotEqual(world.shear_next(), world)
            next_support = world.support_next()
            if next_support is not None:
                self.assertEqual(
                    world.shear_next().support_next(), next_support.shear_next())
            else:
                self.assertEqual(world.support, 3)
        certificate = certify_family()
        self.assertEqual((certificate.shear_orbit_order, certificate.support_walls),
                         (3, 3))

    def test_origin_based_agreement_does_not_substitute_full_state_witness(self):
        a = ClassifiedWindow(0, 0)
        b = ClassifiedWindow(1, 0)
        self.assertEqual(a.step((0, 0, 0), "B"),
                         b.step((0, 0, 0), "B"))
        self.assertNotEqual(a.step((2, 0, 0), "B"),
                            b.step((2, 0, 0), "B"))
        self.assertEqual(classify_pair(a, b).status,
                         "INEQUIVALENT_FIXED_B_AT_DEPTH_THREE")

    def test_native_representation_and_the_two_variable_extension_are_distinct(self):
        self.assertIsNotNone(ClassifiedWindow(0, 0).world().native())
        for world in family():
            if world != ClassifiedWindow(0, 0):
                self.assertIsNone(world.world().native())

    def test_full_state_conjugacy_does_not_require_literal_state_equality(self):
        original = ClassifiedWindow(2, 0)
        changed = ClassifiedWindow(2, 1)
        rel = classify_pair(original, changed)
        state = (0, 1, 0, 0, 0)
        self.assertNotEqual(rel.map_state(state), state)
        self.assertEqual(rel.map_state(state), shear(state, 1))
        self.assertEqual(rel.map_state(original.step(state, "B")),
                         changed.step(rel.map_state(state), "B"))

    def test_invalid_inputs_rejected(self):
        for support, coefficient in ((-1, 0), (4, 0), (0, 3),
                                     (True, 1), (1, False)):
            with self.assertRaises(ValueError):
                ClassifiedWindow(support, coefficient)
        with self.assertRaises(ValueError):
            scalar_invariant(2, 0)
        with self.assertRaises(ValueError):
            scalar_invariant(3, 4)
        with self.assertRaises(ValueError):
            ClassifiedWindow(2, 1).step((0, 0, 0), "invalid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
