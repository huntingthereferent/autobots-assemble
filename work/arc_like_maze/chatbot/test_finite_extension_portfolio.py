"""Independent finite replay controls for the completed-extension portfolio."""
import unittest
from itertools import combinations
from dataclasses import replace
from finite_goal_priority import Law
from bounded_backtracked_goal import discover_and_extend
from finite_extension_portfolio import compare_completed

GOALS = ((0, 1, 0), (0, 1, 1))

class PortfolioTests(unittest.TestCase):
    def test_differing_laws_keep_incompatible_completions_separate(self):
        old, new = Law((0, 0, 1)), Law((0, 0, 0))
        records = tuple(discover_and_extend(old, new, goal) for goal in GOALS)
        self.assertTrue(all(r.status == "GOAL_CARRIED_FINITE_WITNESS" for r in records))
        result = compare_completed(old, new, records, GOALS)
        self.assertEqual(result.status, "PARTIAL_GOALS")
        self.assertEqual(len(result.carried), 1)
        self.assertGreater(len(result.conflicts), 0)
        for c in result.conflicts:
            self.assertEqual(c.old_equal, old.follow(c.left_word) == old.follow(c.right_word))
            self.assertEqual(c.new_equal, new.follow(c.left_word) == new.follow(c.right_word))
            self.assertNotEqual(c.old_equal, c.new_equal)

    def test_identical_laws_admit_complete_pairing(self):
        a = Law((0, 0, 1))
        records = tuple(discover_and_extend(a, a, goal) for goal in GOALS)
        result = compare_completed(a, a, records, GOALS)
        self.assertEqual(result.status, "GOALS_CARRIED")
        self.assertEqual(len(result.carried), 2)
        self.assertEqual(len(result.paired_states), 27)
        self.assertEqual(len(result.admitted_edges), 54)
        self.assertEqual(result.compatible_subsets, 3)

    def test_independent_subset_count_and_scores(self):
        for a, b in [((0, 0, 1), (0, 0, 0)), ((0, 0, 1), (0, 0, 1))]:
            old, new = Law(a), Law(b)
            records = tuple(discover_and_extend(old, new, goal) for goal in GOALS)
            result = compare_completed(old, new, records, GOALS)
            expected = []
            for size in range(1, 3):
                for selected in combinations(range(2), size):
                    pairing = {}
                    inverse = {}
                    edges = {}
                    valid = True
                    for i in selected:
                        for s, image in records[i].paired_states:
                            if s in pairing and pairing[s] != image or image in inverse and inverse[image] != s:
                                valid = False
                                break
                            pairing[s], inverse[image] = image, s
                        if not valid: break
                        for s, action, t, ns, nt in records[i].admitted_edges:
                            if (s, action) in edges and edges[(s, action)] != (s, action, t, ns, nt):
                                valid = False
                                break
                            edges[(s, action)] = (s, action, t, ns, nt)
                        if not valid: break
                    if valid:
                        expected.append((sum(goal in pairing for goal in GOALS),
                                         len(edges), len(pairing), -len(selected)))
            self.assertEqual(result.compatible_subsets, len(expected))
            measured = (len(result.carried), len(result.admitted_edges),
                        len(result.paired_states), -len(result.indices))
            self.assertEqual(measured, max(expected))

    def test_failed_or_tampered_candidate_is_not_admitted(self):
        a, b = Law((0, 0, 1)), Law((0, 0, 0))
        good = discover_and_extend(a, b, GOALS[0])
        with self.assertRaises(ValueError):
            compare_completed(a, b, (replace(good, status="UNKNOWN_SEARCH_LIMIT"),), GOALS)
        with self.assertRaises(ValueError):
            compare_completed(a, b, (replace(good, mapped_goal=(2, 2, 2)),), GOALS)

if __name__ == "__main__":
    unittest.main()
