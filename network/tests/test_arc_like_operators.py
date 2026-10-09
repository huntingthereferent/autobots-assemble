"""One-layer-up constructed-world relations, not native ARC runs."""
import unittest

from work.arc_like_maze.alignment import discover_alignment
from work.arc_like_maze.math import World, inverse_candidates
from work.arc_like_maze.operators import (
    SCALE, SHEAR, SWAP, TRANSLATE, COLLAPSE,
    audit_constructors, shear_three_turn_witness,
)


class ConstructionOperatorTests(unittest.TestCase):
    def test_three_turn_closed_construction_loop_not_three_equal_worlds(self):
        loop = shear_three_turn_witness()
        self.assertEqual([w.phi for w in loop], [(0, 1, 0), (0, 1, 1), (0, 1, 2), (0, 1, 0)])
        self.assertTrue(all(loop[i] != loop[i+1] for i in range(3)))
        self.assertTrue(all(not discover_alignment(loop[i], loop[i+1]).aligned for i in range(3)))

    def test_shear_third_power_identity_on_all_nine_candidates(self):
        self.assertTrue(all(SHEAR(SHEAR(SHEAR(w))) == w for w in inverse_candidates()))

    def test_scale_shear_swap_respect_A_B_equivalence(self):
        result = audit_constructors((SCALE, SHEAR, SWAP))
        self.assertEqual(result.status, "CLOSED_ON_AB_QUOTIENT")
        self.assertEqual((result.states, len(result.classes), result.operator_edges), (9, 5, 27))
        self.assertEqual(result.refinement_rounds, 0)
        self.assertEqual(result.refined_classes, result.classes)
        self.assertEqual(sorted(map(len, result.recurrent_components)), [1, 4])
        self.assertFalse(result.quotient_breaks)

    def test_scale_only_preserves_every_world_relation(self):
        result = audit_constructors((SCALE,))
        self.assertEqual(result.status, "CLOSED_ON_AB_QUOTIENT")
        self.assertEqual(result.preserving_edges, 9)
        self.assertFalse(result.broken_edges)

    def test_shear_moves_between_classes_but_quotient_stays_well_defined(self):
        result = audit_constructors((SHEAR,))
        self.assertEqual(result.status, "CLOSED_ON_AB_QUOTIENT")
        self.assertEqual(result.preserving_edges, 3)
        self.assertEqual(len(result.broken_edges), 6)
        self.assertEqual(sorted(map(len, result.recurrent_components)), [1, 1, 3])
        first = result.broken_edges[0]
        w1, w2 = first.conflicting_words
        # A mismatch must be witnessed in at least one of the two directions.
        a, b = World(3, first.source), World(3, first.target)
        self.assertNotEqual(a.apply(w1) == a.apply(w2), b.apply(w1) == b.apply(w2))

    def test_swap_can_move_between_classes_without_breaking_quotient(self):
        result = audit_constructors((SWAP,))
        self.assertEqual(result.status, "CLOSED_ON_AB_QUOTIENT")
        self.assertEqual(result.preserving_edges, 5)
        self.assertEqual(len(result.broken_edges), 4)

    def test_translation_breaks_old_quotient_with_concrete_witness(self):
        result = audit_constructors((SCALE, SHEAR, SWAP, TRANSLATE))
        self.assertEqual(result.status, "OPEN_AB_QUOTIENT")
        self.assertEqual(len(result.classes), 5)
        self.assertEqual(len(result.refined_classes), 9)
        self.assertEqual(result.refinement_rounds, 1)
        self.assertEqual(len(result.quotient_breaks), 4)
        for failure in result.quotient_breaks:
            self.assertEqual(failure.operator, "translate")
            a, b = (World(3, phi) for phi in failure.equivalent_sources)
            self.assertTrue(discover_alignment(a, b).aligned)
            ta, tb = TRANSLATE(a), TRANSLATE(b)
            self.assertFalse(discover_alignment(ta, tb).aligned)
            w1, w2 = failure.target_words
            self.assertNotEqual(ta.apply(w1) == ta.apply(w2), tb.apply(w1) == tb.apply(w2))

    def test_collapsing_operator_does_not_falsely_count_as_equivalence(self):
        result = audit_constructors((COLLAPSE,))
        self.assertEqual(result.status, "CLOSED_ON_AB_QUOTIENT")
        self.assertTrue(result.broken_edges)
        self.assertLess(result.preserving_edges, result.operator_edges)

    def test_unknown_when_reachable_search_exhaustion(self):
        result = audit_constructors((SHEAR,), max_states=2)
        self.assertEqual(result.status, "UNKNOWN")

    def test_unknown_for_empty_operator_set(self):
        self.assertEqual(audit_constructors(()).status, "UNKNOWN")

    def test_world_family_boundary_not_silently_closed(self):
        result = audit_constructors((SHEAR,), family=(World(3, (0, 1, 0)),))
        self.assertEqual(result.status, "OPEN_FAMILY")

    def test_operator_rejects_incompatible_depth(self):
        with self.assertRaises(ValueError):
            SHEAR(World(4))


if __name__ == '__main__':
    unittest.main(verbosity=2)
