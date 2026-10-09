"""Five-letter A/B fixed-word obstruction after a two-invariant collision."""
import unittest
from itertools import product

from work.arc_like_maze.window_word_collision import (
    CollisionWorld, collision_rule, family, fixed_word_formula,
    classify_pair, first_fixed_count_break, certify_collision,
)
from work.arc_like_maze.window_branch import BranchedWindow
from work.arc_like_maze.nondiagonal_transport import shear


class WordCollisionTests(unittest.TestCase):
    def test_thirty_six_distinct_laws_twelve_certified_full_state_classes(self):
        certificate = certify_collision()
        self.assertEqual(certificate.status, "CLOSED_DECLARED_12_FULL_STATE_CLASSES")
        self.assertEqual((certificate.concrete_laws,
                          certificate.full_state_classes), (36, 12))
        self.assertEqual(certificate.class_sizes, (3,) * 12)
        self.assertEqual((certificate.aligned_pairs,
                          certificate.B_obstructions,
                          certificate.BBB_obstructions,
                          certificate.AABAB_obstructions),
                         (108, 972, 144, 72))
        self.assertEqual(certificate.first_balanced_word, "AABAB")
        self.assertTrue(certificate.shortest_fixed_count_obstruction)

    def test_previous_24_worlds_embed_without_changed_transitions(self):
        old = [BranchedWindow(k, c, pulse) for k in range(4)
               for pulse in (0, 1) for c in range(3)]
        for original in old:
            current = CollisionWorld(
                original.support, original.coefficient, original.pulse, 0)
            self.assertEqual(current.world(), original.world())
            for depth in (3, 4, 5):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        self.assertEqual(current.step(state, action),
                                         original.step(state, action))

    def test_balanced_edit_changes_exactly_two_entries_outside_old_rows(self):
        for k, c in product(range(4), range(3)):
            old = collision_rule(k, c, 0, 0)
            new = collision_rule(k, c, 0, 1)
            self.assertEqual([(i, (new[i]-old[i]) % 3)
                              for i in range(9) if old[i] != new[i]],
                             [(3, 1), (4, 2)])
            self.assertEqual(sum(new[3:6]) % 3, sum(old[3:6]) % 3)

    def test_first_two_invariants_collide_but_five_letter_word_splits(self):
        for k, c in product(range(4), range(3)):
            original = CollisionWorld(k, c, 0, 0)
            changed = CollisionWorld(k, c, 0, 1)
            self.assertEqual(original.fixed_word("B"), changed.fixed_word("B"))
            self.assertEqual(original.fixed_word("BBB"), changed.fixed_word("BBB"))
            self.assertEqual(original.fixed_word("AABAB"), 9)
            self.assertEqual(changed.fixed_word("AABAB"), 3)

    def test_no_shorter_word_has_a_different_fixed_point_count(self):
        for k, c in product(range(4), range(3)):
            source = CollisionWorld(k, c, 0, 0)
            target = CollisionWorld(k, c, 0, 1)
            self.assertIsNone(first_fixed_count_break(source, target, 4))
            self.assertEqual(first_fixed_count_break(source, target, 5),
                             ("AABAB", 9, 3))

    def test_all_three_word_invariants_have_exact_all_depth_formulas(self):
        for obj in family():
            for depth in range(3, 7):
                for word in ("B", "BBB", "AABAB"):
                    self.assertEqual(
                        obj.fixed_word(word, depth),
                        fixed_word_formula(word, depth, obj.support,
                                           obj.pulse, obj.balanced),
                    )

    def test_every_ordered_pair_has_a_witness_or_a_concrete_obstruction(self):
        count = {"map": 0, "B": 0, "BBB": 0, "AABAB": 0}
        for source in family():
            for target in family():
                result = classify_pair(source, target)
                if result.shear_witness is None:
                    self.assertEqual(result.status, "INEQUIVALENT_WORD_FIXED_POINTS")
                    self.assertNotEqual(result.source_fixed, result.target_fixed)
                    self.assertEqual(result.first_obstruction_depth, 3)
                    count[result.obstruction_word] += 1
                else:
                    count["map"] += 1
                    for depth in (3, 4, 5):
                        for state in product(range(3), repeat=depth):
                            image = result.map_state(state)
                            for a in "AB":
                                self.assertEqual(
                                    result.map_state(source.step(state, a)),
                                    target.step(image, a))
        self.assertEqual(count, {"map": 108, "B": 972,
                                 "BBB": 144, "AABAB": 72})

    def test_new_non_diagonal_state_maps_compose_and_invert(self):
        for k, pulse, balanced in product(range(4), (0, 1), (0, 1)):
            if pulse and balanced:
                continue
            a = CollisionWorld(k, 0, pulse, balanced)
            b = CollisionWorld(k, 1, pulse, balanced)
            c = CollisionWorld(k, 2, pulse, balanced)
            for state in product(range(3), repeat=5):
                ab = classify_pair(a, b).map_state
                bc = classify_pair(b, c).map_state
                ac = classify_pair(a, c).map_state
                self.assertEqual(bc(ab(state)), ac(state))
                self.assertEqual(shear(shear(state, 2), 1), state)

    def test_all_triangular_laws_are_reversible_on_complete_state_sets(self):
        for world in family():
            for depth in range(3, 7):
                for state in product(range(3), repeat=depth):
                    for a in "AB":
                        after = world.step(state, a)
                        self.assertEqual(world.inverse(after, a), state)
                        self.assertEqual(world.step(world.inverse(state, a), a),
                                         state)

    def test_dimensional_projections_commute_with_actions(self):
        for world in family():
            for depth in range(4, 8):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        self.assertEqual(
                            world.step(state, action)[:-1],
                            world.step(state[:-1], action))

    def test_finite_constructors_have_a_fork_not_a_false_square(self):
        for k, c in product(range(4), range(3)):
            root = CollisionWorld(k, c, 0, 0)
            p = root.pulse_next()
            t = root.balanced_next()
            self.assertIsNotNone(p)
            self.assertIsNotNone(t)
            self.assertNotEqual(p, t)
            self.assertIsNone(p.balanced_next())
            self.assertIsNone(t.pulse_next())
            self.assertEqual(root.shear_next().pulse_next(), p.shear_next())
            self.assertEqual(root.shear_next().balanced_next(), t.shear_next())
            if k < 3:
                self.assertEqual(root.support_next().pulse_next(),
                                 p.support_next())
                self.assertEqual(root.support_next().balanced_next(),
                                 t.support_next())
            else:
                self.assertIsNone(root.support_next())

    def test_shear_returns_after_three_distinct_laws_for_each_class(self):
        for world in family():
            self.assertEqual(world.shear_next().shear_next().shear_next(), world)
            self.assertNotEqual(world, world.shear_next())
            self.assertNotEqual(world, world.shear_next().shear_next())

    def test_word_break_is_not_merely_a_difference_in_origin_trajectory(self):
        base = CollisionWorld(0, 0, 0, 0)
        edit = CollisionWorld(0, 0, 0, 1)
        self.assertEqual(base.move((0, 0, 0), "BBB"), (0, 0, 0))
        self.assertEqual(edit.move((0, 0, 0), "BBB"), (0, 0, 0))
        self.assertEqual(base.fixed_word("BBB"), edit.fixed_word("BBB"))
        self.assertNotEqual(base.fixed_word("AABAB"), edit.fixed_word("AABAB"))

    def test_invalid_outside_declared_family_is_rejected(self):
        for bad in ((0, 0, 1, 1), (4, 0, 0, 0), (0, 3, 0, 0),
                    (0, 0, 0, 2), (True, 0, 0, 0)):
            with self.assertRaises(ValueError):
                CollisionWorld(*bad)
        obj = CollisionWorld(0, 0, 0, 1)
        with self.assertRaises(ValueError):
            obj.move((0, 0, 0), "C")
        with self.assertRaises(ValueError):
            obj.fixed_word("AABAB", 2)
        with self.assertRaises(ValueError):
            first_fixed_count_break(obj, obj, -1)
        with self.assertRaises(ValueError):
            fixed_word_formula("BA", 3, 0, 0, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
