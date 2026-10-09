"""Exhaustive origin-rooted coupled-world relation tests."""
import unittest
from itertools import product

from work.arc_like_maze.alignment import discover_alignment, equivalent_classes
from work.arc_like_maze.coupling_family import (CoupledWorld, all_couplings, scale_world,
    scaling_witness, certify_coupling_family, rotate_within_class, certify_rotation)

class TestCouplingFamily(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = certify_coupling_family(depth=4)
        cls.groups = equivalent_classes(all_couplings(4))

    def test_exact_81_worlds_21_rooted_classes(self):
        self.assertEqual((self.certificate.status, self.certificate.worlds,
            self.certificate.rooted_classes), ("CLOSED_ROOTED_CLASSES_IN_DECLARED_FAMILY",81,21))
        self.assertEqual(self.certificate.class_sizes,(2,)*4+(4,)*16+(9,))

    def test_invariants_at_fourth_coordinate(self):
        phi=(0,1,2)
        def fixed(h):
            w=CoupledWorld(4,phi,h)
            return sum(w.step(s,'B')==s for s in product(range(3),repeat=4))
        self.assertEqual(fixed((0,1,2)),3)
        self.assertEqual(fixed((0,0,2)),6)
        self.assertEqual(fixed((0,0,0)),9)

    def test_nonzero_class_pairs_have_full_depth_scaling_alignment(self):
        for group in self.groups:
            if group[0].phi==(0,0,0):continue
            for source in group:
                for target in group:
                    s,t=scaling_witness(source,target)
                    for depth in range(4,7):
                        a=CoupledWorld(depth,source.phi,source.h)
                        b=CoupledWorld(depth,target.phi,target.h)
                        for state in product(range(3),repeat=depth):
                            mapped=scale_world(state,s,t)
                            for action in 'AB':
                                self.assertEqual(scale_world(a.step(state,action),s,t),
                                                 b.step(mapped,action))

    def test_phi_zero_same_rooted_orbit_but_not_all_full_space_equivalent(self):
        a=CoupledWorld(4,(0,0,0),(0,0,0))
        b=CoupledWorld(4,(0,0,0),(0,0,1))
        self.assertTrue(discover_alignment(a,b).aligned)
        self.assertIsNone(scaling_witness(a,b))
        full_a=sum(a.step(s,'B')==s for s in product(range(3),repeat=4))
        full_b=sum(b.step(s,'B')==s for s in product(range(3),repeat=4))
        self.assertNotEqual(full_a,full_b)
        self.assertGreater(self.certificate.scoped_orbit_only_pairs,0)

    def test_projection_and_reversibility(self):
        for world in all_couplings(5):
            low=CoupledWorld(4,world.phi,world.h)
            for state in product(range(3),repeat=5):
                for action in 'AB':
                    self.assertEqual(world.step(state,action)[:4],low.step(state[:4],action))
                    self.assertEqual(world.inverse(world.step(state,action),action),state)

    def test_all_pairwise_classification_at_depth_four(self):
        # Every cross-class pair must fail, not merely have different fixed-point totals.
        for i,group in enumerate(self.groups):
            for later in self.groups[i+1:]:
                r=discover_alignment(group[0],later[0])
                self.assertEqual(r.status,'OPEN')
                self.assertIsNotNone(r.conflicting_words)

    def test_new_break_first_visible_at_depth_four(self):
        phi=(0,1,2)
        a=CoupledWorld(3,phi,(0,1,2));b=CoupledWorld(3,phi,(0,0,2))
        self.assertTrue(discover_alignment(a,b).aligned)
        a=CoupledWorld(4,phi,(0,1,2));b=CoupledWorld(4,phi,(0,0,2))
        self.assertEqual(discover_alignment(a,b).status,'OPEN')

    def test_explicit_relation_preserving_rotation_has_order_36(self):
        result=certify_rotation()
        self.assertEqual(result.status,"CLOSED_ROOTED_CONSTRUCTION_PERMUTATION")
        self.assertEqual((result.worlds,result.classes,result.global_order),(81,21,36))
        self.assertTrue(result.moved_every_world)
        rotated=rotate_within_class()
        self.assertEqual(len(set(rotated.values())),81)
        # The constructors are chosen on the quotient; they are not uniquely
        # demanded by the A/B equations or certified as full-space conjugacies.
        for world in rotated:
            self.assertTrue(discover_alignment(world,rotated[world]).aligned)

    def test_invalid_outside_contract(self):
        with self.assertRaises(ValueError):CoupledWorld(4,(0,1,2),(1,0,1))
        with self.assertRaises(ValueError):CoupledWorld(4,(0,1,2),(0,1,2)).step((1,2),'A')
        with self.assertRaises(ValueError):scale_world((0,1,2,0),0,1)
        self.assertEqual(certify_coupling_family(depth=3).status,'UNKNOWN')

if __name__=='__main__':unittest.main(verbosity=2)
