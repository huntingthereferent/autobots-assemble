import unittest
from itertools import product
from collections import Counter
from engine_two_native_continuation import (
    F3, FIBER,FULL,CARRY_2,CARRY_3,ZERO,WORLD_9,WORLD_27,
    WORLD_27_SCALED,WindowLaw,cycles,continue_native,build_b_conjugacy,record_experiment
)

class ContinuationResearchTests(unittest.TestCase):
    def test_both_worlds_are_actual_invertible_A_B_laws(self):
        for w in (WORLD_9,WORLD_27,WORLD_27_SCALED):
            for s in FULL:
                for a in 'AB':
                    self.assertEqual(w.inverse(w.step(s,a),a),s)
                    self.assertEqual(w.step(w.inverse(s,a),a),s)

    def test_fiber_is_b_invariant_but_not_a_invariant(self):
        for w in (WORLD_9,WORLD_27):
            self.assertTrue(all(w.step(s,'B') in FIBER for s in FIBER))
            self.assertFalse(any(w.step(s,'A') in FIBER for s in FIBER))

    def test_same_observation_up_to_eight_does_not_prove_equivalence(self):
        r=continue_native(WORLD_9,WORLD_27,8)
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        self.assertEqual(len(r.observations),8)
        self.assertTrue(all(o.left_fixed==o.right_fixed==0 for o in r.observations))
        self.assertEqual([o.n for o in r.observations],list(range(1,9)))

    def test_ninth_power_is_first_distinction(self):
        r=continue_native(WORLD_9,WORLD_27,9)
        self.assertEqual(r.status,'DISTINGUISHED_B_ACTIONS')
        self.assertEqual((r.observations[-1].left_fixed,r.observations[-1].right_fixed),(81,0))
        self.assertEqual(r.observations[-1].left_origin,(0,0,0,0,0))
        self.assertEqual(r.observations[-1].right_origin,(0,0,0,1,0))
        self.assertEqual(len(r.observations),9)

    def test_cycle_inventory_is_independent_of_iteration_reader(self):
        self.assertEqual(Counter(map(len,cycles(WORLD_9))),Counter({9:9}))
        self.assertEqual(Counter(map(len,cycles(WORLD_27))),Counter({27:3}))
        self.assertEqual(len(set(FIBER)),81)

    def test_earned_B_only_positive_control_has_explicit_intertwiner(self):
        r=continue_native(WORLD_27,WORLD_27_SCALED,27)
        self.assertEqual(r.status,'B_ONLY_CONJUGACY_WITNESSED')
        h=build_b_conjugacy(WORLD_27,WORLD_27_SCALED)
        self.assertEqual(len(h),81)
        self.assertEqual(len(set(h.values())),81)
        for x in FIBER:
            self.assertEqual(h[WORLD_27.step(x,'B')],WORLD_27_SCALED.step(h[x],'B'))

    def test_no_premature_positive_stop_even_for_conjugate_B_actions(self):
        r=continue_native(WORLD_27,WORLD_27_SCALED,26)
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        self.assertEqual(len(r.observations),26)

    def test_full_state_first_distinction_is_three_not_nine(self):
        a=[sum(WORLD_9.power(s,n)==s for s in FULL) for n in range(1,10)]
        b=[sum(WORLD_27.power(s,n)==s for s in FULL) for n in range(1,10)]
        self.assertEqual(next(i for i,(x,y) in enumerate(zip(a,b),1) if x!=y),3)
        self.assertEqual((a[2],b[2]),(81,54))

    def test_identical_worlds_get_positive_identity_witness(self):
        r=continue_native(WORLD_9,WORLD_9,9)
        self.assertEqual(r.status,'B_ONLY_CONJUGACY_WITNESSED')
        self.assertEqual(len(r.observations),9)

    def test_incomplete_carrier_is_rejected_if_not_b_invariant(self):
        with self.assertRaises(ValueError):
            continue_native(WORLD_9,WORLD_27,9,carrier=FIBER[:5])

    def test_source_and_earlier_witnesses_survive(self):
        r=continue_native(WORLD_9,WORLD_27,9)
        self.assertEqual(r.observations[0].left_fixed_states,())
        self.assertEqual(r.observations[8].left_fixed_states,tuple(FIBER))
        self.assertEqual(r.observations[8].right_fixed_states,())
        self.assertEqual(r.compact()['source']['q0'],tuple(CARRY_2))
        self.assertEqual(r.compact()['target']['q1'],tuple(CARRY_3))

    def test_input_validation(self):
        with self.assertRaises(ValueError):continue_native(WORLD_9,WORLD_27,0)
        with self.assertRaises(ValueError):WindowLaw((0,)*8,ZERO,'bad')
        with self.assertRaises(ValueError):WORLD_9.step((0,0,0,0,0),'C')
        with self.assertRaises(ValueError):WORLD_9.inverse((0,0,0,0,0),'C')

    def test_repeatable_experiment(self):
        data=record_experiment()
        self.assertEqual(data['first_distinction']['status'],'DISTINGUISHED_B_ACTIONS')
        self.assertEqual(data['full_carrier_qualification']['first_divergence'],3)

if __name__=='__main__':unittest.main()