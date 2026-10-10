import unittest
from itertools import product
from engine_two_trace_boundary_probe import (
    STATES,Q_LEFT,Q_RIGHT,step,symmetry,power,counts,investigate,
)
B=lambda s,Q:step(s,'B',Q)

class TraceBoundaryTests(unittest.TestCase):
    def test_all_states_exhausted(self):
        self.assertEqual(len(STATES),243)
        self.assertEqual(len(set(STATES)),243)
    def test_native_B_fixed_word_counts(self):
        self.assertEqual(counts(Q_LEFT),{'B^1':0,'B^3':243,'B^9':243})
        self.assertEqual(counts(Q_RIGHT),{'B^1':0,'B^3':0,'B^9':243})
    def test_three_turn_shift_is_exact(self):
        for s in STATES:
            self.assertEqual(power(s,B,Q_LEFT,3),s)
            self.assertEqual(power(s,B,Q_RIGHT,3),s[:3]+((s[3]+1)%3,)+s[4:])
    def test_commuting_symmetry_both_generators(self):
        for Q in (Q_LEFT,Q_RIGHT):
            for s in STATES:
                for action in 'AB':
                    self.assertEqual(symmetry(step(s,action,Q),Q),
                                     step(symmetry(s,Q),action,Q))
    def test_cyclic_order(self):
        for s in STATES:
            self.assertEqual(power(s,symmetry,Q_LEFT,3),s)
            self.assertNotEqual(power(s,symmetry,Q_RIGHT,3),s)
            self.assertEqual(power(s,symmetry,Q_RIGHT,9),s)
    def test_no_spurious_equivalence_conclusion(self):
        info=investigate()
        self.assertEqual(info['status'],'WITNESSED_BOUNDARY')
        self.assertEqual(info['root_word_witness']['after_image'],(0,0,0,1,0))

if __name__=='__main__':unittest.main()