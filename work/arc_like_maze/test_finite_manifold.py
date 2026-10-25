"""Checks for the finite cubical torus and its original World adapter."""
import unittest
from work.arc_like_maze.finite_manifold import FiniteTorus3
from work.arc_like_maze.math import World


class FiniteManifoldTests(unittest.TestCase):
    def test_cell_counts_and_euler(self):
        m = FiniteTorus3()
        self.assertEqual(m.f_vector(), (27, 81, 81, 27))
        self.assertEqual(m.verify()["euler_characteristic"], 0)
        self.assertTrue(m.verify()["degree_six"])

    def test_world_transition_is_exact(self):
        m = FiniteTorus3()
        w = World(3, (0, 1, 2))
        for v in m.vertices():
            for action in "AB":
                self.assertEqual(m.transition(v, action), w.step(v, action))
        self.assertTrue(m.verify()["transition_closed"])
        self.assertTrue(m.verify()["transition_bijective"])

    def test_periodic_neighborhood(self):
        m = FiniteTorus3()
        self.assertEqual(len(m.neighbors((0, 0, 0))), 6)
        self.assertIn((2, 0, 0), m.neighbors((0, 0, 0)))


if __name__ == "__main__":
    unittest.main()
