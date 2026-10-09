"""48 independently constructed laws; exact full-state vs rooted distinction."""
import unittest
from collections import Counter
from itertools import product

from work.arc_like_maze.window_combined import (
    CombinedWorld, combined_rule, family, fixed_word_formula,
    classify_pair, rooted_conflict, certify_combined,
)
from work.arc_like_maze.window_word_collision import CollisionWorld
from work.arc_like_maze.nondiagonal_transport import shear


class CombinedWindowTests(unittest.TestCase):
    def test_previous_thirty_six_worlds_embed_exactly(self):
        for k, e, t, c in product(range(4), range(2), range(2), range(3)):
            if (e, t) == (1, 1):
                continue
            old = CollisionWorld(k, c, e, t)
            new = CombinedWorld(k, c, e, t)
            self.assertEqual(old.world(), new.world())

    def test_forty_eight_distinct_two_predecessor_laws(self):
        members = family()
        self.assertEqual(len(members), 48)
        self.assertEqual(len(set(members)), 48)
        signatures = {
            tuple(w.step(s, "B") for s in product(range(3), repeat=3))
            for w in members
        }
        self.assertEqual(len(signatures), 48)

    def test_complete_14_full_state_and_16_rooted_classes(self):
        cert = certify_combined()
        self.assertEqual(cert.status, "CLOSED_DECLARED_FULL_AND_ROOTED_QUOTIENTS")
        self.assertEqual((cert.concrete_worlds, cert.full_state_classes,
                          cert.rooted_classes), (48, 14, 16))
        self.assertEqual(cert.full_class_sizes, (3,)*12+(6,)*2)
        self.assertEqual(cert.rooted_class_sizes, (3,)*16)
        self.assertEqual(
            (cert.rooted_ordered_maps, cert.nonroot_ordered_maps,
             cert.B_obstructed, cert.BBB_obstructed,
             cert.AABAB_obstructed, cert.ABABAB_obstructed,
             cert.verified_root_collisions),
            (144, 36, 1728, 288, 72, 36, 36),
        )

    def test_all_four_word_formulas_are_exact_on_full_finite_states(self):
        for w in family():
            for depth in (3, 4, 5, 6):
                for word in ("B", "BBB", "AABAB", "ABABAB"):
                    self.assertEqual(w.fixed_word(word, depth),
                                     fixed_word_formula(
                                         word, depth, w.support, w.pulse,
                                         w.balanced))

    def test_combined_edit_collides_on_first_three_invariants(self):
        for k, c in product(range(4), range(3)):
            a = CombinedWorld(k, c, 1, 0)
            b = CombinedWorld(k, c, 1, 1)
            for word in ("B", "BBB", "AABAB"):
                self.assertEqual(a.fixed_word(word), b.fixed_word(word))

    def test_sixth_letter_word_obstructs_middle_supports(self):
        for k, source_count, target_count in ((1, 18, 9), (2, 9, 0)):
            for c in range(3):
                a = CombinedWorld(k, c, 1, 0)
                b = CombinedWorld(k, c, 1, 1)
                self.assertEqual((a.fixed_word("ABABAB"),
                                  b.fixed_word("ABABAB")),
                                 (source_count, target_count))
                rel = classify_pair(a, b)
                self.assertEqual(rel.obstruction_word, "ABABAB")
                self.assertEqual(rel.obstruction_depth, 3)
                with self.assertRaises(ValueError):
                    rel.map_state((0, 0, 0))

    def test_no_shorter_fixed_word_count_obstruction_for_middle_supports(self):
        for k in (1, 2):
            source = CombinedWorld(k, 0, 1, 0)
            target = CombinedWorld(k, 0, 1, 1)
            for n in range(1, 6):
                for chars in product("AB", repeat=n):
                    word = "".join(chars)
                    self.assertEqual(source.fixed_word(word),
                                     target.fixed_word(word),
                                     f"shorter obstruction at {word} k={k}")

    def test_outer_supports_have_full_state_nonroot_conjugacy(self):
        for k in (0, 3):
            for c, d in product(range(3), repeat=2):
                source = CombinedWorld(k, c, 1, 0)
                target = CombinedWorld(k, d, 1, 1)
                for a, b in ((source, target), (target, source)):
                    rel = classify_pair(a, b)
                    self.assertEqual(rel.status,
                                     "ALL_DEPTH_FULL_STATE_NONROOT_CONJUGACY")
                    self.assertFalse(rel.root_preserving)
                    self.assertNotEqual(rel.map_state((0, 0, 0)),
                                        (0, 0, 0))
                    for depth in (3, 4, 5, 6):
                        for state in product(range(3), repeat=depth):
                            image = rel.map_state(state)
                            for action in "AB":
                                self.assertEqual(
                                    rel.map_state(a.step(state, action)),
                                    b.step(image, action))

    def test_explicit_nonroot_map_is_reversible_on_both_directions(self):
        for k, c, d in product((0, 3), range(3), range(3)):
            a = CombinedWorld(k, c, 1, 0)
            b = CombinedWorld(k, d, 1, 1)
            forward = classify_pair(a, b).map_state
            backward = classify_pair(b, a).map_state
            for state in product(range(3), repeat=5):
                self.assertEqual(backward(forward(state)), state)
                self.assertEqual(forward(backward(state)), state)

    def test_two_positive_words_witness_failed_rooted_alignment(self):
        for k in (0, 3):
            for c, d in product(range(3), repeat=2):
                a = CombinedWorld(k, c, 1, 0)
                b = CombinedWorld(k, d, 1, 1)
                witness = rooted_conflict(a, b)
                self.assertIsNotNone(witness)
                word1, word2, same_source, target1, target2 = witness
                origin = (0, 0, 0)
                self.assertEqual(a.apply(origin, word1), same_source)
                self.assertEqual(a.apply(origin, word2), same_source)
                self.assertEqual(b.apply(origin, word1), target1)
                self.assertEqual(b.apply(origin, word2), target2)
                self.assertNotEqual(target1, target2)

    def test_classify_all_2304_ordered_pairs_without_unknown_merges(self):
        tally = Counter()
        for a in family():
            for b in family():
                rel = classify_pair(a, b)
                if rel.kind:
                    tally["root" if rel.root_preserving else "nonroot"] += 1
                else:
                    tally[rel.obstruction_word] += 1
                    self.assertNotEqual(rel.source_count, rel.target_count)
        self.assertEqual(tally, Counter({
            "root":144, "nonroot":36, "B":1728, "BBB":288,
            "AABAB":72, "ABABAB":36,
        }))

    def test_no_projection_break_or_noninvertible_transition(self):
        for w in family():
            for depth in (3, 4, 5, 6):
                for state in product(range(3), repeat=depth):
                    for action in "AB":
                        moved = w.step(state, action)
                        self.assertEqual(w.inverse(moved, action), state)
                        if depth >= 4:
                            self.assertEqual(
                                moved[:-1], w.step(state[:-1], action))

    def test_complete_grid_operator_directions_are_independent(self):
        for k, c in product(range(4), range(3)):
            start = CombinedWorld(k, c, 0, 0)
            via_pulse = start.pulse_next().balanced_next()
            via_balance = start.balanced_next().pulse_next()
            self.assertEqual(via_pulse, via_balance)
            self.assertEqual((via_pulse.pulse, via_pulse.balanced),(1,1))
            self.assertEqual(start.shear_next().pulse_next().balanced_next(),
                             via_pulse.shear_next())
            if k < 3:
                self.assertEqual(start.support_next().pulse_next().balanced_next(),
                                 via_pulse.support_next())
            else:
                self.assertIsNone(start.support_next())

    def test_every_shear_orbit_is_exactly_three_unequal_worlds(self):
        for w in family():
            self.assertEqual(w.shear_next().shear_next().shear_next(), w)
            self.assertNotEqual(w.shear_next(), w)
            self.assertNotEqual(w.shear_next().shear_next(), w)
            self.assertTrue(classify_pair(w, w.shear_next()).root_preserving)

    def test_reject_invalid_parameters_and_unproved_word_formula(self):
        for bad in ((0,0,0,2),(0,0,2,0),(0,3,0,0),(4,0,0,0),
                    (0,False,0,0)):
            with self.assertRaises(ValueError): CombinedWorld(*bad)
        with self.assertRaises(ValueError):
            fixed_word_formula("ABAB",3,0,1,1)
        with self.assertRaises(ValueError):
            fixed_word_formula("ABABAB",2,0,1,1)
        with self.assertRaises(ValueError):
            CombinedWorld(0,0,1,1).apply((0,0,0),"C")
        with self.assertRaises(ValueError):
            CombinedWorld(0,0,1,1).fixed_word("BBB",2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
