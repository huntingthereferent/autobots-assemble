import unittest
from work.arc_like_maze.math import World
from interfaces.math.world_probe import compare_paths, oscillate


class WorldProbeTests(unittest.TestCase):
    def test_identical_worlds_do_not_diverge(self):
        result = compare_paths(World(3), World(3), "ABABBA")
        self.assertIsNone(result.first_divergence)
        self.assertEqual(result.divergent_steps, ())

    def test_worlds_diverge_on_source_defined_transition(self):
        result = compare_paths(World(3, (0, 1, 2)), World(3, (0, 2, 1)), "ABB")
        self.assertEqual(result.first_divergence, 3)
        self.assertNotEqual(result.reference[-1], result.candidate[-1])

    def test_invalid_actions_are_rejected(self):
        with self.assertRaises(ValueError):
            compare_paths(World(3), World(3), "AC")

    def test_different_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            compare_paths(World(3), World(4), "AB")

    def test_multiple_probes(self):
        results = oscillate(World(3), World(3), ("A", "B"))
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
