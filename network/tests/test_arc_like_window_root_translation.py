"""Central root-moving witness: a distinct operator from H and R."""
import unittest
from dataclasses import replace
from itertools import product

from work.arc_like_maze.window_combined import CombinedWorld, classify_pair, family
from work.arc_like_maze.window_marked_arrows import (
    ORIGIN, PointedWorld, StateArrow, canonical_arrow, transport_target_mark,
)
from work.arc_like_maze.window_root_translation import (
    translate, TranslationFactor, ConjugacyFactor, OperatorPath,
    PointedOperator, include_existing, shift_point, shift_nonroot_bridge,
    certify_translation,
)


class RootTranslationTests(unittest.TestCase):
    def test_new_operator_has_order_three_and_inverse(self):
        for depth in range(3, 8):
            for state in product(range(3), repeat=depth):
                self.assertEqual(translate(translate(translate(state, 1), 1), 1), state)
                for r in range(3):
                    self.assertEqual(translate(translate(state, r), (-r) % 3), state)

    def test_independent_root_symmetry_commutes_with_A_B_every_world(self):
        for world in family():
            for depth in range(3, 7):
                for state in product(range(3), repeat=depth):
                    for a in 'AB':
                        for r in range(3):
                            self.assertEqual(translate(world.step(state, a), r),
                                             world.step(translate(state, r), a))

    def test_new_operator_commutes_with_H_R_old_full_state_maps(self):
        for k in (0, 3):
            for c, d in product(range(3), repeat=2):
                a = CombinedWorld(k, c, 1, 0)
                b = CombinedWorld(k, d, 1, 1)
                for s, t in ((a, b), (b, a)):
                    old = canonical_arrow(s, t)
                    for state in product(range(3), repeat=5):
                        for r in (1, 2):
                            self.assertEqual(
                                translate(old.map_state(state), r),
                                old.map_state(translate(state, r)))

    def test_marked_target_must_change_on_new_root_translation(self):
        source = PointedWorld(CombinedWorld(1, 0, 0, 0))
        for amount in (1, 2):
            moved = shift_point(source, amount)
            self.assertEqual(moved.source, source)
            self.assertEqual(moved.target.mark, (0, 0, amount))
            self.assertEqual(moved.map_state(ORIGIN), moved.target.mark)
            with self.assertRaises(ValueError):
                OperatorPath(source, source,
                             (TranslationFactor(source.world, amount),)).require_marked()

    def test_three_pointed_marks_are_not_three_world_laws(self):
        for world in family():
            marks = {shift_point(PointedWorld(world), r).target.mark for r in range(3)}
            self.assertEqual(marks, {(0, 0, 0), (0, 0, 1), (0, 0, 2)})
            self.assertEqual({shift_point(PointedWorld(world), r).target.world
                              for r in range(3)}, {world})

    def test_shift_and_shear_is_a_commuting_pointed_square(self):
        for w in family():
            successor = CombinedWorld(w.support, (w.coefficient + 1) % 3, w.pulse, w.balanced)
            a = PointedWorld(w)
            h = include_existing(canonical_arrow(w, successor)).require_marked()
            for r in (1, 2):
                moved_a = shift_point(a, r)
                moved_b = shift_point(h.target, r)
                # Lift the SAME witness H to a noncanonical mark.
                from_witness = OperatorPath(moved_a.target, moved_b.target, h.path.factors)
                self.assertEqual(from_witness.mark_status, "MARK_PRESERVED")
                top = h.then(moved_b)
                bottom = moved_a.then(from_witness.require_marked())
                self.assertEqual(top.source, bottom.source)
                self.assertEqual(top.target, bottom.target)
                for state in product(range(3), repeat=4):
                    self.assertEqual(top.map_state(state), bottom.map_state(state))

    def test_existing_rooted_arrow_can_be_lifted_without_erasing_factors(self):
        a = CombinedWorld(2, 0, 0, 0)
        b = CombinedWorld(2, 2, 0, 0)
        old = canonical_arrow(a, b).require_marked()
        new = include_existing(old).require_marked()
        self.assertEqual(len(new.path.factors), len(old.state_arrow.factors))
        self.assertIsInstance(new.path.factors[0], ConjugacyFactor)
        for state in product(range(3), repeat=5):
            self.assertEqual(new.map_state(state), old.map_state(state))

    def test_nonroot_bridge_cannot_be_silent_marked_arrow(self):
        old = canonical_arrow(CombinedWorld(0, 0, 1, 0), CombinedWorld(0, 1, 1, 1))
        with self.assertRaises(ValueError):
            include_existing(old).require_marked()
        changed = shift_nonroot_bridge(old.source.world, old.target.world, 1)
        self.assertEqual(changed.old_change.original.target.mark, ORIGIN)
        self.assertEqual(changed.route.target.mark, (0, 2, 2))
        self.assertEqual(changed.route.source.mark, ORIGIN)
        self.assertEqual(len(changed.route.path.factors), 2)
        self.assertIsInstance(changed.route.path.factors[0], ConjugacyFactor)
        self.assertIsInstance(changed.route.path.factors[1], TranslationFactor)

    def test_full_nonroot_family_has_three_explicit_target_marks_each(self):
        for k in (0, 3):
            for c, d in product(range(3), repeat=2):
                a = CombinedWorld(k, c, 1, 0)
                b = CombinedWorld(k, d, 1, 1)
                routes = [shift_nonroot_bridge(a, b, r) for r in range(3)]
                self.assertEqual(len({q.route.target.mark for q in routes}), 3)
                self.assertTrue(all(q.route.target.mark[1] == 2 for q in routes))
                self.assertTrue(all(q.route.target.mark != ORIGIN for q in routes))
                for route in routes:
                    left, right, same, different_a, different_b = (
                        route.old_change.original_root_conflict)
                    self.assertEqual(a.apply(ORIGIN, left), a.apply(ORIGIN, right))
                    self.assertNotEqual(b.apply(ORIGIN, left), b.apply(ORIGIN, right))

    def test_inverse_of_mixed_operators_uses_literal_stored_witnesses(self):
        a = CombinedWorld(3, 0, 1, 0)
        b = CombinedWorld(3, 1, 1, 1)
        path = shift_nonroot_bridge(a, b, 2).route
        back = path.inverse()
        self.assertEqual(len(back.path.factors), 2)
        self.assertIsInstance(back.path.factors[0], TranslationFactor)
        self.assertIsInstance(back.path.factors[1], ConjugacyFactor)
        for state in product(range(3), repeat=6):
            self.assertEqual(back.map_state(path.map_state(state)), state)
        identity = path.then(back)
        self.assertEqual(identity.source, identity.target)
        self.assertEqual(len(identity.path.factors), 4)

    def test_intermediate_pointed_mark_must_match_not_just_world(self):
        a = CombinedWorld(3, 0, 1, 0)
        b = CombinedWorld(3, 2, 1, 1)
        bridge = shift_nonroot_bridge(a, b, 2).route
        naive = include_existing(canonical_arrow(b, a))
        with self.assertRaises(ValueError):
            bridge.path.compose(naive)
        with self.assertRaises(ValueError):
            bridge.then(shift_point(PointedWorld(b), 1))
        self.assertEqual(bridge.then(bridge.inverse()).target, PointedWorld(a))

    def test_factor_chain_rejects_disconnected_or_obstructed_witnesses(self):
        a = CombinedWorld(0, 0, 0, 0)
        b = CombinedWorld(1, 0, 0, 0)
        with self.assertRaises(ValueError):
            include_existing(canonical_arrow(a, b))
        with self.assertRaises(ValueError):
            OperatorPath(PointedWorld(a), PointedWorld(a), ())
        with self.assertRaises(ValueError):
            OperatorPath(PointedWorld(a), PointedWorld(b),
                         (TranslationFactor(a, 1),))
        with self.assertRaises(ValueError):
            OperatorPath(PointedWorld(a), PointedWorld(a),
                         (TranslationFactor(a, 1), TranslationFactor(b, 1)))
        with self.assertRaises(ValueError):
            from work.arc_like_maze.window_root_translation import from_relation
            from_relation(classify_pair(a, b))

    def test_forged_marks_witnesses_and_amounts_rejected(self):
        a = CombinedWorld(0, 0, 1, 0)
        b = CombinedWorld(0, 0, 1, 1)
        target = shift_nonroot_bridge(a, b, 1)
        with self.assertRaises(ValueError):
            replace(target, old_change=transport_target_mark(canonical_arrow(b, a)))
        with self.assertRaises(ValueError):
            replace(target, route=shift_point(PointedWorld(a), 1))
        for amount in (True, -1, 3, 1.0):
            with self.assertRaises(ValueError):
                shift_point(PointedWorld(a), amount)
        with self.assertRaises(ValueError):
            translate((0, 0), 1)
        with self.assertRaises(ValueError):
            translate((0, 0, 0), 3)
        with self.assertRaises(ValueError):
            translate((0, False, 0), 1)

    def test_full_operator_audit_for_all_48_worlds(self):
        c = certify_translation()
        self.assertEqual(c.status, 'CLOSED_TRANSLATION_AND_EXPLICIT_MARK_TRANSPORT')
        self.assertEqual((c.worlds, c.distinct_translated_marks), (48, 144))
        self.assertEqual((c.canonical_rooted_relations, c.nonrooted_relations),
                         (144, 36))
        self.assertEqual((c.translated_rooted_routes, c.translated_nonroot_routes),
                         (432, 108))
        self.assertEqual((c.blocked_nonroot_promotions,
                          c.fixed_root_conflicts_retained), (36, 108))


if __name__ == '__main__':
    unittest.main(verbosity=2)
