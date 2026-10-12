"""Finite owner-law tests for the standalone seed-first witness."""
import unittest
from finite_goal_priority import Law
from finite_seed_first import select_and_extend

class FiniteSeedFirstTests(unittest.TestCase):
    def test_early_union_recovers_joint_goals(self):
        r=select_and_extend(Law((0,0,1)),Law((0,0,0)),((0,1,1),(0,2,0)))
        self.assertEqual(r['status'],'GOALS_CARRIED')
        self.assertEqual(r['paths'],('ABAA','ABBABA'))
        self.assertEqual((len(r['pairs']),len(r['edges']),len(r['excluded'])),(9,13,5))
        self.assertEqual(r['goals'],(((0,1,1),(0,1,0),'ABBABA'),
                                     ((0,2,0),(0,2,0),'ABAA')))

    def test_incompatible_goals_stay_partial(self):
        r=select_and_extend(Law((0,0,1)),Law((0,0,0)),((0,1,0),(0,1,1)))
        self.assertEqual(r['status'],'PARTIAL_GOALS')
        self.assertEqual(len(r['goals']),1)

    def test_identical_law_closes_every_edge(self):
        a=Law((0,0,1))
        r=select_and_extend(a,a,((0,1,0),(0,1,1)))
        self.assertEqual((len(r['pairs']),len(r['edges']),len(r['excluded'])),(27,54,0))

    def test_independent_replay_and_injectivity(self):
        a=Law((0,0,1))
        for phi,goals in [((0,0,0),((0,1,1),(0,2,0))),
                          ((1,0,1),((0,1,0),(0,1,1))),
                          ((0,0,1),((0,1,0),(0,1,1)))]:
            b=Law(phi);r=select_and_extend(a,b,goals)
            fwd=dict(r['pairs'])
            self.assertEqual(len(fwd),len(set(fwd.values())))
            for s,action,t,ns,nt in r['edges']:
                self.assertEqual((fwd[s],fwd[t]),(ns,nt))
                self.assertEqual((a.step(s,action),b.step(ns,action)),(t,nt))
            for g,n,w in r['goals']:
                self.assertEqual((a.follow(w),b.follow(w)),(g,n))

    def test_depth_and_inputs(self):
        a=Law((0,0,1))
        r=select_and_extend(a,a,((0,1,1),),depth=0)
        self.assertEqual(r['status'],'GOALS_OUTSIDE_DEPTH')
        for goals in ((),((0,1,1),(0,1,1)),((5,0,0),)):
            with self.assertRaises(ValueError):select_and_extend(a,a,goals)
        for kwargs in ({'depth':-1},{'depth':True},{'variants':0},{'limit':17}):
            with self.assertRaises(ValueError):select_and_extend(a,a,((0,1,1),),**kwargs)

if __name__ == '__main__':unittest.main()
