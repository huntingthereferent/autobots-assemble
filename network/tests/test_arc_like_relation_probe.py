"""Finite A/B observation-guided probe: native math, witnesses, and scope walls."""
import unittest

from work.arc_like_maze.alignment import equivalent_classes
from work.arc_like_maze.math import World, inverse_candidates
from work.arc_like_maze.relation_probe import (
    endpoint_equal, identify, separating_probes,
)


class RelationProbeTests(unittest.TestCase):
    def setUp(self):
        self.candidates = inverse_candidates()
        self.probes = separating_probes(self.candidates)

    def test_probes_are_exact_separating_witnesses(self):
        self.assertEqual(len(self.probes), 3)
        self.assertEqual(len(set(self.probes)), 3)
        for pair in self.probes:
            self.assertNotEqual(set(endpoint_equal(w, pair) for w in self.candidates), {True})
            self.assertNotEqual(set(endpoint_equal(w, pair) for w in self.candidates), {False})

    def test_all_nine_resolve_to_exact_rooted_classes_with_two_to_three_queries(self):
        classes = equivalent_classes(self.candidates)
        self.assertEqual(sorted(map(len, classes)), [1, 2, 2, 2, 2])
        for target in self.candidates:
            with self.subTest(target=target.phi):
                result = identify(self.candidates,
                                  lambda pair: endpoint_equal(target, pair), self.probes)
                self.assertEqual(result.status, "CONDITIONAL_CLASS")
                self.assertIn(len(result.observations), (2, 3))
                expected = next(c for c in classes if target in c)
                self.assertEqual(tuple(self.candidates[i] for i in result.candidate_indices), expected)
                for record in result.observations:
                    self.assertEqual(record.equal, endpoint_equal(target, record.probe))

    def test_outside_grammar_can_share_a_signature(self):
        outsider = World(3, (1, 0, 0))
        self.assertNotIn(outsider, self.candidates)
        result = identify(self.candidates,
                          lambda pair: endpoint_equal(outsider, pair), self.probes)
        self.assertEqual(result.status, "CONDITIONAL_CLASS")
        self.assertGreater(len(result.candidate_indices), 0)
        self.assertEqual(tuple(self.candidates[i].phi for i in result.candidate_indices),
                         ((0, 1, 0), (0, 2, 0)))

    def test_exhausted_budget_is_not_a_classification(self):
        target = self.candidates[5]
        result = identify(self.candidates,
                          lambda pair: endpoint_equal(target, pair), self.probes,
                          max_queries=1)
        self.assertEqual(result.status, "UNKNOWN_BUDGET")
        self.assertEqual(len(result.observations), 1)
        self.assertGreater(len(result.candidate_indices), 2)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            separating_probes(())
        with self.assertRaises(ValueError):
            separating_probes((self.candidates[0], self.candidates[0]))
        with self.assertRaises(ValueError):
            identify(self.candidates, lambda _: True, self.probes, max_queries=-1)


if __name__ == "__main__":
    unittest.main()
