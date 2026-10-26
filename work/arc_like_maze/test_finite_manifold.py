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

    def test_graph_return_is_not_permutation_return(self):
        m = FiniteTorus3()
        # A is a nontrivial lattice automorphism, so the graph returns
        # after one step even though the full state permutation does not.
        result = m.geometry_return_analysis("AAA")
        self.assertEqual(result["first_graph_return"], 1)
        self.assertEqual(result["first_permutation_return"], 3)
        self.assertEqual(result["first_graph_repeat"], (0, 1))
        self.assertEqual(result["first_permutation_repeat"], (0, 3))
        self.assertEqual(result["distinct_graphs"], 1)
        self.assertEqual(result["distinct_permutations"], 3)

    def test_b_has_exact_order_three(self):
        m = FiniteTorus3()
        for vertex in m.vertices():
            self.assertEqual(m.apply_word(vertex, "BBB"), vertex)
        self.assertEqual(
            [row["fixed_overlap"] for row in m.trace_geometry("BBBBBB")],
            [81, 27, 27, 81, 27, 27, 81],
        )
        result = m.geometry_return_analysis("BBBBBB")
        self.assertEqual(result["first_graph_return"], 3)
        self.assertEqual(result["first_permutation_return"], 3)
        self.assertEqual(result["distinct_graphs"], 3)
        self.assertEqual(result["distinct_permutations"], 3)

    def test_mixed_ab_longer_permutation_cycle(self):
        m = FiniteTorus3()
        # Every AB block is applied in the same left-to-right order as World.step.
        word = "AB" * 9
        trace = [m.geometry_return_analysis("AB" * n) for n in range(1, 10)]
        self.assertEqual([r["first_graph_return"] for r in trace[:2]], [None, None])
        self.assertEqual(trace[2]["first_graph_return"], 6)
        self.assertIsNone(trace[2]["first_permutation_return"])
        self.assertEqual(trace[-1]["first_permutation_return"], 18)
        self.assertEqual(m.permutation_signature(word), m.permutation_signature(""))
        self.assertNotEqual(m.permutation_signature("AB" * 3), m.permutation_signature(""))
        self.assertEqual(
            [m.geometry_comparison("B")["preserved_edges"],
             len(m.edges() & m.transported_edges_word("AB"))],
            [27, 27],
        )

    def test_exhaustive_action_closure(self):
        result = FiniteTorus3().action_closure()
        self.assertEqual(result["permutations"], 81)
        self.assertEqual(result["distinct_edge_geometries"], 3)
        self.assertEqual(result["reference_graph_stabilizer"], 27)
        self.assertEqual(result["overlap_distribution"], {27: 2, 81: 1})
        self.assertEqual(result["max_shortest_word_length"], 10)
        self.assertEqual(result["shortest_word_distribution"], {
            0: 1, 1: 2, 2: 4, 3: 6, 4: 10, 5: 14,
            6: 16, 7: 14, 8: 9, 9: 4, 10: 1,
        })

    def test_graph_stabilizer_is_normal_translation_group(self):
        result = FiniteTorus3().subgroup_structure()
        self.assertEqual(result["full_group_order"], 81)
        self.assertEqual(result["stabilizer_order"], 27)
        self.assertEqual(result["translation_order"], 27)
        self.assertTrue(result["stabilizer_equals_translations"])
        self.assertTrue(result["stabilizer_abelian"])
        self.assertTrue(result["stabilizer_normal"])
        self.assertEqual(result["index"], 3)

    def test_semidirect_product_shear_and_unique_normal_forms(self):
        result = FiniteTorus3().semidirect_product_structure()
        self.assertEqual(result["translation_order"], 27)
        self.assertTrue(result["complement_order_three"])
        self.assertTrue(result["conjugation_matches_shear"])
        self.assertEqual(result["shear_matrix_mod_3"],
                         ((1, 0, 0), (1, 1, 0), (0, 1, 1)))
        self.assertEqual(result["normal_form_count"], 81)
        self.assertTrue(result["unique_translation_times_b_power"])
        self.assertTrue(result["b_powers_intersect_translations_trivially"])
        self.assertTrue(result["a_is_translation"])

    def test_lower_central_series_and_center(self):
        result = FiniteTorus3().lower_central_structure()
        self.assertEqual(result["group_order"], 81)
        self.assertEqual(result["center_order"], 3)
        self.assertEqual(result["commutator_subgroup_order"], 9)
        self.assertEqual(result["lower_central_orders"], [81, 9, 3, 1])
        self.assertEqual(result["nilpotency_class"], 3)
        self.assertTrue(result["derived_is_abelian"])
        self.assertTrue(result["center_elements_are_translations"])

    def test_element_orders_and_exponent(self):
        result = FiniteTorus3().element_order_structure()
        self.assertEqual(result["group_order"], 81)
        self.assertEqual(result["order_distribution"], {1: 1, 3: 44, 9: 36})
        self.assertEqual(result["exponent"], 9)
        self.assertTrue(result["has_element_order_9"])
        self.assertFalse(result["has_element_order_27"])
        self.assertTrue(result["all_orders_divide_exponent"])

    def test_group_presentation_relations_and_normal_forms(self):
        result = FiniteTorus3().group_presentation_verification()
        self.assertTrue(result["generators_order_three"])
        self.assertTrue(result["translations_commute"])
        self.assertTrue(result["conjugation_relations"])
        self.assertEqual(result["normal_form_count"], 81)
        self.assertEqual(result["generated_by_a_b_count"], 81)
        self.assertTrue(result["normal_forms_equal_generated_group"])
        self.assertTrue(result["a_equals_x"])

    def test_four_coordinate_group_multiplication(self):
        m = FiniteTorus3()
        result = m.coordinate_group_verification()
        self.assertEqual(result["coordinate_count"], 81)
        self.assertTrue(result["faithful"])
        self.assertTrue(result["multiplication_matches_permutations"])
        self.assertTrue(result["identity_law"])
        self.assertTrue(result["closure"])
        self.assertEqual(
            m.coordinate_product((0, 0, 0, 1), (1, 0, 0, 0)),
            (1, 1, 0, 1),
        )
        self.assertEqual(
            m.coordinate_product((0, 0, 0, 2), (1, 0, 0, 0)),
            (1, 2, 1, 2),
        )

    def test_coordinate_inverse_commutator_conjugation(self):
        m = FiniteTorus3()
        identity = (0, 0, 0, 0)
        for element in ((0, 0, 0, 0), (1, 2, 0, 1), (2, 1, 2, 2)):
            inverse = m.coordinate_inverse(element)
            self.assertEqual(m.coordinate_product(element, inverse), identity)
            self.assertEqual(m.coordinate_product(inverse, element), identity)
        b = (0, 0, 0, 1)
        x = (1, 0, 0, 0)
        self.assertEqual(m.coordinate_conjugate(b, x), (1, 1, 0, 0))
        self.assertEqual(m.coordinate_commutator(b, x), (0, 1, 0, 0))
        result = m.coordinate_algebra_verification()
        self.assertTrue(result["inverse_laws"])
        self.assertTrue(result["commutators_are_translations"])
        self.assertTrue(result["conjugation_law"])
        self.assertEqual(result["distinct_commutator_values"], 9)

    def test_coordinate_lower_central_series_matches_permutations(self):
        result = FiniteTorus3().coordinate_lower_central_structure()
        self.assertEqual(result["center_order"], 3)
        self.assertEqual(result["derived_order"], 9)
        self.assertEqual(result["lower_central_orders"], (81, 9, 3, 1))
        self.assertEqual(result["nilpotency_class"], 3)
        self.assertTrue(result["matches_permutation_analysis"])
        self.assertEqual(result["center"], (
            (0, 0, 0, 0), (0, 0, 1, 0), (0, 0, 2, 0),
        ))

    def test_audit_independent_coordinate_group_laws(self):
        m = FiniteTorus3()
        from itertools import product
        coordinates = tuple(product(range(3), repeat=4))
        identity = (0, 0, 0, 0)
        # All 81^2 products must admit both-sided cancellation.
        for a in coordinates:
            inverse = m.coordinate_inverse(a)
            self.assertEqual(m.coordinate_product(a, inverse), identity)
            self.assertEqual(m.coordinate_product(inverse, a), identity)
            for b in coordinates:
                self.assertEqual(
                    m.coordinate_product(inverse, m.coordinate_product(a, b)),
                    b,
                )
                self.assertEqual(
                    m.coordinate_product(m.coordinate_product(b, a), inverse),
                    b,
                )
        # Explicit noncommutativity witness prevents an accidental
        # abelian implementation from passing the group-law tests.
        x = (1, 0, 0, 0)
        b = (0, 0, 0, 1)
        self.assertNotEqual(
            m.coordinate_product(x, b),
            m.coordinate_product(b, x),
        )
        self.assertTrue(m.coordinate_algebra_verification()["conjugation_law"])

    def test_periodic_neighborhood(self):
        m = FiniteTorus3()
        self.assertEqual(len(m.neighbors((0, 0, 0))), 6)
        self.assertIn((2, 0, 0), m.neighbors((0, 0, 0)))


if __name__ == "__main__":
    unittest.main()
