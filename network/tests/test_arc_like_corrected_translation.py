"""Compensated translation symmetries and exact finite-fiber obstructions."""
import unittest
from itertools import product

from work.arc_like_maze.corrected_translation import (
    LinearHigherCoupling, PointedHigherSystem, CorrectedConjugacy,
    corrected_point, obstruction, certify_correction,
)


class CorrectedTranslationTests(unittest.TestCase):
    def test_order_three_repair_for_all_nonzero_drifts_and_couplings(self):
        for drift, c3, c4, gain in product((1, 2), range(3), range(3), (1, 2)):
            system = LinearHigherCoupling(drift, c3, c4, gain)
            self.assertEqual(certify_correction(system).status,
                             'CORRECTED_CENTRALIZER_ACTION')
            for state in product(range(3), repeat=5):
                self.assertEqual(system.correction(system.correction(
                    system.correction(state,1),1),1),state)

    def test_nonzero_higher_coupling_is_not_in_itself_an_obstruction(self):
        for sys in (LinearHigherCoupling(1,1,0),LinearHigherCoupling(1,0,1),
                    LinearHigherCoupling(2,2,1)):
            self.assertTrue(sys.repairable)
            self.assertIsNone(obstruction(sys))
            self.assertNotEqual(sys.correction((0,0,1,0,0),1),
                                (0,0,2,0,0))

    def test_uncorrected_translation_fails_when_higher_rule_reads_x2(self):
        from work.arc_like_maze.translation_centralizer import first_obstruction
        for c3,c4,first in ((1,0,4),(0,1,5),(1,1,4)):
            sys = LinearHigherCoupling(1,c3,c4)
            self.assertEqual(first_obstruction(sys.world(),1).first_dimension,first)
            for d in range(first,7):
                at_least_one = False
                for state in product(range(3), repeat=d):
                    unc = list(state); unc[2] = (unc[2]+1)%3
                    lhs=sys.step(tuple(unc),'B')
                    rhs=list(sys.step(state,'B'));rhs[2]=(rhs[2]+1)%3
                    if lhs!=tuple(rhs):at_least_one=True;break
                self.assertTrue(at_least_one)

    def test_corrected_lift_commutes_even_when_uncorrected_does_not(self):
        for drift,c3,c4,gain in product((1,2),(0,1,2),(0,1,2),(1,2)):
            sys=LinearHigherCoupling(drift,c3,c4,gain)
            for dimension in (3,4,5,6):
                for state in product(range(3),repeat=dimension):
                    for r in (0,1,2):
                        for generator in 'AB':
                            self.assertEqual(sys.step(sys.correction(state,r),generator),
                                sys.correction(sys.step(state,generator),r))

    def test_first_obstruction_on_fixed_fiber_is_dimension_four(self):
        sys=LinearHigherCoupling(0,1,0)
        witness=obstruction(sys)
        self.assertEqual(witness.dimension,4)
        self.assertEqual((witness.source_prefix,witness.target_prefix),
                         ((2,0,0),(2,0,1)))
        self.assertEqual((witness.source_B_fixed,witness.translated_B_fixed),(3,0))
        self.assertEqual(certify_correction(sys).centralizing_amounts,(0,))
        with self.assertRaises(ValueError):sys.correction((0,0,0,0),1)

    def test_first_obstruction_on_fixed_fiber_is_dimension_five(self):
        sys=LinearHigherCoupling(0,0,2)
        witness=obstruction(sys)
        self.assertEqual(witness.dimension,5)
        self.assertEqual((witness.source_B_fixed,witness.translated_B_fixed),(9,0))
        self.assertEqual(certify_correction(sys).first_obstruction_dimension,5)
        for state in product(range(3),repeat=4):
            t=list(state);t[2]=(t[2]+1)%3
            moved=sys.step(state,'B'); moved=list(moved);moved[2]=(moved[2]+1)%3
            self.assertEqual(sys.step(tuple(t),'B'),tuple(moved))

    def test_zero_drift_with_zero_higher_coupling_still_centralizes(self):
        sys=LinearHigherCoupling(0,0,0,2)
        self.assertEqual(certify_correction(sys).centralizing_amounts,(0,1,2))
        self.assertEqual(sys.correction((0,0,2,1,0),1),(0,0,0,1,0))

    def test_repair_point_requires_five_coordinate_mark(self):
        sys=LinearHigherCoupling(1,1,2)
        p=PointedHigherSystem(sys,(0,0,0,0,0))
        f=corrected_point(p,1)
        g=corrected_point(f.target,1)
        h=corrected_point(g.target,1)
        self.assertEqual((f.target.mark,g.target.mark,h.target.mark),
                         ((0,0,1,0,0),(0,0,2,1,2),(0,0,0,0,0)))
        self.assertEqual(h.target,p)
        self.assertEqual(f.then(g).then(h).factors,(1,1,1))
        self.assertEqual(f.then(g).then(h).source,
                         f.then(g).then(h).target)

    def test_exact_inverse_and_composition_preserve_factor_provenance(self):
        sys=LinearHigherCoupling(2,2,1)
        p=PointedHigherSystem(sys,(1,2,0,1,2))
        f=corrected_point(p,1)
        g=corrected_point(f.target,2)
        composed=f.then(g)
        self.assertEqual(composed.source,composed.target)
        self.assertEqual(composed.factors,(1,2))
        self.assertEqual(composed.inverse().factors,(1,2))
        for state in product(range(3),repeat=6):
            self.assertEqual(composed.map_state(state),state)
            self.assertEqual(f.inverse().map_state(f.map_state(state)),state)

    def test_all_actions_have_triangular_inverses_and_commuting_projections(self):
        for drift,c3,c4 in product(range(3),repeat=3):
            sys=LinearHigherCoupling(drift,c3,c4)
            for d in range(3,7):
                for x in product(range(3),repeat=d):
                    for a in 'AB':
                        self.assertEqual(sys.inverse(sys.step(x,a),a),x)
                        if d>3:
                            self.assertEqual(sys.step(x,a)[:-1],sys.step(x[:-1],a))

    def test_presentation_is_existing_two_predecessor_engine_not_a_new_action(self):
        for drift,c3,c4 in product(range(3),repeat=3):
            sys=LinearHigherCoupling(drift,c3,c4)
            world=sys.world()
            self.assertEqual(world.rule(0),(drift,)*9)
            for u,v in product(range(3),repeat=2):
                self.assertEqual(world.rule(1)[3*u+v],c3*v%3)
                self.assertEqual(world.rule(2)[3*u+v],c4*u%3)
            self.assertEqual(world.rule(10),(0,)*9)

    def test_fiber_obstruction_is_not_claimed_to_rule_out_all_conjugacies(self):
        for sys in (LinearHigherCoupling(0,1,0),LinearHigherCoupling(0,0,1)):
            self.assertFalse(sys.repairable)
            self.assertIn(sys.first_obstruction_dimension,(4,5))
            with self.assertRaises(ValueError):
                corrected_point(PointedHigherSystem(sys,(0,0,0,0,0)),1)
            # Identity is always admissible even in an obstructed system.
            f=corrected_point(PointedHigherSystem(sys,(0,0,0,0,0)),0)
            self.assertEqual(f.source,f.target)

    def test_invalid_coefficients_marks_and_middle_systems_are_rejected(self):
        for bad in (True,-1,3,1.0):
            with self.assertRaises(ValueError):LinearHigherCoupling(bad,0,0)
        sys=LinearHigherCoupling(1,1,1)
        for mark in ((0,0,0),(0,0,0,0,3),(0,0,0,0,False)):
            with self.assertRaises(ValueError):PointedHigherSystem(sys,mark)
        point=PointedHigherSystem(sys,(0,0,0,0,0))
        with self.assertRaises(ValueError):point.point(4)
        with self.assertRaises(ValueError):sys.correction((0,0),1)
        with self.assertRaises(ValueError):sys.correction((0,0,0),3)
        f=corrected_point(point,1)
        with self.assertRaises(ValueError):f.then(corrected_point(point,1))
        with self.assertRaises(ValueError):CorrectedConjugacy(point,point,(1,))

if __name__=='__main__':unittest.main(verbosity=2)
