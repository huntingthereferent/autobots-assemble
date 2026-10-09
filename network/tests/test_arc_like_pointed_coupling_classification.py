"""Witness-preserving classification of both zero/nonzero-trace fifth lifts."""
import unittest
from itertools import product

from work.arc_like_maze.pointed_coupling_classification import (
    CouplingLaw, CycleWitness, AdmissionCertificate, SelectedSymmetry,
    PointedSystem, PointedConjugacy, inspect_coupling, select_symmetry,
    transport_point, reconcile_families,
)
from work.arc_like_maze import zero_trace_lift as zero
from work.arc_like_maze import variable_fourth_lift as nonzero

F3=(0,1,2)
ZERO=(0,)*9
DEPENDENT=tuple((z+y*y)%3 for z,y in product(F3,repeat=2))
NONADMITTED=tuple((z*y)%3 for z,y in product(F3,repeat=2))
ZERO_THREE=CouplingLaw(1,(0,0,0),(0,0,1),ZERO)
ZERO_NINE=CouplingLaw(1,(0,1,2),(0,0,1),(2,1,0)*3)
ZERO_BOTH=CouplingLaw(1,(1,0,2),(0,0,0),ZERO)
NINE=CouplingLaw(1,(0,1,1),(0,0,0),DEPENDENT)


class UnifiedPointedCouplingTests(unittest.TestCase):
    def test_family_certificate_recovers_both_proved_disjoint_branches(self):
        result=reconcile_families()
        self.assertEqual(result.status,"RECONCILED_POINTED_COHOMOLOGICAL_FAMILIES")
        self.assertEqual((result.zero_trace_configurations,
                          result.nonzero_trace_configurations), (162,324))
        self.assertEqual(result.fourth_coordinate_configurations,486)
        self.assertEqual(result.admitted_coupling_combinations,30510)
        self.assertEqual((result.order_three_possible,
                          result.order_nine_possible,
                          result.both_orders_possible),(11106,20592,1188))
        self.assertEqual((result.component_one_configurations,
                          result.component_three_configurations),(468,18))

    def test_all_486_configs_keep_rank_and_connectedness_with_zero_coupling(self):
        ranks={3:0,4:0,5:0,6:0,7:0}
        branch_counts={"ZERO_TRACE":0,"NONZERO_TRACE":0}
        for g in (1,2):
            for Q in product(F3,repeat=3):
                for j,k in product(F3,repeat=2):
                    spec=CouplingLaw(g,Q,(0,j,k),ZERO)
                    r=inspect_coupling(spec)
                    self.assertTrue(r.admitted)
                    self.assertEqual(r.branch,spec.branch)
                    self.assertEqual(r.admitted_tables_for_configuration,
                                     3**(9-r.constraint_rank))
                    self.assertEqual(len(r.normalized_correction),27)
                    self.assertEqual(len(r.component_index),27)
                    self.assertEqual(r.component_count,len(set(r.component_index)))
                    self.assertIn(r.possible_orders,((3,),(9,),(3,9)))
                    ranks[r.constraint_rank]+=1
                    branch_counts[r.branch]+=1
        self.assertEqual(branch_counts,{"ZERO_TRACE":162,"NONZERO_TRACE":324})
        self.assertEqual(ranks,{3:14,4:28,5:100,6:128,7:216})

    def test_preserve_zero_trace_available_orders_and_graph_components(self):
        examples=((ZERO_THREE,(3,),1),(ZERO_NINE,(9,),1),
                  (ZERO_BOTH,(3,9),3))
        for law,orders,components in examples:
            result=inspect_coupling(law)
            self.assertTrue(result.admitted)
            self.assertEqual((result.branch,result.component_count,
                              result.possible_orders),
                             ("ZERO_TRACE",components,orders))
            older=zero.classify(law.parameters,law.fifth)
            self.assertEqual((result.constraint_rank,result.possible_orders),
                             (older.rank,older.possible_orders))

    def test_nonzero_trace_admitted_and_rejected_reports_preserve_source_proofs(self):
        accepted=inspect_coupling(NINE)
        self.assertEqual(accepted.branch,"NONZERO_TRACE")
        self.assertTrue(accepted.admitted)
        self.assertEqual(accepted.component_count,1)
        self.assertEqual(accepted.possible_orders,(9,))
        self.assertIsNone(accepted.obstruction)
        old=nonzero.classify(NINE.parameters,NINE.fifth)
        self.assertEqual(accepted.constraint_rank,old.rank)
        self.assertEqual(accepted.admitted_tables_for_configuration,3**(9-old.rank))
        blocked=inspect_coupling(CouplingLaw(1,(0,1,1),(0,0,0),NONADMITTED))
        self.assertFalse(blocked.admitted)
        self.assertEqual(blocked.possible_orders,())
        self.assertIsNone(blocked.normalized_correction)
        self.assertTrue(blocked.obstruction.verify())
        self.assertIsInstance(blocked.obstruction.original,nonzero.CycleObstruction)

    def test_zero_trace_obstruction_preserves_original_signed_edge_witness(self):
        spec=CouplingLaw(1,(0,0,0),(0,0,1),(1,)+(0,)*8)
        report=inspect_coupling(spec)
        self.assertFalse(report.admitted)
        self.assertEqual(report.branch,"ZERO_TRACE")
        self.assertTrue(report.obstruction.verify())
        self.assertIsInstance(report.obstruction.original,zero.CycleObstruction)
        self.assertNotEqual(report.obstruction.path_voltage_difference,0)
        original=zero.classify(spec.parameters,spec.fifth)
        self.assertEqual(report.obstruction.original.first_voltage,
                         original.obstruction.first_voltage)
        with self.assertRaises(ValueError):
            select_symmetry(spec,3)

    def test_same_world_law_has_different_three_nine_symmetries_not_new_worlds(self):
        three=select_symmetry(ZERO_BOTH,3)
        nine=select_symmetry(ZERO_BOTH,9)
        self.assertEqual(three.law,nine.law)
        self.assertEqual(three.law.world(),nine.law.world())
        self.assertNotEqual(three.correction,nine.correction)
        self.assertNotEqual(three.component_constants,nine.component_constants)
        self.assertEqual(three.order,3)
        self.assertEqual(nine.order,9)
        for state in product(F3,repeat=5):
            self.assertEqual(three.power(state,2),three.centralizer(three.centralizer(state)))
            self.assertEqual(three.centralizer(three.power(state,2)),state)
            self.assertEqual(nine.centralizer(nine.power(state,8)),state)
            self.assertNotEqual(nine.centralizer(nine.centralizer(
                nine.centralizer(state))),state)

    def test_explicit_component_constants_cannot_silently_change_order(self):
        report=inspect_coupling(ZERO_BOTH)
        candidates=[]
        for constants in product(F3,repeat=report.component_count):
            orders=[]
            for order in (3,9):
                try: orders.append(select_symmetry(ZERO_BOTH,order,constants))
                except ValueError: pass
            self.assertEqual(len(orders),1)
            candidates.append(orders[0])
        self.assertEqual(len(candidates),27)
        self.assertEqual({s.order for s in candidates},{3,9})
        with self.assertRaises(ValueError):
            select_symmetry(ZERO_BOTH,9,(0,))
        with self.assertRaises(ValueError):
            select_symmetry(ZERO_BOTH,9,(0,0,True))

    def test_selected_order_nine_matches_prior_implemented_state_map(self):
        chosen=select_symmetry(NINE,9)
        old=nonzero.VariableFourthSystem(NINE.parameters,NINE.fifth)
        self.assertEqual(chosen.component_constants,(0,))
        for depth in range(3,7):
            for state in product(F3,repeat=depth):
                self.assertEqual(chosen.centralizer(state),old.centralizer(state))
                for letter in 'AB':
                    self.assertEqual(chosen.step(state,letter),old.step(state,letter))
                    self.assertEqual(chosen.inverse_step(chosen.step(state,letter),letter),state)
                    self.assertEqual(
                        chosen.centralizer(chosen.step(state,letter)),
                        chosen.step(chosen.centralizer(state),letter))

    def test_selected_zero_trace_matches_previously_witnessed_correction(self):
        for law,order in ((ZERO_THREE,3),(ZERO_NINE,9),
                          (ZERO_BOTH,3),(ZERO_BOTH,9)):
            chosen=select_symmetry(law,order)
            previous=zero.select_lift(law.parameters,law.fifth,order)
            self.assertEqual(chosen.correction,previous.correction)
            for state in product(F3,repeat=5):
                self.assertEqual(chosen.centralizer(state),
                                 previous.centralizer(state))
                self.assertEqual(chosen.centralizer(chosen.power(state,order-1)),
                                 state)

    def test_gauge_constant_changes_point_not_the_admission_certificate(self):
        a=select_symmetry(NINE,9,(0,))
        b=select_symmetry(NINE,9,(1,))
        self.assertEqual(a.law,b.law)
        self.assertEqual(a.law.world(),b.law.world())
        self.assertEqual(a.correction[0]+1,(b.correction[0]))
        self.assertNotEqual(a.correction,b.correction)
        self.assertEqual(inspect_coupling(NINE).possible_orders,(9,))
        root_a=PointedSystem(a,(0,0,0,0,0))
        root_b=PointedSystem(b,(0,0,0,0,0))
        self.assertNotEqual(root_a,root_b)
        with self.assertRaises(ValueError):
            PointedConjugacy(root_a,root_b,(0,))

    def test_exact_distinguished_point_transport_for_both_orders(self):
        for law,order in ((ZERO_THREE,3),(ZERO_BOTH,9),(NINE,9)):
            chosen=select_symmetry(law,order)
            root=PointedSystem(chosen,(0,0,0,0,0))
            current=root
            aggregate=None
            marks=set()
            for _ in range(order):
                marks.add(current.mark)
                edge=transport_point(current,1)
                aggregate=edge if aggregate is None else aggregate.then(edge)
                current=edge.target
            self.assertEqual(current,root)
            self.assertEqual(len(marks),order)
            self.assertEqual(aggregate.exponents,(1,)*order)
            self.assertEqual(aggregate.inverse().exponents,
                             (order-1,)*order)
            for state in product(F3,repeat=5):
                self.assertEqual(aggregate.map_state(state),state)

    def test_pointed_composition_requires_matching_actual_selected_symmetry(self):
        root=PointedSystem(select_symmetry(ZERO_BOTH,3),(0,0,0,0,0))
        step=transport_point(root,1)
        different=PointedSystem(select_symmetry(ZERO_BOTH,9),
                                step.target.mark)
        with self.assertRaises(ValueError):
            PointedConjugacy(step.target,different,(0,))
        with self.assertRaises(ValueError):
            step.then(transport_point(root,1))
        self.assertEqual(step.then(step.inverse()).source,root)

    def test_obstructed_laws_cannot_be_promoted_or_forged_as_admitted(self):
        spec=CouplingLaw(1,(0,0,0),(0,0,1),(1,)+(0,)*8)
        bad=inspect_coupling(spec)
        with self.assertRaises(ValueError):
            SelectedSymmetry(spec,(0,)*27,(0,),3)
        with self.assertRaises(ValueError):
            AdmissionCertificate(spec,spec.branch,True,bad.component_count,
                bad.constraint_rank,bad.admitted_tables_for_configuration,
                (3,),(0,)*27,bad.component_index,bad.obstruction)
        with self.assertRaises(ValueError):
            AdmissionCertificate(spec,spec.branch,False,bad.component_count,
                bad.constraint_rank,bad.admitted_tables_for_configuration,
                (),None,bad.component_index,None)

    def test_invalid_inputs_and_wrong_order_do_not_change_existing_law(self):
        for invalid in (True,0,3):
            with self.assertRaises(ValueError):
                CouplingLaw(invalid,(0,0,0),(0,0,0),ZERO)
        with self.assertRaises(ValueError):
            CouplingLaw(1,(0,0,True),(0,0,0),ZERO)
        with self.assertRaises(ValueError):
            CouplingLaw(1,(0,0,0),(1,0,0),ZERO)
        with self.assertRaises(ValueError):
            CouplingLaw(1,(0,0,0),(0,0,0),(0,)*8)
        with self.assertRaises(ValueError):
            select_symmetry(NINE,3)
        with self.assertRaises(ValueError):
            select_symmetry(NINE,True)
        s=select_symmetry(NINE,9)
        with self.assertRaises(ValueError):
            s.power((0,0,0),9)
        with self.assertRaises(ValueError):
            PointedSystem(s,(0,0,0,0))
        with self.assertRaises(ValueError):
            s.centralizer((0,0))


if __name__ == '__main__':
    unittest.main(verbosity=2)
