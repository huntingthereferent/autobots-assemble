import unittest

from selector import rank_actions, score_action


class WitnessCompressionSelectorTests(unittest.TestCase):
    def test_fm004_action2_separates_both_live_models(self):
        score = score_action(
            {
                "H_flip": ("XXX", "..X", "X.X"),
                "H_rotate": ("X.X", "X..", "XXX"),
            }
        )
        self.assertEqual(score["separated_pairs"], 1)
        self.assertEqual(score["total_pairs"], 1)
        self.assertEqual(score["separation_rate"], 1.0)
        self.assertEqual(score["coverage"], 1.0)

    def test_missing_prediction_does_not_fake_discrimination(self):
        score = score_action(
            {
                "H_flip": None,
                "H_rotate": ("X.X", "X..", "XXX"),
            }
        )
        self.assertEqual(score["separated_pairs"], 0)
        self.assertEqual(score["unknown_pairs"], 1)
        self.assertEqual(score["separation_rate"], 0.0)

    def test_rank_prefers_action_that_splits_more_candidate_pairs(self):
        ranked = rank_actions(
            {
                "ACTION_A": {
                    "H1": "x",
                    "H2": "x",
                    "H3": "y",
                },
                "ACTION_B": {
                    "H1": "x",
                    "H2": "y",
                    "H3": "z",
                },
            }
        )
        self.assertEqual(ranked[0]["action"], "ACTION_B")
        self.assertEqual(ranked[0]["separated_pairs"], 3)

    def test_goal_progress_is_only_a_tiebreaker(self):
        ranked = rank_actions(
            {
                "informative": {"H1": "x", "H2": "y"},
                "goalish": {"H1": "x", "H2": "x"},
            },
            goal_progress={"informative": 0.0, "goalish": 100.0},
        )
        self.assertEqual(ranked[0]["action"], "informative")


if __name__ == "__main__":
    unittest.main()
