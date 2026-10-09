"""Precise centralizer criterion for a coordinate translation over F3."""
import unittest
from itertools import product

from work.arc_like_maze.translation_centralizer import (
    coordinate_translation, first_obstruction, centralizing_amounts,
    PointedSystem, PointPreservingConjugacy, translate_point, certify_centralizer,
)
from work.arc_like_maze.window_two import WindowProcess

ZERO = (0,) * 9

def table(function):
    return tuple(function(u,v) % 3 for u, v in product(range(3), repeat=2))

def world(q1=ZERO,q2=ZERO,q0=ZERO, q3=ZERO):
    return WindowProcess(1,(q0,q1,q2,q3),(ZERO,))

class CentralizerTests(unittest.TestCase):
    def test_uncoupled_system_has_all_three_centralizing_translations(self):
        w = world()
        self.assertEqual(centralizing_amounts(w),(0,1,2))
        self.assertEqual(certify_centralizer(w).status,"CENTRAL_TRANSLATION")
        self.assertIsNone(first_obstruction(w,1))

    def test_higher_coupling_can_be_nonzero_without_breaking_symmetry(self):
        w = world(table(lambda u,v:u), table(lambda u,v:v),
                  table(lambda u,v:1+u*v),table(lambda u,v:u+2*v))
        self.assertEqual(centralizing_amounts(w),(0,1,2))
        for d in range(3,7):
            for x in product(range(3),repeat=d):
                for r in range(3):
                    for generator in ('A','B'):
                        self.assertEqual(w.step(coordinate_translation(x,r),generator),
                            coordinate_translation(w.step(x,generator),r))

    def test_dependency_on_x2_in_q1_first_breaks_in_dimension_four(self):
        w = world(table(lambda u,v:v))
        for r in (1,2):
            obstruction=first_obstruction(w,r)
            self.assertEqual(obstruction.first_dimension,4)
            self.assertEqual(obstruction.coordinate,3)
            self.assertEqual(obstruction.state,(0,0,0,0))
            self.assertEqual(obstruction.generator,'B')
            self.assertNotEqual(obstruction.generator_after_translation,
                                obstruction.translation_after_generator)
            self.assertEqual(obstruction.generator_after_translation[-1],r)
            self.assertEqual(obstruction.translation_after_generator[-1],0)
        self.assertEqual(centralizing_amounts(w),(0,))

    def test_dependency_on_x2_in_q2_first_breaks_in_dimension_five(self):
        w = world(ZERO,table(lambda u,v:u))
        for r in (1,2):
            obstruction=first_obstruction(w,r)
            self.assertEqual(obstruction.first_dimension,5)
            self.assertEqual(obstruction.coordinate,4)
            self.assertEqual(obstruction.state,(0,0,0,0,0))
            self.assertNotEqual(obstruction.generator_after_translation[-1],
                                obstruction.translation_after_generator[-1])
        self.assertEqual(centralizing_amounts(w),(0,))

    def test_first_obstruction_depth_is_minimal(self):
        for q1,q2,dimension in ((table(lambda u,v:v),ZERO,4),
                                 (ZERO,table(lambda u,v:u),5)):
            w=world(q1,q2)
            for d in range(3,dimension):
                for x in product(range(3),repeat=d):
                    self.assertEqual(w.step(coordinate_translation(x,1),'B'),
                                     coordinate_translation(w.step(x,'B'),1))

    def test_coordinate_translation_is_reversible_of_order_three(self):
        for d in range(3,7):
            for x in product(range(3),repeat=d):
                self.assertEqual(coordinate_translation(coordinate_translation(
                    coordinate_translation(x,1),1),1),x)
                for r in range(3):
                    self.assertEqual(coordinate_translation(
                        coordinate_translation(x,r),(-r)%3),x)
                    if d>3:
                        self.assertEqual(coordinate_translation(x,r)[:-1],
                                         coordinate_translation(x[:-1],r))

    def test_pointed_conjugacy_preserves_mark_and_inverse_factors(self):
        p=PointedSystem(world(),(0,0,0))
        first=translate_point(p,1)
        second=translate_point(first.target,1)
        third=translate_point(second.target,1)
        total=first.then(second).then(third)
        self.assertEqual([first.target.mark,second.target.mark,third.target.mark],
                         [(0,0,1),(0,0,2),(0,0,0)])
        self.assertEqual(total.source,total.target)
        self.assertEqual(total.amounts,(1,1,1))
        self.assertEqual(total.inverse().amounts,(2,2,2))
        for x in product(range(3),repeat=5):
            self.assertEqual(total.map_state(x),x)

    def test_cannot_silently_keep_old_mark_or_use_broken_translation(self):
        w=world()
        p=PointedSystem(w,(0,0,0))
        with self.assertRaises(ValueError):
            PointPreservingConjugacy(p,p,(1,))
        failing=PointedSystem(world(table(lambda u,v:v)),(0,0,0))
        with self.assertRaises(ValueError):
            translate_point(failing,1)
        self.assertEqual(translate_point(failing,0).source,
                         translate_point(failing,0).target)

    def test_unequal_middle_point_blocks_composition(self):
        w=world();a=PointedSystem(w,(0,0,0))
        f=translate_point(a,1)
        bad=translate_point(a,2)
        with self.assertRaises(ValueError):
            f.then(bad)

    def test_table_criterion_agrees_with_exhaustive_state_equations(self):
        rules=(ZERO,table(lambda u,v:u),table(lambda u,v:v),
               table(lambda u,v:u+v),table(lambda u,v:u*v),
               table(lambda u,v:u*u),table(lambda u,v:v*v))
        for q1,q2 in product(rules,repeat=2):
            w=world(q1,q2)
            for r in (1,2):
                symbolic=first_obstruction(w,r)
                for d in (3,4,5):
                    observed=any(w.step(coordinate_translation(s,r),'B') !=
                                 coordinate_translation(w.step(s,'B'),r)
                                 for s in product(range(3),repeat=d))
                    self.assertEqual(observed, bool(symbolic and
                                                 symbolic.first_dimension <= d))

    def test_any_later_coupling_does_not_read_coordinate_two(self):
        w=world(ZERO,ZERO,ZERO,table(lambda u,v:u*v+1))
        self.assertIsNone(first_obstruction(w,1))
        for d in range(3,7):
            for s in product(range(3),repeat=d):
                for a in 'AB':
                    self.assertEqual(w.step(coordinate_translation(s,1),a),
                                     coordinate_translation(w.step(s,a),1))

    def test_triangular_inverses_and_projections_survive_broken_symmetry(self):
        for w in (world(table(lambda u,v:v)), world(ZERO,table(lambda u,v:u))):
            for d in range(3,7):
                for x in product(range(3),repeat=d):
                    for a in 'AB':
                        self.assertEqual(w.inverse(w.step(x,a),a),x)
                        if d>3:
                            self.assertEqual(w.step(x,a)[:-1],w.step(x[:-1],a))

    def test_reject_invalid_marks_and_amounts(self):
        p=PointedSystem(world(),(0,0,0))
        for r in (-1,3,True,1.0):
            with self.assertRaises(ValueError):
                first_obstruction(p.world,r)
            with self.assertRaises(ValueError):
                coordinate_translation((0,0,0),r)
        with self.assertRaises(ValueError):
            coordinate_translation((0,0),1)
        with self.assertRaises(ValueError):
            PointedSystem(p.world,(0,0,True))
        with self.assertRaises(ValueError):
            p.point(2)
        self.assertEqual(p.point(5),(0,0,0,0,0))

if __name__=='__main__':unittest.main(verbosity=2)
