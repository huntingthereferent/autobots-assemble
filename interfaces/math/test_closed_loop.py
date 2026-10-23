import unittest
from work.arc_like_maze.math import World
from interfaces.math.closed_loop import run, finite_world_executor


class ClosedLoopTests(unittest.TestCase):
    def setUp(self):
        self.a = World(3, (0, 1, 2))
        self.b = World(3, (0, 2, 1))

    def test_selects_and_eliminates_using_observation(self):
        result = run((self.a, self.b), finite_world_executor(self.a))
        self.assertEqual(result.status, "INDISTINGUISHABLE_WITHIN_HORIZON")
        self.assertEqual(result.survivors, (self.a,))
        self.assertEqual(result.rounds[0].probe, "ABB")
        self.assertEqual(result.rounds[0].eliminated_count, 1)

    def test_unknown_world_exhausts_models(self):
        result = run((self.a, self.b), lambda actions: (9, 9, 9))
        self.assertEqual(result.status, "MODEL_SET_EXHAUSTED")
        self.assertEqual(result.survivors, ())

    def test_zero_round_limit(self):
        result = run((self.a, self.b), finite_world_executor(self.a), max_rounds=0)
        self.assertEqual(result.status, "ROUND_LIMIT")
        self.assertEqual(result.rounds, ())

    def test_executor_dimension_check(self):
        with self.assertRaises(ValueError):
            run((self.a, self.b), lambda actions: (0,))

    def test_identical_candidates_need_no_execution(self):
        def forbidden(actions):
            raise AssertionError("should not execute")
        result = run((self.a, self.a), forbidden)
        self.assertEqual(result.status, "INDISTINGUISHABLE_WITHIN_HORIZON")


if __name__ == "__main__":
    unittest.main()
