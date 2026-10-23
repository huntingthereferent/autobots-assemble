import unittest
from work.arc_like_maze.math import World
from interfaces.math.arena import Challenge, adjudicate, scoreboard


class ArenaTests(unittest.TestCase):
    def test_mixed_challenges_are_scored_by_transitions(self):
        world = World(3)
        cases = (
            Challenge("skeptic", "deny transition", "A", (0, 0, 0)),
            Challenge("tracer", "predict transition", "A", (1, 0, 0)),
        )
        verdicts = adjudicate(world, cases)
        self.assertEqual(tuple(v.outcome for v in verdicts), ("CORRECTED", "SUPPORTED"))
        self.assertEqual(scoreboard(verdicts), {
            "agents_entered": 2, "challenges": 2, "corrected": 1, "supported": 1
        })

    def test_language_motive_does_not_change_verdict(self):
        world = World(3)
        verdicts = adjudicate(world, (
            Challenge("a", "I insist this is correct", "A", (0, 0, 0)),
            Challenge("b", "I disagree", "A", (0, 0, 0)),
        ))
        self.assertTrue(all(v.outcome == "CORRECTED" for v in verdicts))

    def test_correct_counterexample_is_supported(self):
        world = World(3, (0, 2, 1))
        challenge = Challenge("counterexample", "challenge default world", "ABB", world.apply("ABB"))
        self.assertEqual(adjudicate(world, (challenge,))[0].outcome, "SUPPORTED")


if __name__ == "__main__":
    unittest.main()
