"""Exact order-nine fifth-coordinate lifts as the fourth-coordinate law varies."""
import unittest
from itertools import product

from work.arc_like_maze.variable_fourth_lift import (
    FourthCoordinateParameters, VariableFourthSystem, DistinguishedSystem,
    PointedConjugacy, classify, linear_certificate, solve_voltage,
    transport_point, certify_order_nine_family,
)
from work.arc_like_maze.fifth_coordinate_lift import FifthCoordinateSystem

F3=(0,1,2)
Q=(0,0,1)
Q_SQUARE=(0,1,1)
P5=(0,0,0)
P6=(0,1,1)
P7=(0,0,1)
ZERO=(0,)*9


def param(rank,gain=1):
    return FourthCoordinateParameters(
        gain,Q,{5:P5,6:P6,7:P7}[rank])


class VariableFourthTests(unittest.TestCase):
    def test_complete_rank_and_order_certificate_for_all_324_configurations(self):
        c=certify_order_nine_family()
        self.assertEqual(c.status,
                         "EXACT_VARIABLE_FOURTH_ORDER_NINE_CLASSIFICATION")
        self.assertEqual(c.fourth_coordinate_configurations,324)
        self.assertEqual(c.rank_histogram,((5,60),(6,48),(7,216)))
        self.assertEqual(c.admitted_fifth_combinations,8100)
        self.assertEqual(c.verified_basis_vectors,816)
        self.assertEqual(c.nontrivial_fourth_dependence_at_rank7,0)
        self.assertEqual(c.order27_counterexamples,0)

    def test_each_rank_is_realized_by_one_nonconstant_fourth_rule(self):
        for gain in (1,2):
            for rank in (5,6,7):
                p=param(rank,gain)
                actual,connected,basis=linear_certificate(p)
                self.assertEqual((actual,connected,len(basis)),
                                 (rank,1,9-rank))
                self.assertEqual(sum(p.primitive)%3,1)

    def test_exact_nullspace_span_admits_all_fifth_couplings(self):
        for gain,rank in product((1,2),(5,6,7)):
            p=param(rank,gain)
            _,_,basis=linear_certificate(p)
            seen=set()
            for coefficients in product(F3,repeat=len(basis)):
                fifth=tuple(sum(a*b[i] for a,b in zip(coefficients,basis))%3
                            for i in range(9))
                seen.add(fifth)
                result=classify(p,fifth)
                self.assertEqual(result.status,"ORDER_NINE_POINTED_CENTRALIZER")
                self.assertEqual(result.order,9)
            self.assertEqual(len(seen),3**(9-rank))

    def test_rank_seven_forbids_any_genuine_fourth_coordinate_dependence(self):
        for gain in (1,2):
            p=param(7,gain)
            _,_,basis=linear_certificate(p)
            for vec in basis:
                self.assertTrue(all(vec[3*z+y]==vec[3*z]
                                    for z,y in product(F3,repeat=2)))
            fifth=tuple(y for z,y in product(F3,repeat=2))
            result=classify(p,fifth)
            self.assertEqual(result.status,"SIGNED_CYCLE_OBSTRUCTION")
            self.assertTrue(result.obstruction.validate(p,fifth))

    def test_rank_five_and_six_admit_genuine_fourth_dependence(self):
        for gain in (1,2):
            for rank in (5,6):
                p=param(rank,gain)
                _,_,basis=linear_certificate(p)
                candidate=next(v for v in basis
                               if any(v[3*z+y]!=v[3*z]
                                      for z,y in product(F3,repeat=2)))
                self.assertEqual(classify(p,candidate).order,9)

    def test_explicit_signed_cycle_replays_a_rejected_table(self):
        for gain,rank in product((1,2),(5,6,7)):
            p=param(rank,gain)
            fifth=tuple((z*y)%3 for z,y in product(F3,repeat=2))
            result=classify(p,fifth)
            if result.order is None:
                self.assertIsNotNone(result.obstruction)
                self.assertNotEqual(result.obstruction.first_voltage,
                                    result.obstruction.second_voltage)
                self.assertTrue(result.obstruction.validate(p,fifth))
                with self.assertRaises(ValueError):
                    VariableFourthSystem(p,fifth).centralizer((0,0,0,0,0))

    def test_previously_fixed_quadratic_rule_embeds_semantically(self):
        fifth=tuple((z+y*y)%3 for z,y in product(F3,repeat=2))
        for gain in (1,2):
            p=FourthCoordinateParameters(gain,Q_SQUARE,(0,0,0))
            new=VariableFourthSystem(p,fifth)
            old=FifthCoordinateSystem(gain,fifth)
            self.assertEqual(p.fourth_rule,old.world().rule(1))
            for depth in (3,4,5,6):
                for state in product(F3,repeat=depth):
                    for letter in "AB":
                        self.assertEqual(new.step(state,letter),
                                         old.step(state,letter))
                    self.assertEqual(new.centralizer(state),
                                     old.generator_lift(state))

    def test_commutation_and_group_order_for_rank_five_six_seven_examples(self):
        for gain,rank in product((1,2),(5,6,7)):
            p=param(rank,gain)
            _,_,basis=linear_certificate(p)
            q2=basis[-1]
            sys=VariableFourthSystem(p,q2)
            for depth in range(3,7):
                for state in product(F3,repeat=depth):
                    moved=sys.centralizer(state)
                    for generator in "AB":
                        self.assertEqual(
                            sys.centralizer(sys.step(state,generator)),
                            sys.step(moved,generator))
                    self.assertEqual(
                        sys.centralizer(sys.power(state,8)),state)
                    if depth>=4:
                        third=sys.power(state,3)
                        self.assertEqual(third[:3],state[:3])
                        self.assertNotEqual(third[3],state[3])

    def test_all_depths_keep_exact_triangular_inverse_and_projection(self):
        for rank in (5,6,7):
            p=param(rank)
            sys=VariableFourthSystem(p,ZERO)
            for depth in range(3,7):
                for state in product(F3,repeat=depth):
                    for generator in "AB":
                        after=sys.step(state,generator)
                        self.assertEqual(sys.inverse(after,generator),state)
                        if depth>3:
                            self.assertEqual(sys.step(state[:-1],generator),
                                             after[:-1])
                    if depth>3:
                        self.assertEqual(sys.centralizer(state)[:-1],
                                         sys.centralizer(state[:-1]))

    def test_explicit_pointed_order_nine_cycle_and_factor_conservation(self):
        p=param(6)
        _,_,basis=linear_certificate(p)
        sys=VariableFourthSystem(p,basis[-1])
        root=DistinguishedSystem(sys,(0,0,0,0,0))
        arrow=None
        current=root
        marks=set()
        for count in range(9):
            marks.add(current.mark)
            step=transport_point(current)
            arrow=step if arrow is None else arrow.then(step)
            current=step.target
        self.assertEqual(current,root)
        self.assertEqual(len(marks),9)
        self.assertEqual(arrow.exponents,(1,)*9)
        self.assertEqual(arrow.inverse().exponents,(8,)*9)
        for state in product(F3,repeat=5):
            self.assertEqual(arrow.map_state(state),state)

    def test_root_mismatch_and_noncomposable_points_are_rejected(self):
        sys=VariableFourthSystem(param(7),ZERO)
        point=DistinguishedSystem(sys,(0,0,0,0,0))
        moved=transport_point(point)
        with self.assertRaises(ValueError):
            PointedConjugacy(point,point,(1,))
        with self.assertRaises(ValueError):
            PointedConjugacy(point,point,(9,))
        with self.assertRaises(ValueError):
            moved.then(moved)
        with self.assertRaises(ValueError):
            transport_point(point,9)

    def test_order_three_base_is_explicitly_outside_current_scope(self):
        for g in (1,2):
            with self.assertRaises(ValueError):
                FourthCoordinateParameters(g,(0,1,2),(0,0,0))
            with self.assertRaises(ValueError):
                FourthCoordinateParameters(g,(0,0,0),(0,0,0))

    def test_strict_parameter_and_coupling_validations(self):
        for gain in (True,0,3):
            with self.assertRaises(ValueError):
                FourthCoordinateParameters(gain,Q,P5)
        for q in ((0,0),(0,0,1),(0,0,True)):
            with self.assertRaises(ValueError):
                FourthCoordinateParameters(1,q,P5)
        with self.assertRaises(ValueError):
            FourthCoordinateParameters(1,Q,(1,0,0))
        with self.assertRaises(ValueError):
            classify(param(5),(0,)*8)
        with self.assertRaises(ValueError):
            VariableFourthSystem(param(5),ZERO).centralizer((0,0))
        with self.assertRaises(ValueError):
            DistinguishedSystem(VariableFourthSystem(param(5),ZERO),
                                (0,0,0,0))


if __name__=="__main__":
    unittest.main(verbosity=2)
