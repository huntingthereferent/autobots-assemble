"""Zero-trace fourth-coordinate systems: rank, gauge, and order-three/nine."""
import unittest
from itertools import product

from work.arc_like_maze.zero_trace_lift import (
    ZERO, ZeroTraceParameters, PointedSystem, PointedConjugacy,
    linear_certificate, trace_ranks, solve, classify, select_lift,
    transport_point, certify_zero_trace_family,
)
from work.arc_like_maze.variable_fourth_lift import FourthCoordinateParameters

F3=(0,1,2)
ORDER_THREE_ONLY=ZeroTraceParameters(1,(0,0,0),(0,0,1))
ORDER_NINE_ONLY=ZeroTraceParameters(1,(0,1,2),(0,0,1))
BOTH_ORDERS=ZeroTraceParameters(1,(1,0,2),(0,0,0))
THREE_COMPONENTS=ZeroTraceParameters(1,(0,0,0),(0,0,0))
NINE_COUPLING=(2,1,0,2,1,0,2,1,0)
REJECTED=(1,)+(0,)*8


class ZeroTraceTests(unittest.TestCase):
    def test_exact_complete_162_configuration_certificate(self):
        cert=certify_zero_trace_family()
        self.assertEqual(cert.status,"CLOSED_ZERO_TRACE_COHOMOLOGICAL_ORDER_CLASSIFICATION")
        self.assertEqual(cert.configurations,162)
        self.assertEqual(cert.graph_components,((1,144),(3,18)))
        self.assertEqual(cert.rank_histogram,(
            (1,3,12),(1,4,24),(1,5,36),(1,6,72),
            (3,3,2),(3,4,4),(3,5,4),(3,6,8),
        ))
        self.assertEqual((cert.admitted_combinations,cert.order_three_possible,
                          cert.order_nine_possible,cert.both_orders_possible,
                          cert.nontrivial_gauge_cases),
                         (22410,11106,12492,1188,12))

    def test_first_second_gain_have_exact_matching_histograms(self):
        for gain in (1,2):
            histogram={}
            for Q in product(F3,repeat=3):
                if sum(Q)%3:continue
                for j,k in product(F3,repeat=2):
                    p=ZeroTraceParameters(gain,Q,(0,j,k))
                    info=linear_certificate(p)
                    key=(info.component_count,info.rank)
                    histogram[key]=histogram.get(key,0)+1
            self.assertEqual(histogram,{(1,3):6,(1,4):12,(1,5):18,(1,6):36,
                                         (3,3):1,(3,4):2,(3,5):2,(3,6):4})

    def test_sometimes_lower_graph_has_three_independent_correction_constants(self):
        info=linear_certificate(THREE_COMPONENTS)
        self.assertEqual((info.component_count,info.rank),(3,3))
        self.assertEqual(len(info.coupling_basis),6)
        _,relative=trace_ranks(THREE_COMPONENTS)
        self.assertEqual(relative,0)
        self.assertEqual(classify(THREE_COMPONENTS,ZERO).possible_orders,(3,))

    def test_nonzero_correction_can_raise_order_three_to_nine(self):
        p=ORDER_NINE_ONLY
        self.assertEqual((linear_certificate(p).component_count,
                          linear_certificate(p).rank),(1,6))
        report=classify(p,NINE_COUPLING)
        self.assertEqual(report.possible_orders,(9,))
        with self.assertRaises(ValueError):
            select_lift(p,NINE_COUPLING,3)
        system=select_lift(p,NINE_COUPLING,9)
        self.assertEqual(system.order,9)
        for state in product(F3,repeat=5):
            third=system.power(state,3)
            self.assertEqual(third[:4],state[:4])
            self.assertNotEqual(third[4],state[4])
            self.assertEqual(system.centralizer(system.power(state,8)),state)

    def test_some_corrected_systems_remain_order_three(self):
        p=ORDER_THREE_ONLY
        self.assertEqual(classify(p,ZERO).possible_orders,(3,))
        system=select_lift(p,ZERO,3)
        for state in product(F3,repeat=5):
            third=system.centralizer(system.power(state,2))
            self.assertEqual(third,state)
        with self.assertRaises(ValueError):
            select_lift(p,ZERO,9)

    def test_same_fifth_coupling_can_support_both_cyclic_orders(self):
        p=BOTH_ORDERS
        self.assertEqual((linear_certificate(p).component_count,
                          linear_certificate(p).rank),(3,6))
        self.assertEqual(classify(p,ZERO).possible_orders,(3,9))
        three=select_lift(p,ZERO,3)
        nine=select_lift(p,ZERO,9)
        self.assertEqual(three.parameters,nine.parameters)
        self.assertEqual(three.fifth,nine.fifth)
        self.assertNotEqual(three.correction,nine.correction)
        for state in product(F3,repeat=5):
            self.assertEqual(three.centralizer(three.power(state,2)),state)
            self.assertNotEqual(nine.centralizer(nine.power(state,2)),state)
            self.assertEqual(nine.centralizer(nine.power(state,8)),state)

    def test_rejected_table_has_replayable_signed_cycle_obstruction(self):
        for p in (ORDER_THREE_ONLY,ORDER_NINE_ONLY,BOTH_ORDERS):
            values,witness=solve(p,REJECTED)
            self.assertIsNone(values)
            self.assertIsNotNone(witness)
            self.assertNotEqual(witness.first_voltage,witness.second_voltage)
            self.assertTrue(witness.verify(p,REJECTED))
            self.assertEqual(classify(p,REJECTED).status,"SIGNED_CYCLE_OBSTRUCTION")
            with self.assertRaises(ValueError):
                select_lift(p,REJECTED,3)

    def test_actual_generating_transformations_commute_with_admitted_corrections(self):
        examples=((ORDER_THREE_ONLY,ZERO,3),
                  (ORDER_NINE_ONLY,NINE_COUPLING,9),
                  (BOTH_ORDERS,ZERO,3),(BOTH_ORDERS,ZERO,9))
        for p,fifth,order in examples:
            system=select_lift(p,fifth,order)
            for depth in range(3,7):
                for state in product(F3,repeat=depth):
                    transformed=system.centralizer(state)
                    for generator in "AB":
                        self.assertEqual(
                            system.centralizer(system.step(state,generator)),
                            system.step(transformed,generator))

    def test_inverse_actions_and_dimensional_projection(self):
        examples=((ORDER_THREE_ONLY,ZERO,3),
                  (ORDER_NINE_ONLY,NINE_COUPLING,9),
                  (BOTH_ORDERS,ZERO,9))
        for p,q2,order in examples:
            system=select_lift(p,q2,order)
            for depth in range(3,7):
                for state in product(F3,repeat=depth):
                    for generator in "AB":
                        moved=system.step(state,generator)
                        self.assertEqual(system.inverse(moved,generator),state)
                        if depth>3:
                            self.assertEqual(system.step(state[:-1],generator),
                                             moved[:-1])
                    if depth>3:
                        self.assertEqual(system.centralizer(state[:-1]),
                                         system.centralizer(state)[:-1])

    def test_pointed_conjugacy_tracks_all_nine_exponent_factors(self):
        system=select_lift(BOTH_ORDERS,ZERO,9)
        root=PointedSystem(system,(0,0,0,0,0))
        marked=root
        factors=None
        points=set()
        for _ in range(9):
            points.add(marked.mark)
            move=transport_point(marked,1)
            factors=move if factors is None else factors.then(move)
            marked=move.target
        self.assertEqual(marked,root)
        self.assertEqual(len(points),9)
        self.assertEqual(factors.exponents,(1,)*9)
        self.assertEqual(factors.inverse().exponents,(8,)*9)

    def test_marked_three_turn_and_nine_turn_endpoints_are_distinct(self):
        p=BOTH_ORDERS
        three=PointedSystem(select_lift(p,ZERO,3),(0,0,0,0,0))
        nine=PointedSystem(select_lift(p,ZERO,9),(0,0,0,0,0))
        self.assertEqual(three.system.fifth,nine.system.fifth)
        a=transport_point(three,1)
        b=transport_point(a.target,1)
        c=transport_point(b.target,1)
        self.assertEqual(a.then(b).then(c).target,three)
        a=transport_point(nine,1)
        b=transport_point(a.target,1)
        c=transport_point(b.target,1)
        self.assertNotEqual(a.then(b).then(c).target,nine)

    def test_old_order_nine_family_is_not_relabelled_as_zero_trace(self):
        with self.assertRaises(ValueError):
            ZeroTraceParameters(1,(0,1,1),(0,0,0))
        # Earlier order-nine parameters still exist independently.
        p=FourthCoordinateParameters(1,(0,1,1),(0,0,0))
        self.assertEqual(sum(p.quotient)%3,2)

    def test_reject_wrong_marks_bad_gains_and_false_cyclic_order(self):
        for gain in (0,True,3):
            with self.assertRaises(ValueError):
                ZeroTraceParameters(gain,(0,0,0),(0,0,0))
        with self.assertRaises(ValueError):
            ZeroTraceParameters(1,(0,0,True),(0,0,0))
        with self.assertRaises(ValueError):
            ZeroTraceParameters(1,(0,0,0),(1,0,0))
        with self.assertRaises(ValueError):
            classify(ORDER_THREE_ONLY,(0,)*8)
        with self.assertRaises(ValueError):
            select_lift(ORDER_THREE_ONLY,ZERO,True)
        with self.assertRaises(ValueError):
            select_lift(ORDER_THREE_ONLY,ZERO,9)
        s=select_lift(ORDER_THREE_ONLY,ZERO,3)
        with self.assertRaises(ValueError):
            PointedSystem(s,(0,0,0,0))
        root=PointedSystem(s,(0,0,0,0,0))
        with self.assertRaises(ValueError):
            PointedConjugacy(root,root,(1,))
        with self.assertRaises(ValueError):
            transport_point(root,3)
        with self.assertRaises(ValueError):
            s.centralizer((0,0))


if __name__=="__main__":
    unittest.main(verbosity=2)
