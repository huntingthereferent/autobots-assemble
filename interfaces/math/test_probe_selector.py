import unittest
from work.arc_like_maze.math import World
from interfaces.math.probe_selector import select_probe, record_observation, next_probe


class ProbeSelectorTests(unittest.TestCase):
    def setUp(self):
        self.a = World(3, (0, 1, 2))
        self.b = World(3, (0, 2, 1))

    def test_finds_shortest_distinguishing_probe(self):
        result = select_probe((self.a, self.b))
        self.assertEqual(result.actions, "ABB")
        self.assertNotEqual(self.a.apply(result.actions), self.b.apply(result.actions))

    def test_horizon_returns_unknown(self):
        self.assertIsNone(select_probe((self.a, self.b), 2).actions)

    def test_identical_worlds_no_distinction(self):
        self.assertIsNone(select_probe((self.a, self.a), 8).actions)

    def test_observation_eliminates_incompatible_world(self):
        outcome, following = next_probe((self.a, self.b), "ABB", self.a.apply("ABB"))
        self.assertEqual(outcome.surviving, (self.a,))
        self.assertEqual(outcome.eliminated, (self.b,))
        self.assertIsNone(following.actions)

    def test_unexplained_observation_preserves_failure(self):
        outcome, following = next_probe((self.a, self.b), "ABB", (9, 9, 9))
        self.assertEqual(outcome.surviving, ())
        self.assertIsNone(following)

    def test_rejects_bad_inputs(self):
        with self.assertRaises(ValueError):
            select_probe(())
        with self.assertRaises(ValueError):
            select_probe((World(3), World(4)))
        with self.assertRaises(ValueError):
            record_observation((self.a,), "C", (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
