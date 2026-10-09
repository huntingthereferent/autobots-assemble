"""Counterexamples and finite closure for inverse A/B constructed worlds."""
import unittest

from work.arc_like_maze.alignment import (
    certify_finite_family, certify_inverse_candidates, discover_alignment,
    equivalent_classes, scale_construction,
)
from work.arc_like_maze.math import World, inverse_candidates


class GeneratedAlignmentTests(unittest.TestCase):
    def test_discover_distinct_values_same_relations_without_given_map(self):
        a = World(3, (0, 1, 2))
        b = World(3, (0, 2, 1))
        witness = discover_alignment(a, b)
        self.assertTrue(witness.aligned)
        self.assertEqual(len(witness.pairs), 27)
        self.assertEqual(dict(witness.pairs)[a.apply("BB")], b.apply("BB"))
        self.assertNotEqual(a.apply("BB"), b.apply("BB"))

    def test_inverse_alignment_without_manual_inverse(self):
        a, b = World(3, (0, 1, 2)), World(3, (0, 2, 1))
        left = dict(discover_alignment(a, b).pairs)
        right = dict(discover_alignment(b, a).pairs)
        self.assertTrue(all(right[v] == k for k, v in left.items()))

    def test_nonlinear_relation_has_action_word_counterexample(self):
        a, b = World(3), World(3, (0, 1, 1))
        result = discover_alignment(a, b)
        self.assertEqual(result.status, "OPEN")
        w1, w2 = result.conflicting_words
        self.assertEqual(a.apply(w1), a.apply(w2))
        self.assertNotEqual(b.apply(w1), b.apply(w2))

    def test_deeper_world_cannot_be_mistaken_for_closure(self):
        witness = discover_alignment(World(3), World(4))
        self.assertEqual(witness.status, "OPEN")
        self.assertIsNotNone(witness.conflicting_words)

    def test_exploration_budget_is_unknown_not_open(self):
        self.assertEqual(discover_alignment(World(3), World(3), max_states=3).status, "UNKNOWN")

    def test_candidate_world_equivalence_partition_is_complete(self):
        groups = equivalent_classes(inverse_candidates())
        self.assertEqual(sum(len(group) for group in groups), 9)
        for group in groups:
            for world in group:
                self.assertTrue(discover_alignment(group[0], world).aligned)
        for i, group in enumerate(groups):
            for other in groups[i + 1:]:
                self.assertFalse(discover_alignment(group[0], other[0]).aligned)

    def test_closed_family_all_nine_relations_automatically_aligned(self):
        result = certify_inverse_candidates()
        self.assertEqual(result.status, "CLOSED_FOR_DECLARED_FAMILY")
        self.assertEqual(result.aligned_edges, 9)
        self.assertEqual(sum(len(c) for c in result.cycles), 9)
        self.assertEqual(sorted(len(c) for c in result.cycles), [1, 2, 2, 2, 2])

    def test_not_silently_closing_incomplete_family(self):
        result = certify_finite_family((World(3, (0, 1, 2)),), scale_construction)
        self.assertEqual(result.status, "OPEN")
        self.assertIn("leaves", result.failure)

    def test_constructor_that_changes_relation_is_not_closed(self):
        family = (World(3), World(3, (0, 1, 1)))
        result = certify_finite_family(family, lambda w: family[1] if w == family[0] else family[0])
        self.assertEqual(result.status, "OPEN")
        self.assertIsNotNone(result.conflicting_words)

    def test_identity_constructor_is_trivial_closure_only(self):
        w = World(3)
        result = certify_finite_family((w,), lambda current: current)
        self.assertEqual(result.status, "CLOSED_FOR_DECLARED_FAMILY")
        self.assertEqual(len(result.cycles[0]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
