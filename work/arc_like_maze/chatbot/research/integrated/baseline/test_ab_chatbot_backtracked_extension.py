"""Witness, negative controls and independent finite-law confirmation."""
import unittest

from ab_chatbot_backtracked_extension import BacktrackedGoalExtender
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
import test_ab_chatbot_path_union as fixture

ROOT = (0,0,0)
GOAL = (1,1,2)

def fixed_priority_oracle(a, b, order):
    old, new = FiniteSystem(a), FiniteSystem(b)
    forward={ROOT:ROOT}; inverse={ROOT:ROOT}; pending=[(ROOT,act) for act in order]
    for state, action in pending:
        t,n = old.step(state,action),new.step(forward[state],action)
        if (t in forward and forward[t]!=n) or (n in inverse and inverse[n]!=t):
            continue
        if t not in forward:
            forward[t]=n;inverse[n]=t
            pending.extend((t,act) for act in order)
    return forward

class BacktrackedExtensionTests(unittest.TestCase):
    def build(self, a=(0,0,1), b=(1,0,1), *, depth=6, budget=54, remote=False):
        f=fixture.PathUnionTests()
        self.addCleanup(f.doCleanups)
        d,old,new,oldowner,newowner=f.make(a,b,depth=0,budget=budget,
                                            remote_new=remote)
        return BacktrackedGoalExtender(old,new,GOAL,max_depth=depth),old,new,newowner

    @staticmethod
    def finish(a, allowance=108):
        for _ in range(220):
            r=a.advance(max_new_edges=allowance)
            if r.status not in ('SEARCHING','EXTENDING'):
                return r
        raise AssertionError('search not terminated')

    def test_both_fixed_priorities_miss_goal_but_branch_extension_carries_it(self):
        a,old,new,_=self.build()
        pair=((0,0,1),(1,0,1))
        for order in ('AB','BA'):
            self.assertNotIn(GOAL,fixed_priority_oracle(*pair,order))
        report=self.finish(a)
        self.assertEqual(report.status,'GOAL_CARRIED_WITNESSED')
        self.assertEqual((report.mapped_goal,report.goal_word),((1,1,1),'ABBBBB'))
        self.assertEqual((report.paired_states,report.admitted_edges,report.excluded_edges),(27,42,12))
        self.assertGreaterEqual(report.branch_alternatives,2)
        self.assertGreater(report.branch_rejections,0)
        self.assertGreaterEqual(len(report.selected_paths),1)
        o,n=FiniteSystem(pair[0]),FiniteSystem(pair[1])
        self.assertEqual(o.follow(report.goal_word),GOAL)
        self.assertEqual(n.follow(report.goal_word),report.mapped_goal)
        for s,action,t,ns,nt in a.last_extension.admitted_edges:
            self.assertEqual(o.step(s,action),t)
            self.assertEqual(n.step(ns,action),nt)
            self.assertEqual(dict(a.last_extension.state_pairs)[s],ns)
            self.assertEqual(dict(a.last_extension.state_pairs)[t],nt)

    def test_depth_limit_does_not_mean_unreachable(self):
        a,*_=self.build(depth=5)
        r=self.finish(a)
        self.assertEqual(r.status,'GOAL_OUTSIDE_SEARCH_BOUND')
        self.assertIsNone(r.goal_word)

    def test_zero_new_edges_preserves_observation_budget(self):
        a,old,new,_=self.build()
        r=a.advance(max_new_edges=0)
        self.assertEqual(r.status,'SEARCHING')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))
        self.assertEqual(self.finish(a).status,'GOAL_CARRIED_WITNESSED')

    def test_bounded_reads_per_call_and_resume(self):
        a,old,new,_=self.build()
        for _ in range(120):
            before=len(old.snapshot.edges)+len(new.snapshot.edges)
            r=a.advance(max_new_edges=2)
            after=len(old.snapshot.edges)+len(new.snapshot.edges)
            self.assertLessEqual(after-before,2)
            if r.status not in ('SEARCHING','EXTENDING'):break
        self.assertEqual(r.status,'GOAL_CARRIED_WITNESSED')

    def test_observation_wall_is_not_a_negative_answer(self):
        a,old,new,_=self.build(budget=2)
        r=self.finish(a)
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        old.snapshot.max_edges=new.snapshot.max_edges=54
        self.assertEqual(self.finish(a).status,'GOAL_CARRIED_WITNESSED')

    def test_repin_invalidates_result(self):
        a,old,new,owner=self.build()
        self.assertEqual(self.finish(a).status,'GOAL_CARRIED_WITNESSED')
        owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        new.ask('pin current version')
        self.assertEqual(a.advance(max_new_edges=0).status,'UNKNOWN_VERSION')

    def test_corrupted_new_edge_fails_full_replay(self):
        a,old,new,_=self.build()
        self.assertEqual(self.finish(a).status,'GOAL_CARRIED_WITNESSED')
        s,act,t,ns,nt=a.last_extension.new_edges[-1]
        old.snapshot.edges[(s,act)]=(2,2,2) if t!=(2,2,2) else (1,1,1)
        self.assertEqual(a.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_remote_reports_not_witnessed(self):
        a,*_=self.build(remote=True)
        self.assertEqual(self.finish(a).status,'GOAL_CARRIED_REMOTE_REPORTED')

    def test_invalid_depth_goal_and_allowance(self):
        a,old,new,_=self.build()
        for invalid in (-1,9,True,1.2):
            with self.assertRaises(ValueError):BacktrackedGoalExtender(old,new,GOAL,max_depth=invalid)
        with self.assertRaises(ValueError):BacktrackedGoalExtender(old,new,(3,0,0))
        for invalid in (-1,109,True,1.2):
            with self.assertRaises(ValueError):a.advance(max_new_edges=invalid)

if __name__=='__main__':unittest.main()
