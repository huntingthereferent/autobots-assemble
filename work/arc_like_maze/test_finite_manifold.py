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

    def test_a_preserves_edges_b_does_not(self):
        m = FiniteTorus3()
        for vertex in m.vertices():
            for neighbor in m.neighbors(vertex):
                self.assertIn(m.transition(neighbor, "A"), m.neighbors(m.transition(vertex, "A")))
        source = (0, 0, 0)
        adjacent = (0, 1, 0)
        self.assertIn(adjacent, m.neighbors(source))
        self.assertNotIn(
            m.transition(adjacent, "B"),
            m.neighbors(m.transition(source, "B")),
        )

    def test_transported_geometry(self):
        m = FiniteTorus3()
        a = m.geometry_comparison("A")
        b = m.geometry_comparison("B")
        self.assertEqual(a["original_edges"], 81)
        self.assertEqual(a["lost_edges"], 0)
        self.assertTrue(a["is_graph_automorphism"])
        self.assertEqual(b["transported_edges"], 81)
        self.assertGreater(b["lost_edges"], 0)
        self.assertEqual(b["lost_edges"], b["introduced_edges"])
        self.assertFalse(b["is_graph_automorphism"])

    def test_word_trace_and_return(self):
        m = FiniteTorus3()
        self.assertEqual(m.apply_word((0, 0, 0), "AAB"), World(3).apply("AAB"))
        trace = m.trace_geometry("AABABB")
        self.assertEqual(len(trace), 7)
        self.assertEqual(trace[0]["fixed_overlap"], 81)
        self.assertEqual(trace[1]["fixed_overlap"], 81)
        self.assertEqual(trace[2]["fixed_overlap"], 81)
        self.assertEqual(trace[3]["fixed_overlap"], 27)
        self.assertTrue(all(row["edges"] == 81 for row in trace))
        self.assertEqual(m.transported_edges_word(""), m.edges())
        with self.assertRaises(ValueError):
            m.apply_word((0, 0, 0), "AC")

    def test_periodic_neighborhood(self):
        m = FiniteTorus3()
        self.assertEqual(len(m.neighbors((0, 0, 0))), 6)
        self.assertIn((2, 0, 0), m.neighbors((0, 0, 0)))


if __name__ == "__main__":
    unittest.main()
