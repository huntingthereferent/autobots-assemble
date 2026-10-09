"""Higher-coordinate cocycle: proved orders three and nine, or cycle obstruction."""
import unittest
from itertools import product

from work.arc_like_maze.higher_coupling_lift import (
    HigherCouplingSystem, PointedHigherSystem, PointedHigherConjugacy,
    classify_upper, signed_cycle_obstruction, transport_point,
)
from work.arc_like_maze.nonconstant_drift import solve_potential, NonconstantCouplingSystem

LOWER=(0,1,2,0,2,1,1,1,1)
LOWER_GAIN_TWO=(0,1,2,1,0,2,1,1,1)
ORDER_THREE=(0,1,2,1,2,0,0,1,2)
ORDER_NINE=(0,1,1,1,1,0,1,1,0)
OBSTRUCTED=(1,0,0,0,0,0,0,0,0)
ZERO=(0,)*9


class HigherCouplingLiftTests(unittest.TestCase):
    def test_complete_19683_table_classification_for_both_gains(self):
        for gain,lower in ((1,LOWER),(2,LOWER_GAIN_TWO)):
            tally={'ORDER_THREE_CENTRALIZER':0,'ORDER_NINE_CENTRALIZER':0,
                   'COHOMOLOGICAL_OBSTRUCTION':0}
            for q in product(range(3),repeat=9):
                analysis=classify_upper(lower,q,gain)
                tally[analysis.status]+=1
                if analysis.obstruction is not None:
                    self.assertTrue(analysis.obstruction.validate(lower,q,gain))
            self.assertEqual(tally,{'ORDER_THREE_CENTRALIZER':81,
                                    'ORDER_NINE_CENTRALIZER':162,
                                    'COHOMOLOGICAL_OBSTRUCTION':19440})

    def test_nonconstant_upper_rule_has_order_three_and_explicit_potential(self):
        sys=HigherCouplingSystem(LOWER,1,ORDER_THREE)
        cert=sys.analysis
        self.assertEqual(cert.status,'ORDER_THREE_CENTRALIZER')
        self.assertEqual(cert.order,3)
        self.assertEqual(cert.quotient,(0,1,2))
        self.assertEqual(cert.row_offsets,(0,0,2))
        self.assertEqual(cert.primitive,(0,1,2))
        self.assertEqual(cert.three_turn_trace,0)
        self.assertNotEqual(ORDER_THREE[3:6],ORDER_THREE[6:9])

    def test_quadratic_upper_rule_commutes_but_has_order_nine(self):
        sys=HigherCouplingSystem(LOWER,1,ORDER_NINE)
        cert=sys.analysis
        self.assertEqual((cert.status,cert.order,cert.three_turn_trace),
                         ('ORDER_NINE_CENTRALIZER',9,2))
        self.assertEqual((cert.quotient,cert.primitive),
                         ((0,1,1),(0,1,1)))
        for state in product(range(3),repeat=4):
            after_three=sys.apply_power(state,3)
            self.assertEqual(after_three[:3],state[:3])
            self.assertEqual(after_three[3],(state[3]+2)%3)
            self.assertEqual(sys.apply_power(state,6)[3],(state[3]+1)%3)
            self.assertEqual(sys.apply_power(state,0),state)
            self.assertEqual(sys.apply_power(state,8),
                             sys.apply_power(after_three,5))
        # Eight applications never pretend to be the identity.
        self.assertNotEqual(sys.apply_power((0,0,0,0),8),(0,0,0,0))
        after_nine=sys.generator_lift(sys.apply_power((0,0,0,0),8))
        self.assertEqual(after_nine,(0,0,0,0))

    def test_all_admitted_upper_cocycles_commute_with_both_generators(self):
        for upper in (ORDER_THREE,ORDER_NINE,ZERO):
            sys=HigherCouplingSystem(LOWER,1,upper)
            for dimension in range(3,7):
                for state in product(range(3),repeat=dimension):
                    moved=sys.generator_lift(state)
                    for letter in 'AB':
                        self.assertEqual(
                            sys.generator_lift(sys.step(state,letter)),
                            sys.step(moved,letter))

    def test_exact_cohomological_obstruction_carries_two_path_witnesses(self):
        cert=classify_upper(LOWER,OBSTRUCTED,1)
        self.assertEqual(cert.status,'COHOMOLOGICAL_OBSTRUCTION')
        self.assertIsNone(cert.order)
        self.assertIsNotNone(cert.obstruction)
        self.assertNotEqual(cert.obstruction.voltage_a,cert.obstruction.voltage_b)
        self.assertTrue(cert.obstruction.validate(LOWER,OBSTRUCTED,1))
        with self.assertRaises(ValueError):
            HigherCouplingSystem(LOWER,1,OBSTRUCTED).generator_lift((0,0,0,0))

    def test_graph_solver_agrees_with_factorization_on_varied_sparse_tables(self):
        samples=(ZERO,ORDER_THREE,ORDER_NINE,OBSTRUCTED,
                 (2,2,2,1,1,1,0,0,0),(0,1,2,0,2,1,1,1,1))
        for lower,gain in ((LOWER,1),(LOWER_GAIN_TWO,2)):
            for upper in samples:
                report=classify_upper(lower,upper,gain)
                obstacle=signed_cycle_obstruction(lower,upper,gain)
                self.assertEqual(obstacle is None,report.order is not None)
                if obstacle is not None:
                    self.assertTrue(obstacle.validate(lower,upper,gain))

    def test_commuting_lift_does_not_imply_order_three(self):
        sys=HigherCouplingSystem(LOWER,1,ORDER_NINE)
        for x in product(range(3),repeat=5):
            third=sys.apply_power(x,3)
            self.assertNotEqual(third,x)
            self.assertEqual(third[:3],x[:3])
            self.assertEqual(third[3],(x[3]+2)%3)

    def test_reversible_generators_and_dimensional_projection_survive_extension(self):
        for q in (ORDER_THREE,ORDER_NINE,OBSTRUCTED):
            sys=HigherCouplingSystem(LOWER,1,q)
            for dimension in range(3,7):
                for state in product(range(3),repeat=dimension):
                    for action in 'AB':
                        after=sys.step(state,action)
                        self.assertEqual(sys.inverse(after,action),state)
                        if dimension>3:
                            self.assertEqual(after[:-1],sys.step(state[:-1],action))

    def test_coherent_lift_projection_for_all_admitted_tables(self):
        for upper in (ORDER_THREE,ORDER_NINE,ZERO):
            sys=HigherCouplingSystem(LOWER,1,upper)
            for dimension in range(4,7):
                for x in product(range(3),repeat=dimension):
                    self.assertEqual(sys.generator_lift(x)[:-1],
                                     sys.generator_lift(x[:-1]))

    def test_order_three_lift_is_exact_specialization_of_previous_potential(self):
        # q1(v,z)=2*z was covered by the previous lower-coupling theorem.
        upper=tuple(2*z%3 for v,z in product(range(3),repeat=2))
        previous=NonconstantCouplingSystem(LOWER,1,2,0)
        current=HigherCouplingSystem(LOWER,1,upper)
        self.assertEqual(current.world(),previous.world())
        self.assertEqual(current.analysis.order,3)
        for x in product(range(3),repeat=5):
            for r in range(3):
                self.assertEqual(current.apply_power(x,r),
                                 previous.correction(x,r))

    def test_arbitrary_row_terms_do_not_change_z_derivative(self):
        for intercepts in product(range(3),repeat=3):
            q=tuple((z+intercepts[v])%3 for v,z in product(range(3),repeat=2))
            analysis=classify_upper(LOWER,q,1)
            self.assertEqual(analysis.order,3)
            self.assertEqual(analysis.three_turn_trace,0)

    def test_transported_mark_and_order_nine_factor_provenance(self):
        sys=HigherCouplingSystem(LOWER,1,ORDER_NINE)
        root=PointedHigherSystem(sys,(0,0,0,0))
        arrow=transport_point(root,1)
        current=arrow
        for n in range(2,10):
            current=current.then(transport_point(current.target,1))
            self.assertEqual(len(current.exponents),n)
            if n==3:
                self.assertEqual(current.target.mark,(0,0,0,2))
            if n==9:
                self.assertEqual(current.target,root)
        self.assertEqual(arrow.inverse().exponents,(8,))
        for x in product(range(3),repeat=4):
            self.assertEqual(arrow.inverse().map_state(arrow.map_state(x)),x)

    def test_three_turn_marked_loop_is_separate_from_nine_turn_loop(self):
        sys=HigherCouplingSystem(LOWER,1,ORDER_THREE)
        root=PointedHigherSystem(sys,(0,0,0,0))
        a=transport_point(root,1)
        b=transport_point(a.target,1)
        c=transport_point(b.target,1)
        self.assertEqual(a.then(b).then(c).target,root)
        self.assertEqual(a.then(b).then(c).exponents,(1,1,1))

    def test_wrong_mark_or_unproved_exponent_cannot_be_promoted(self):
        sys=HigherCouplingSystem(LOWER,1,ORDER_NINE)
        root=PointedHigherSystem(sys,(0,0,0,0))
        with self.assertRaises(ValueError):
            PointedHigherConjugacy(root,root,(1,))
        with self.assertRaises(ValueError):
            PointedHigherConjugacy(root,root,(9,))
        with self.assertRaises(ValueError):
            PointedHigherConjugacy(root,root,())
        one=transport_point(root,1)
        with self.assertRaises(ValueError):
            one.then(one)
        with self.assertRaises(ValueError):
            sys.apply_power((0,0,0,0),9)

    def test_previous_lower_admission_boundary_is_preserved(self):
        bad=(0,)*9
        self.assertIsNone(solve_potential(bad,1))
        with self.assertRaises(ValueError):
            HigherCouplingSystem(bad,1,ORDER_THREE)
        with self.assertRaises(ValueError):
            classify_upper(bad,ORDER_THREE,1)

    def test_strict_finite_field_and_dimension_guards(self):
        with self.assertRaises(ValueError):
            HigherCouplingSystem(LOWER,1,(0,)*8)
        with self.assertRaises(ValueError):
            HigherCouplingSystem(LOWER,True,ORDER_THREE)
        with self.assertRaises(ValueError):
            HigherCouplingSystem(LOWER,1,(0,)*8+(True,))
        with self.assertRaises(ValueError):
            PointedHigherSystem(HigherCouplingSystem(LOWER,1,ORDER_THREE),(0,0,0))
        with self.assertRaises(ValueError):
            HigherCouplingSystem(LOWER,1,ORDER_THREE).generator_lift((0,0))
        with self.assertRaises(ValueError):
            signed_cycle_obstruction(LOWER,ORDER_THREE,0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
