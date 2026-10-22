"""Auditable, paired WORLD48 runner trials; no inference beyond the declared laws."""
import unittest

from work.arc3.window48_challenges import check_rooted_paths
from work.arc_like_maze.runner_comparison import compare_runners, run_runner


class FiniteRunnerComparisonTests(unittest.TestCase):
    def test_breadth_runner_finds_and_replays_original_rooted_split(self):
        result = run_runner(0, "breadth", budget=100, depth_bound=8)
        self.assertEqual(result["status"], "VERIFIED_ROOTED_SPLIT")
        self.assertLessEqual(result["observations"], 100)
        self.assertEqual(result["expanded_edges"] * 2, result["observations"])
        self.assertTrue(
            check_rooted_paths(result["law_ids"], *result["witness_words"])["passed"]
        )
        self.assertTrue(result["trace"])

    def test_policy_comparison_receives_same_world_and_budget(self):
        comparison = compare_runners(0, budget=72, depth_bound=8)
        self.assertEqual(set(comparison["runners"]), {"breadth", "depth"})
        for policy, result in comparison["runners"].items():
            self.assertEqual(result["policy"], policy)
            self.assertEqual(result["law_ids"], comparison["law_ids"])
            self.assertEqual(result["budget"], comparison["same_budget"])
            self.assertEqual(result["depth_bound"], comparison["same_depth_bound"])
            self.assertLessEqual(result["observations"], 72)
            self.assertEqual(result["expanded_edges"] * 2, result["observations"])
            self.assertTrue(all(row["action"] in "AB" for row in result["trace"]))
            if result["status"] == "VERIFIED_ROOTED_SPLIT":
                self.assertTrue(
                    check_rooted_paths(result["law_ids"], *result["witness_words"])["passed"]
                )
            else:
                self.assertIsNone(result["witness_words"])
                self.assertIn(result["status"], {"BUDGET_WALL", "DEPTH_WALL", "EXHAUSTED_DECLARED_STATES"})

    def test_reproducible_trace_and_explicit_zero_budget_wall(self):
        first = run_runner(2, "breadth", budget=42, depth_bound=6)
        second = run_runner(2, "breadth", budget=42, depth_bound=6)
        self.assertEqual(first, second)
        wall = run_runner(2, "depth", budget=0, depth_bound=6)
        self.assertEqual((wall["status"], wall["observations"], wall["trace"]),
                         ("BUDGET_WALL", 0, []))

    def test_unadmitted_challenge_policy_and_limits_rejected(self):
        for args in [
            (-1, "breadth", 20, 8), (48, "breadth", 20, 8),
            (0, "unapproved", 20, 8), (0, "depth", -1, 8),
            (0, "depth", 20, 0),
        ]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                run_runner(args[0], args[1], budget=args[2], depth_bound=args[3])


if __name__ == "__main__":
    unittest.main()
