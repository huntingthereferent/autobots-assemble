"""Fifth-coordinate lift: exactly 81 admitted coupling tables per gain."""
import unittest
from itertools import product

from work.arc_like_maze.fifth_coordinate_lift import (
    BASE, FifthCoordinateSystem, PointedFifthSystem, PointedFifthConjugacy,
    classify_fifth, linear_constraint_rank, lower_rules, voltage_graph,
    transport_point,
)
from work.arc_like_maze.higher_coupling_lift import HigherCouplingSystem

F3=(0,1,2)
EXAMPLE=tuple((z+y*y)%3 for z,y in product(F3,repeat=2))
OBSTRUCTED=tuple((z*y)%3 for z,y in product(F3,repeat=2))


class FifthCoordinateLiftTests(unittest.TestCase):
    def test_all_19683_couplings_for_each_gain_have_exact_classification(self):
        for gain in (1,2):
            counts={'admitted':0,'obstructed':0,'reads_y':0}
            for q in product(F3,repeat=9):
                result=classify_fifth(gain,q)
                if result.order is None:
                    counts['obstructed']+=1
                    self.assertEqual(result.status,"COHOMOLOGICAL_OBSTRUCTION")
                    self.assertTrue(result.obstruction.verify(gain,q))
                else:
                    counts['admitted']+=1
                    self.assertEqual(result.order,9)
                    if len(set(result.fiber_function))>1:
                        counts['reads_y']+=1
            self.assertEqual(counts,{'admitted':81,'obstructed':19602,
                                     'reads_y':72})

    def test_exact_linear_constraint_rank_is_five_for_both_lower_systems(self):
        self.assertEqual(linear_constraint_rank(1),5)
        self.assertEqual(linear_constraint_rank(2),5)
        self.assertEqual(3**(9-linear_constraint_rank(1)),81)

    def test_explicit_nonconstant_higher_rule_really_depends_on_x3(self):
        self.assertEqual(EXAMPLE,(0,1,1,1,2,2,2,0,0))
        for gain in (1,2):
            result=classify_fifth(gain,EXAMPLE)
            self.assertEqual(result.status,"ORDER_NINE_CENTRALIZER")
            self.assertEqual(result.slope,1)
            self.assertEqual(result.fiber_function,(0,1,1))
            self.assertIsNone(result.obstruction)

    def test_two_predecessor_grammar_and_old_fourth_coordinate_system_embed(self):
        for gain in (1,2):
            q0,q1,alpha=lower_rules(gain)
            self.assertEqual(q0,BASE[gain])
            self.assertEqual(q1,tuple((z+alpha[v])**2%3
                                     for v,z in product(F3,repeat=2)))
            old=HigherCouplingSystem(q0,gain,q1)
            new=FifthCoordinateSystem(gain,EXAMPLE)
            for depth in (3,4):
                for state in product(F3,repeat=depth):
                    for action in 'AB':
                        self.assertEqual(old.step(state,action),
                                         new.step(state,action))
            self.assertEqual(new.world().rule(2),EXAMPLE)
            self.assertEqual(new.world().rule(9),(0,)*9)

    def test_all_admitted_nonconstant_fifth_couplings_commute_with_both_generators(self):
        for gain in (1,2):
            for slope,f in product(F3,product(F3,repeat=3)):
                q=tuple((slope*z+f[y])%3 for z,y in product(F3,repeat=2))
                sys=FifthCoordinateSystem(gain,q)
                for depth in (3,4,5,6):
                    for state in product(F3,repeat=depth):
                        moved=sys.generator_lift(state)
                        for operation in 'AB':
                            self.assertEqual(
                                sys.generator_lift(sys.step(state,operation)),
                                sys.step(moved,operation))

    def test_signed_voltage_obstruction_is_literal_and_replayable(self):
        for gain in (1,2):
            report=classify_fifth(gain,OBSTRUCTED)
            self.assertIsNone(report.order)
            self.assertIsNotNone(report.obstruction)
            self.assertTrue(report.obstruction.verify(gain,OBSTRUCTED))
            self.assertNotEqual(report.obstruction.first_voltage,
                                report.obstruction.second_voltage)
            with self.assertRaises(ValueError):
                FifthCoordinateSystem(gain,OBSTRUCTED).generator_lift(
                    (0,0,0,0,0))

    def test_independent_graph_potential_matches_constructed_formula(self):
        for gain in (1,2):
            _,_,alpha=lower_rules(gain)
            for slope,f in product(F3,product(F3,repeat=3)):
                q=tuple((slope*z+f[y])%3 for z,y in product(F3,repeat=2))
                potentials,obstruction=voltage_graph(gain,q)
                self.assertIsNone(obstruction)
                self.assertEqual(len(potentials),27)
                for v,z,y in product(F3,repeat=3):
                    self.assertEqual(potentials[(v,z,y)],
                       (slope*(z+alpha[v])+f[y]-f[0])%3)

    def test_all_admitted_maps_have_order_nine_not_twenty_seven(self):
        for gain in (1,2):
            for slope,f in product(F3,product(F3,repeat=3)):
                q=tuple((slope*z+f[y])%3 for z,y in product(F3,repeat=2))
                sys=FifthCoordinateSystem(gain,q)
                for state in product(F3,repeat=5):
                    third=sys.apply_power(state,3)
                    self.assertEqual(third[:3],state[:3])
                    self.assertEqual(third[3],(state[3]+2)%3)
                    self.assertEqual(
                        sys.generator_lift(sys.apply_power(state,8)),state)

    def test_projection_of_fifth_lift_is_prior_order_nine_centralizer(self):
        for gain in (1,2):
            q0,q1,_=lower_rules(gain)
            old=HigherCouplingSystem(q0,gain,q1)
            new=FifthCoordinateSystem(gain,EXAMPLE)
            for state in product(F3,repeat=5):
                self.assertEqual(new.generator_lift(state)[:4],
                                 old.generator_lift(state[:4]))
                self.assertEqual(new.apply_power(state,3)[3],
                                 old.apply_power(state[:4],3)[3])

    def test_generator_inverse_and_truncation_remain_exact(self):
        for gain in (1,2):
            for coupling in (EXAMPLE,OBSTRUCTED,(0,)*9):
                sys=FifthCoordinateSystem(gain,coupling)
                for depth in range(3,7):
                    for state in product(F3,repeat=depth):
                        for op in 'AB':
                            nxt=sys.step(state,op)
                            self.assertEqual(sys.inverse(nxt,op),state)
                            if depth>3:
                                self.assertEqual(nxt[:-1],
                                                 sys.step(state[:-1],op))
                        if sys.analysis.order is not None and depth>3:
                            self.assertEqual(sys.generator_lift(state)[:-1],
                                             sys.generator_lift(state[:-1]))

    def test_pointed_order_nine_orbit_requires_five_coordinate_marks(self):
        sys=FifthCoordinateSystem(1,EXAMPLE)
        root=PointedFifthSystem(sys,(0,0,0,0,0))
        path=None
        current=root
        marks=set()
        for step in range(9):
            marks.add(current.mark)
            edge=transport_point(current,1)
            path=edge if path is None else path.then(edge)
            current=edge.target
            if step==2:
                self.assertNotEqual(current,root)
                self.assertEqual(current.mark[3],2)
        self.assertEqual(current,root)
        self.assertEqual(len(marks),9)
        self.assertEqual(path.exponents,(1,)*9)
        self.assertEqual(path.source,path.target)

    def test_pointed_inverse_and_composition_keep_every_factor(self):
        sys=FifthCoordinateSystem(2,EXAMPLE)
        root=PointedFifthSystem(sys,(1,2,0,1,2))
        f=transport_point(root,2)
        g=transport_point(f.target,5)
        fg=f.then(g)
        self.assertEqual(fg.exponents,(2,5))
        inverse=fg.inverse()
        self.assertEqual(inverse.exponents,(4,7))
        self.assertEqual(inverse.source,fg.target)
        for state in product(F3,repeat=5):
            self.assertEqual(inverse.map_state(fg.map_state(state)),state)

    def test_mark_guard_rejects_wrong_endpoint_and_noncomposable_paths(self):
        sys=FifthCoordinateSystem(1,EXAMPLE)
        start=PointedFifthSystem(sys,(0,0,0,0,0))
        f=transport_point(start,1)
        with self.assertRaises(ValueError):
            PointedFifthConjugacy(start,start,(1,))
        with self.assertRaises(ValueError):
            PointedFifthConjugacy(start,start,(9,))
        with self.assertRaises(ValueError):
            PointedFifthConjugacy(start,start,())
        with self.assertRaises(ValueError):
            f.then(f)
        with self.assertRaises(ValueError):
            transport_point(start,9)

    def test_zero_upper_fifth_coupling_still_has_order_nine(self):
        for gain in (1,2):
            sys=FifthCoordinateSystem(gain,(0,)*9)
            self.assertEqual(sys.analysis.order,9)
            self.assertEqual(sys.analysis.fiber_function,(0,0,0))
            for state in product(F3,repeat=5):
                self.assertEqual(sys.generator_lift(state)[4],state[4])

    def test_malformed_finite_field_inputs_are_not_silently_coerced(self):
        for invalid in ((0,)*8,(0,)*8+(True,),list((0,)*9)):
            with self.assertRaises(ValueError):
                FifthCoordinateSystem(1,invalid)
        with self.assertRaises(ValueError):
            lower_rules(True)
        with self.assertRaises(ValueError):
            classify_fifth(0,(0,)*9)
        with self.assertRaises(ValueError):
            PointedFifthSystem(FifthCoordinateSystem(1,EXAMPLE),(0,0,0,0))
        with self.assertRaises(ValueError):
            FifthCoordinateSystem(1,EXAMPLE).generator_lift((0,0))
        with self.assertRaises(ValueError):
            FifthCoordinateSystem(1,EXAMPLE).apply_power((0,0,0),True)


if __name__=='__main__':
    unittest.main(verbosity=2)
