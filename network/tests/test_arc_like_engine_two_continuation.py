"""Engine 2 continuation witnesses through ACTUAL ConstructedEngine/WindowProcess."""
import json
import unittest
from itertools import product

from work.arc_like_maze.engine_one import ConstructedEngine
from work.arc_like_maze.window_two import WindowProcess
from work.arc_like_maze.engine_two_continuation import (
    EngineTwoContinuationKernel, ContinuationWitness, FIBER,
    _permutation, _cycles, _intertwiner, _fixed,
)

F3=(0,1,2)
ZERO=(0,)*9
Q0=(1,2,0,0,0,0,1,1,1)
Q1=tuple(z*z%3 for v,z in product(F3,repeat=2))
SPIKE_10=(0,0,0,1)+(0,)*5
SPIKE_11=(0,0,0,0,1)+(0,)*4


def engine(q2,version=0):
    return ConstructedEngine(WindowProcess(1,(Q0,Q1,q2),(ZERO,)),version)


def negative():
    return engine(ZERO,4),engine(SPIKE_10,5)


def positive():
    return engine(SPIKE_10,6),engine(SPIKE_11,7)


class EngineTwoActualKernelContinuationTests(unittest.TestCase):
    def test_constructed_engine_exposes_the_same_real_research_entry(self):
        left,right=negative()
        via_engine=left.watch_B_against(right)
        via_kernel=EngineTwoContinuationKernel.enter(left,right)
        self.assertEqual(via_engine,via_kernel)
        self.assertEqual(via_engine.advance(8).status,"UNKNOWN")

    def test_existing_inverse_engine_returns_a_wall_for_window_research_law(self):
        from work.arc_like_maze.engine_one import (
            InverseConstructionEngine, Requirements,
        )
        current,_=negative()
        result=current.evolve(
            InverseConstructionEngine(),
            Requirements("window48",relation="ROOTED_FULL"),
        )
        self.assertEqual(result.status,"WALL")
        self.assertIsNone(result.engine)
        self.assertIn("WindowProcess",result.wall)

    def test_entry_uses_actual_finite_two_input_processes_and_versions(self):
        left,right=negative()
        w=EngineTwoContinuationKernel.enter(left,right)
        self.assertIsInstance(w.left,WindowProcess)
        self.assertEqual(w.summary()['source_engine_versions'],(4,5))
        self.assertEqual(len(FIBER),81)
        self.assertEqual(len(set(FIBER)),81)
        self.assertTrue(all(state[0]==2 for state in FIBER))
        for s in FIBER:
            self.assertEqual(w.left.step(s,'B'),left.step(s,'B'))
            self.assertEqual(w.right.step(s,'B'),right.step(s,'B'))
            self.assertIn(left.step(s,'B'),FIBER)
            self.assertIn(right.step(s,'B'),FIBER)
            self.assertNotIn(left.step(s,'A'),FIBER)

    def test_negative_exact_81_state_cycle_structure(self):
        w=EngineTwoContinuationKernel.enter(*negative())
        a,b=_permutation(w.left),_permutation(w.right)
        self.assertEqual(sorted(len(x) for x in _cycles(a)),[9]*9)
        self.assertEqual(sorted(len(x) for x in _cycles(b)),[27]*3)
        self.assertEqual(_fixed(a,9),tuple(range(81)))
        self.assertEqual(_fixed(b,9),())

    def test_budget_eight_reenters_and_budget_nine_distinguishes(self):
        l,r=negative()
        first=EngineTwoContinuationKernel.enter(l,r).advance(8)
        self.assertEqual(first.status,'UNKNOWN')
        self.assertEqual(first.budgets,(8,))
        self.assertEqual(len(first.observations),8)
        self.assertTrue(all(len(o.left_fixed)==len(o.right_fixed)==0
                            for o in first.observations))
        resumed=EngineTwoContinuationKernel.reenter(
            first.snapshot(),left_engine=l,right_engine=r)
        final=resumed.advance(9)
        self.assertEqual(final.status,'DISTINGUISHED')
        self.assertEqual(final.distinguishing_depth,9)
        self.assertEqual(final.observations[:8],first.observations)
        self.assertEqual(final.budgets,(8,9))
        self.assertEqual((len(final.observations[8].left_fixed),
                          len(final.observations[8].right_fixed)),(81,0))
        self.assertEqual(EngineTwoContinuationKernel.exit(final)['status'],
                         'DISTINGUISHED')

    def test_late_matching_counts_do_not_erase_first_obstruction(self):
        first=EngineTwoContinuationKernel.enter(*negative()).advance(9)
        after=first.advance(27,audit_after_distinction=True)
        self.assertEqual(after.status,'DISTINGUISHED')
        self.assertEqual(after.distinguishing_depth,9)
        self.assertEqual(after.observations[:9],first.observations)
        self.assertEqual(tuple(map(len,(after.observations[-1].left_fixed,
                                        after.observations[-1].right_fixed))),
                         (81,81))

    def test_positive_budget_26_is_unknown_then_verified_b_only_at_27(self):
        left,right=positive()
        initial=EngineTwoContinuationKernel.enter(left,right).advance(26)
        self.assertEqual(initial.status,'UNKNOWN')
        self.assertIsNone(initial.bijection)
        next_w=EngineTwoContinuationKernel.reenter(
            initial.snapshot(),left_engine=left,right_engine=right).advance(27)
        self.assertEqual(next_w.observations[:26],initial.observations)
        self.assertEqual(next_w.budgets,(26,27))
        self.assertEqual(next_w.status,'EQUIVALENT_FOR_B_ONLY')
        self.assertEqual(len(set(next_w.bijection)),81)
        p,q=_permutation(next_w.left),_permutation(next_w.right)
        self.assertTrue(all(next_w.bijection[p[i]]==q[next_w.bijection[i]]
                            for i in range(81)))
        self.assertEqual(EngineTwoContinuationKernel.exit(next_w)[
            'does_not_establish'],'simultaneous A/B conjugacy')

    def test_constructed_positive_intertwiner_is_not_just_matching_counts(self):
        w=EngineTwoContinuationKernel.enter(*positive())
        p,q=_permutation(w.left),_permutation(w.right)
        h=_intertwiner(p,q)
        self.assertNotEqual(h,tuple(range(81)))
        self.assertEqual(set(h),set(range(81)))
        self.assertTrue(all(h[p[i]]==q[h[i]] for i in range(81)))
        self.assertEqual(w.advance(8).status,'UNKNOWN')

    def test_changed_law_fails_reentry_with_original_source_metadata(self):
        w=EngineTwoContinuationKernel.enter(*negative()).advance(8)
        payload=json.loads(w.snapshot())
        payload['right']['stem'][2][3]=2
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(json.dumps(payload))

    def test_changed_observation_and_missing_depth_fail_reentry(self):
        w=EngineTwoContinuationKernel.enter(*negative()).advance(8)
        payload=json.loads(w.snapshot())
        payload['observations'][0]['left_fixed']=[0]
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(json.dumps(payload))
        payload=json.loads(w.snapshot())
        payload['observations'][3]['depth']=5
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(json.dumps(payload))

    def test_declared_fiber_generator_and_schema_cannot_be_upgraded_to_AB(self):
        w=EngineTwoContinuationKernel.enter(*positive()).advance(8)
        for key,value in (('relation','SIMULTANEOUS_AB'),('generator','AB'),
                          ('schema','unknown-schema'),('domain',[])):
            payload=json.loads(w.snapshot())
            payload[key]=value
            with self.assertRaises(ValueError):
                ContinuationWitness.reenter(json.dumps(payload))

    def test_original_constructed_engine_version_is_not_silently_replaced(self):
        l,r=negative()
        w=EngineTwoContinuationKernel.enter(l,r).advance(8)
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(w.snapshot(),
                left_engine=engine(ZERO,99),right_engine=r)
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(w.snapshot(),
                left_engine=l,right_engine=engine(SPIKE_11,7))

    def test_unknown_cannot_be_forged_into_positive_conclusion(self):
        w=EngineTwoContinuationKernel.enter(*positive()).advance(26)
        d=json.loads(w.snapshot())
        d['status']='EQUIVALENT_FOR_B_ONLY'
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(json.dumps(d))
        d=json.loads(w.snapshot())
        d['status']='DISTINGUISHED'
        d['distinguishing_depth']=9
        with self.assertRaises(ValueError):
            ContinuationWitness.reenter(json.dumps(d))

    def test_terminal_decision_stops_except_explicit_negative_audit(self):
        negative_w=EngineTwoContinuationKernel.enter(*negative()).advance(9)
        with self.assertRaises(ValueError):
            negative_w.advance(27)
        positive_w=EngineTwoContinuationKernel.enter(*positive()).advance(27)
        with self.assertRaises(ValueError):
            positive_w.advance(28,audit_after_distinction=True)

    def test_no_budget_rewind_or_boolean_budget(self):
        w=EngineTwoContinuationKernel.enter(*negative()).advance(8)
        with self.assertRaises(ValueError):
            w.advance(7)
        with self.assertRaises(ValueError):
            w.advance(True)
        self.assertEqual(w.advance(8),w)

    def test_full_243_state_conclusion_is_not_inferred(self):
        w=EngineTwoContinuationKernel.enter(*negative()).advance(9)
        allstates=tuple(product(F3,repeat=5))
        self.assertEqual(len(allstates),243)
        self.assertEqual(len(FIBER),81)
        self.assertEqual(w.status,'DISTINGUISHED')
        self.assertEqual(w.summary()['state_count'],81)
        self.assertFalse(w.summary()['A_preserves_fiber'])
        self.assertEqual(w.summary()['generator'],'B')

    def test_other_process_grammars_and_engine_one_laws_are_explicit_walls(self):
        from work.arc_like_maze.window_combined import CombinedWorld
        l,r=negative()
        with self.assertRaises(TypeError):
            EngineTwoContinuationKernel.enter(ConstructedEngine(
                CombinedWorld(0,0,0,0),0),r)
        with self.assertRaises(ValueError):
            EngineTwoContinuationKernel.enter(ConstructedEngine(
                WindowProcess(1,(Q0,Q1),(ZERO,)),0),r)
        with self.assertRaises(ValueError):
            EngineTwoContinuationKernel.enter(ConstructedEngine(
                WindowProcess(1,(Q0,Q1,SPIKE_10),(Q0,)),0),r)

    def test_exit_requires_the_actual_verified_witness(self):
        with self.assertRaises(TypeError):
            EngineTwoContinuationKernel.exit({'status':'DISTINGUISHED'})
        w=EngineTwoContinuationKernel.enter(*negative()).advance(8)
        out=EngineTwoContinuationKernel.exit(w)
        self.assertEqual(out['status'],'UNKNOWN')
        self.assertIsNone(out['distinguishing_depth'])
        self.assertFalse(out['bijection_verified'])


if __name__=='__main__':
    unittest.main(verbosity=2)
