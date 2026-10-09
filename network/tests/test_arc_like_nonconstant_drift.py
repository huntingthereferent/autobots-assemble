"""Cohomological equation for pointed finite-field transformation systems."""
import unittest
from itertools import product

from work.arc_like_maze.nonconstant_drift import (
    Potential, NonconstantCouplingSystem, DistinguishedSystem,
    PointedConjugacy, solve_potential, graph_obstruction,
    certify_cohomology, translated_point,
)
from work.arc_like_maze.corrected_translation import LinearHigherCoupling

GOOD = (0, 1, 2, 0, 2, 1, 1, 1, 1)
ZERO = (0,) * 9


def admitted_tables(gain):
    for drift in (1, 2):
        for first, second in product(range(3), repeat=2):
            row0=(first, second, (-first-second)%3)
            row1=tuple((2*drift-row0[(v-gain)%3])%3 for v in range(3))
            yield row0 + row1 + (drift,)*3


class NonconstantDriftTests(unittest.TestCase):
    def test_exactly_eighteen_tables_per_gain(self):
        for gain in (1, 2):
            admitted = set(admitted_tables(gain))
            self.assertEqual(len(admitted), 18)
            for q in admitted:
                self.assertIsNotNone(solve_potential(q, gain))
            self.assertEqual(sum(solve_potential(q,gain) is not None
                                 for q in product(range(3), repeat=9)), 18)

    def test_nonconstant_representative_has_literal_normalized_potential(self):
        p=solve_potential(GOOD,1)
        self.assertEqual((p.drift,p.alpha),(1,(0,1,1)))
        self.assertEqual(p.value(0,0),0)
        self.assertEqual(p.value(1,0),1)
        self.assertEqual(p.value(2,1),2)
        self.assertIsNone(graph_obstruction(GOOD,1))
        self.assertEqual(certify_cohomology(
            NonconstantCouplingSystem(GOOD,1,1,2)).status,
            'EXPLICIT_COHOMOLOGICAL_LIFT')

    def test_entire_lower_state_cocycle_holds_at_all_27_edges(self):
        for gain in (1,2):
            for rule in admitted_tables(gain):
                p=solve_potential(rule,gain)
                for u,v,z in product(range(3), repeat=3):
                    vn=(v+gain*(u+1))%3
                    zn=(z+rule[3*u+v])%3
                    self.assertEqual((p.value(vn,zn)-p.value(v,z))%3,1)

    def test_corrected_action_commutes_for_nonconstant_coupling_at_all_depths(self):
        for gain in (1,2):
            for rule in (GOOD, tuple(u for u in range(3) for _ in range(3)),
                         (1,)*9):
                # GOOD and q0=u are admitted only for gain 1; otherwise
                # use the algebraically constructed nearby admitted example.
                if solve_potential(rule,gain) is None:
                    rule=next(q for q in admitted_tables(gain) if len(set(q))>1)
                for b,c in ((1,0),(0,2),(1,2)):
                    system=NonconstantCouplingSystem(rule,gain,b,c)
                    self.assertTrue(system.admits_translation)
                    for dimension in range(3,7):
                        for state in product(range(3),repeat=dimension):
                            for r in range(3):
                                for generator in 'AB':
                                    self.assertEqual(
                                        system.correction(system.step(state,generator),r),
                                        system.step(system.correction(state,r),generator))

    def test_corrected_symmetries_form_order_three_group(self):
        for gain in (1,2):
            for q in admitted_tables(gain):
                system=NonconstantCouplingSystem(q,gain,1,2)
                for x in product(range(3),repeat=5):
                    self.assertEqual(
                        system.correction(system.correction(
                            system.correction(x,1),1),1),x)
                    for r in range(3):
                        self.assertEqual(system.correction(
                            system.correction(x,r),(-r)%3),x)

    def test_nonzero_cocycle_correction_is_not_forced_to_be_constant(self):
        sys=NonconstantCouplingSystem(GOOD,1,1,2)
        first=sys.correction((0,0,0,0,0),1)
        second=sys.correction((0,1,0,0,0),1)
        self.assertEqual(first,(0,0,1,0,0))
        self.assertEqual(second,(0,1,1,1,2))
        self.assertNotEqual(first[3:],second[3:])

    def test_constant_drift_is_special_case_of_previous_construction(self):
        for a,b,c,gain in product((1,2),range(3),range(3),(1,2)):
            new=NonconstantCouplingSystem((a,)*9,gain,b,c)
            old=LinearHigherCoupling(a,b,c,gain)
            self.assertEqual(new.world(),old.world())
            p=solve_potential(new.q0,gain)
            self.assertEqual(p.alpha,(0,0,0))
            for x in product(range(3),repeat=5):
                for r in range(3):
                    self.assertEqual(new.correction(x,r),old.correction(x,r))

    def test_zero_higher_coupling_permits_every_nonconstant_lower_rule(self):
        for q in (ZERO,(1,0,0,0,2,0,2,0,2),GOOD):
            for gain in (1,2):
                sys=NonconstantCouplingSystem(q,gain,0,0)
                self.assertEqual(certify_cohomology(sys).status,
                                 'PURE_TRANSLATION_SYMMETRY')
                for state in product(range(3),repeat=5):
                    for r in range(3):
                        self.assertEqual(sys.correction(state,r)[2],
                                         (state[2]+r)%3)
                        self.assertEqual(sys.correction(sys.step(state,'B'),r),
                                         sys.step(sys.correction(state,r),'B'))

    def test_zero_row_two_has_explicit_nonzero_cycle_voltage(self):
        sys=NonconstantCouplingSystem(ZERO,1,1,0)
        cert=certify_cohomology(sys)
        self.assertEqual(cert.status,'NONZERO_VOLTAGE_CYCLE')
        self.assertTrue(cert.obstruction.validate(ZERO,1))
        self.assertNotEqual(cert.obstruction.first_voltage,
                            cert.obstruction.second_voltage)
        self.assertFalse(sys.admits_translation)
        with self.assertRaises(ValueError):
            sys.correction((0,0,0,0),1)

    def test_nonconstant_row_two_has_signed_cycle_obstruction(self):
        q=(0,1,2,0,2,1,1,2,1)
        for g in (1,2):
            witness=graph_obstruction(q,g)
            self.assertIsNotNone(witness)
            self.assertTrue(witness.validate(q,g))
            self.assertIsNone(solve_potential(q,g))

    def test_row_sum_obstruction_and_opposite_step_obstruction(self):
        nonzero_sum=(1,0,0,0,0,0,1,1,1)
        incompatible=(0,1,2,0,0,0,1,1,1)
        for q in (nonzero_sum,incompatible):
            self.assertIsNone(solve_potential(q,1))
            witness=graph_obstruction(q,1)
            self.assertIsNotNone(witness)
            self.assertTrue(witness.validate(q,1))

    def test_independent_voltage_graph_agrees_with_algebra_for_sparse_samples(self):
        rules=(ZERO,GOOD,
            (0,0,0,1,1,1,2,2,2),
            (1,)*9,
            (0,1,2,0,0,0,1,1,1),
            (0,1,2,0,2,1,1,1,1))
        for gain,q in product((1,2),rules):
            self.assertEqual(solve_potential(q,gain) is None,
                             graph_obstruction(q,gain) is not None)

    def test_pointed_conjugacy_explicit_mark_and_factor_provenance(self):
        sys=NonconstantCouplingSystem(GOOD,1,1,2)
        root=DistinguishedSystem(sys,(0,0,0,0,0))
        f=translated_point(root,1)
        g=translated_point(f.target,1)
        h=translated_point(g.target,1)
        self.assertEqual(f.target.mark,(0,0,1,0,0))
        self.assertEqual(g.target.mark,(0,0,2,1,2))
        self.assertEqual(h.target,root)
        self.assertEqual(f.then(g).then(h).factors,(1,1,1))
        self.assertEqual(f.inverse().factors,(2,))
        self.assertEqual(f.then(g).then(h).source,root)
        self.assertEqual(f.then(g).then(h).target,root)

    def test_inverse_projections_and_states_stay_coherent(self):
        for q in (GOOD,ZERO,(2,)*9):
            sys=NonconstantCouplingSystem(q,1,1,2)
            for depth in range(3,7):
                for state in product(range(3),repeat=depth):
                    for action in 'AB':
                        moved=sys.step(state,action)
                        self.assertEqual(sys.inverse(moved,action),state)
                        if depth>3:
                            self.assertEqual(moved[:-1],sys.step(state[:-1],action))
                    if sys.admits_translation and depth>3:
                        self.assertEqual(sys.correction(state,1)[:-1],
                            sys.correction(state[:-1],1))

    def test_reject_broken_pointed_promotions_and_mismatched_systems(self):
        sys=NonconstantCouplingSystem(ZERO,1,1,0)
        root=DistinguishedSystem(sys,(0,0,0,0,0))
        with self.assertRaises(ValueError):
            translated_point(root,1)
        with self.assertRaises(ValueError):
            PointedConjugacy(root,root,(1,))
        with self.assertRaises(ValueError):
            PointedConjugacy(root,root,())
        good=NonconstantCouplingSystem(GOOD,1,1,2)
        p=DistinguishedSystem(good,(0,0,0,0,0))
        f=translated_point(p,1)
        with self.assertRaises(ValueError):
            f.then(f)
        with self.assertRaises(ValueError):
            PointedConjugacy(p,p,(1,))
        with self.assertRaises(ValueError):
            PointedConjugacy(p,root,(0,))

    def test_strict_input_boundaries(self):
        with self.assertRaises(ValueError):
            NonconstantCouplingSystem((0,)*8,1,1,1)
        with self.assertRaises(ValueError):
            NonconstantCouplingSystem((0,)*9,0,1,1)
        with self.assertRaises(ValueError):
            NonconstantCouplingSystem((0,)*9,1,True,0)
        with self.assertRaises(ValueError):
            solve_potential((0,)*9,True)
        with self.assertRaises(ValueError):
            graph_obstruction((0,)*8,1)
        with self.assertRaises(ValueError):
            DistinguishedSystem(NonconstantCouplingSystem(GOOD,1,1,2),(0,0,0))
        with self.assertRaises(ValueError):
            NonconstantCouplingSystem(GOOD,1,1,2).correction((0,0),1)
        with self.assertRaises(ValueError):
            NonconstantCouplingSystem(GOOD,1,1,2).correction((0,0,0),3)


if __name__=="__main__":
    unittest.main(verbosity=2)
