"""Selected centralizer maps may compose without commuting with one another."""
import unittest
from itertools import product

from work.arc_like_maze.pointed_coupling_classification import (
    CouplingLaw, select_symmetry, inspect_coupling,
)
from work.arc_like_maze.mixed_centralizer_composition import (
    GaugeTranslation, GaugeFactor, SymmetryFactor, PointedLaw,
    MixedPointedArrow, component_action, compare_selected, mixed_arrow,
    certify_component_composition,
)

F3=(0,1,2)
ZERO=(0,)*9
CYCLE=CouplingLaw(1,(1,0,2),(0,0,0),ZERO)
FIXED=CouplingLaw(1,(0,0,0),(0,0,0),ZERO)
CONNECTED=CouplingLaw(1,(0,0,0),(0,0,1),ZERO)
ORDER_NINE=CouplingLaw(1,(0,1,1),(0,0,0),ZERO)


class MixedCompositionTests(unittest.TestCase):
    def test_complete_family_component_action_and_commutation_counts(self):
        c=certify_component_composition()
        self.assertEqual(c.status,"EXACT_SELECTED_CENTRALIZER_COMPOSITION")
        self.assertEqual((c.configurations,c.connected,c.three_fixed,c.three_cyclic),
                         (486,468,6,12))
        self.assertEqual((c.ordered_gauge_pairs,c.commuting_pairs,
                          c.noncommuting_pairs),(17334,9558,7776))

    def test_three_component_action_types_have_replayable_permutations(self):
        cases=((CONNECTED,"CONNECTED",1),
               (FIXED,"COMPONENTWISE_FIXED",3),
               (CYCLE,"COMPONENT_CYCLE",3),
               (ORDER_NINE,"CONNECTED",1))
        for law,label,count in cases:
            a=component_action(law)
            self.assertEqual((a.action_type,a.component_count),(label,count))
            self.assertEqual(sorted(a.permutation),list(range(count)))
            self.assertEqual(len(a.component_of),27)
        self.assertEqual(component_action(CYCLE).permutation,(2,0,1))

    def test_order_three_and_order_nine_lifts_of_one_law_do_not_commute(self):
        first=select_symmetry(CYCLE,3)
        second=select_symmetry(CYCLE,9)
        self.assertEqual(first.law,second.law)
        self.assertNotEqual(first.correction,second.correction)
        result=compare_selected(first,second)
        self.assertFalse(result.commutes)
        self.assertTrue(result.replay())
        self.assertEqual(result.witness,(0,0,0,0,0))
        self.assertNotEqual(result.first_after_second,
                            result.second_after_first)
        self.assertEqual(result.first_after_second[:4],
                         result.second_after_first[:4])
        self.assertEqual((result.first_after_second[4]-
                          result.second_after_first[4])%3,2)

    def test_different_selected_lifts_both_centralize_original_generators(self):
        for law in (CYCLE,FIXED,CONNECTED,ORDER_NINE):
            report=inspect_coupling(law)
            for constants in ((0,)*report.component_count,
                              (1,)*report.component_count):
                order=3 if 3 in report.possible_orders else 9
                try: selected=select_symmetry(law,order,constants)
                except ValueError:
                    selected=select_symmetry(law,9,constants)
                for state in product(F3,repeat=5):
                    for generator in 'AB':
                        self.assertEqual(
                            selected.centralizer(selected.step(state,generator)),
                            selected.step(selected.centralizer(state),generator))

    def test_connected_graph_gauge_choices_always_commute(self):
        law=ORDER_NINE
        selections=[select_symmetry(law,9,(r,)) for r in F3]
        for a,b in product(selections,repeat=2):
            cert=compare_selected(a,b)
            self.assertTrue(cert.commutes)
            self.assertIsNone(cert.witness)
            self.assertEqual(cert.differences,(0,)*27)
        self.assertEqual(selections[0].law,selections[2].law)

    def test_fixed_components_gauge_choices_always_commute(self):
        law=FIXED
        a=select_symmetry(law,3,(0,1,2))
        b=select_symmetry(law,3,(2,1,0))
        cert=compare_selected(a,b)
        self.assertTrue(cert.commutes)
        self.assertEqual(cert.component_permutation,(0,1,2))
        self.assertEqual(cert.relative_gauge,(2,0,1))

    def test_cycling_components_relative_diagonal_gauge_commutes(self):
        law=CYCLE
        a=select_symmetry(law,3,(0,0,0))
        b=select_symmetry(law,3,(1,1,1))
        cert=compare_selected(a,b)
        self.assertTrue(cert.commutes)
        self.assertEqual(cert.relative_gauge,(1,1,1))
        self.assertEqual(len(set(cert.relative_gauge)),1)

    def test_vertical_gauge_commutes_with_original_generators_at_all_depths(self):
        for law in (CYCLE,FIXED,CONNECTED,ORDER_NINE):
            count=component_action(law).component_count
            for c in product(F3,repeat=count):
                gauge=GaugeTranslation(law,c)
                for depth in (3,4,5,6):
                    for x in product(F3,repeat=depth):
                        for generator in 'AB':
                            self.assertEqual(
                                gauge.map_state(law.world().step(x,generator)),
                                law.world().step(gauge.map_state(x),generator))
                        self.assertEqual(
                            gauge.inverse().map_state(gauge.map_state(x)),x)

    def test_cycling_component_conjugation_performs_actual_permutation(self):
        law=CYCLE
        selected=select_symmetry(law,9,(0,0,1))
        structure=component_action(law)
        gauge=GaugeTranslation(law,(0,0,1))
        inverse_perm=[0]*3
        for old,new in enumerate(structure.permutation):
            inverse_perm[new]=old
        shifted=GaugeTranslation(law,tuple(gauge.constants[inverse_perm[i]]
                                          for i in range(3)))
        for state in product(F3,repeat=5):
            lhs=selected.centralizer(gauge.map_state(state))
            rhs=shifted.map_state(selected.centralizer(state))
            self.assertEqual(lhs,rhs)

    def test_two_noncommuting_symmetries_still_form_valid_mixed_pointed_arrows(self):
        a=select_symmetry(CYCLE,3)
        b=select_symmetry(CYCLE,9)
        start=PointedLaw(CYCLE,(0,0,0,0,0))
        f=SymmetryFactor(a,1)
        g=SymmetryFactor(b,1)
        first=mixed_arrow(start,(f,))
        second=mixed_arrow(first.target,(g,))
        composed=first.then(second)
        direct=mixed_arrow(start,(f,g))
        self.assertEqual(composed,direct)
        self.assertEqual(composed.factors,(f,g))
        self.assertNotEqual(
            composed.target,mixed_arrow(start,(g,f)).target)
        self.assertEqual(composed.inverse().source,composed.target)
        self.assertEqual(composed.then(composed.inverse()).target,start)
        for state in product(F3,repeat=5):
            self.assertEqual(composed.inverse().map_state(
                             composed.map_state(state)),state)

    def test_mixed_gauge_and_selected_factors_preserve_order_and_inverses(self):
        law=CYCLE
        selected=select_symmetry(law,9)
        root=PointedLaw(law,(0,0,0,0,0))
        f=SymmetryFactor(selected,1)
        g=GaugeFactor(GaugeTranslation(law,(0,1,2)))
        arrow=mixed_arrow(root,(f,g,f.inverse(),g.inverse()))
        self.assertEqual(arrow.factors,(f,g,f.inverse(),g.inverse()))
        self.assertEqual(arrow.inverse().inverse(),arrow)
        for state in product(F3,repeat=5):
            self.assertEqual(arrow.inverse().map_state(arrow.map_state(state)),
                             state)

    def test_mixed_arrow_rejects_mismatched_points_or_underlying_laws(self):
        law=CYCLE
        a=select_symmetry(law,3)
        root=PointedLaw(law,(0,0,0,0,0))
        step=mixed_arrow(root,(SymmetryFactor(a,1),))
        with self.assertRaises(ValueError):
            step.then(step)
        with self.assertRaises(ValueError):
            MixedPointedArrow(root,root,(SymmetryFactor(a,1),))
        other=PointedLaw(FIXED,root.mark)
        with self.assertRaises(ValueError):
            mixed_arrow(root,(SymmetryFactor(select_symmetry(FIXED,3),1),))
        with self.assertRaises(ValueError):
            MixedPointedArrow(root,other,(SymmetryFactor(a,0),))
        with self.assertRaises(ValueError):
            step.then(mixed_arrow(other,(SymmetryFactor(
                select_symmetry(FIXED,3),1),)))

    def test_different_laws_are_not_compared_as_if_equivalent(self):
        first=select_symmetry(CYCLE,3)
        second=select_symmetry(FIXED,3)
        with self.assertRaises(ValueError):
            compare_selected(first,second)
        with self.assertRaises(ValueError):
            GaugeTranslation(CYCLE,(1,))

    def test_false_exponents_and_non_finite_states_are_rejected(self):
        a=select_symmetry(CYCLE,3)
        for bad in (3,True,-1,4):
            with self.assertRaises(ValueError):
                SymmetryFactor(a,bad)
        with self.assertRaises(ValueError):
            PointedLaw(CYCLE,(0,0,0,True,0))
        with self.assertRaises(ValueError):
            mixed_arrow(PointedLaw(CYCLE,(0,0,0,0,0)),())
        with self.assertRaises(ValueError):
            GaugeTranslation(CYCLE,(0,3,0))
        with self.assertRaises(ValueError):
            GaugeTranslation(CYCLE,(0,False,0))
        with self.assertRaises(ValueError):
            GaugeTranslation(CYCLE,(0,0,0)).map_state((0,0))

if __name__ == '__main__':
    unittest.main(verbosity=2)
