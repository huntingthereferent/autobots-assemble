"""Regression and independent law oracle for alternative greedy extension choice."""
import unittest

from ab_chatbot_alternative_extension import AlternativeExtensionChooser
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
import test_ab_chatbot_path_union as fixture


def law_oracle(old_phi, new_phi, order):
    """Independent whole-rule simulation; does not use bridge or extender."""
    old,new=FiniteSystem(old_phi),FiniteSystem(new_phi)
    root=(0,0,0)
    fwd={root:root};rev={root:root};queue=[(root,a) for a in order]
    edges=[];excluded=[];i=0
    while i<len(queue):
        s,a=queue[i];i+=1
        ns=fwd[s]; t=old.step(s,a);nt=new.step(ns,a)
        if (t in fwd and fwd[t]!=nt) or (nt in rev and rev[nt]!=t):
            excluded.append((s,a,t,nt))
        else:
            if t not in fwd:
                fwd[t]=nt;rev[nt]=t
                queue.extend((t,l) for l in order)
            edges.append((s,a,t,ns,nt))
    return tuple(sorted(fwd.items())),tuple(sorted(edges)),len(excluded)

class AlternativeExtensionTests(unittest.TestCase):
    def build(self,a=(0,0,1),b=(1,0,1),*,budget=54,remote=False):
        t=fixture.PathUnionTests()
        self.addCleanup(t.doCleanups)
        d,old,new,oldowner,newowner=t.make(a,b,depth=0,budget=budget,remote_new=remote)
        src=PathUnionAgent(d,((0,0,0),))
        return AlternativeExtensionChooser(src,((0,0,2),)),old,new,oldowner,newowner

    @staticmethod
    def finish(c, allowance=10):
        for _ in range(250):
            report=c.advance(max_new_edges_per_candidate=allowance)
            if report.status!='CONTINUING':return report
        raise AssertionError('candidate comparison did not terminate')

    def test_goal_changes_outcome_with_action_priority(self):
        c,*_=self.build()
        r=self.finish(c)
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(r.selected_order,'BA')
        ab,ba=r.alternatives
        self.assertEqual(ab.order,'AB')
        self.assertEqual((ab.state_pairs,ab.admitted_edges), (20,28))
        self.assertFalse(ab.goals)
        self.assertEqual((ba.state_pairs,ba.admitted_edges),(25,37))
        self.assertEqual(ba.goals,(((0,0,2),(0,0,1),'BBBBBB'),))
        self.assertEqual(r.possible_images,(((0,0,2),((0,0,1),)),))

    def test_independent_oracle_three_rule_pairs(self):
        for a,b in [((0,0,1),(1,0,1)),((0,0,1),(0,0,0)),((0,0,1),(0,0,1))]:
            with self.subTest(a=a,b=b):
                c,*_=self.build(a,b)
                r=self.finish(c)
                for order,e in c.extenders.items():
                    ref=law_oracle(a,b,order)
                    obs=e.advance(max_new_edges=0)
                    self.assertEqual((obs.state_pairs,obs.admitted_edges,len(obs.rejected)),ref)

    def test_no_early_selection_and_no_new_reads_at_zero_budget(self):
        c,old,new,*_=self.build()
        r=c.advance(max_new_edges_per_candidate=0)
        self.assertEqual(r.status,'CONTINUING')
        self.assertIsNone(r.selected_order)
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))
        r=c.advance(max_new_edges_per_candidate=1)
        self.assertEqual(r.status,'CONTINUING')
        self.assertIsNone(r.selected_order)
        self.assertLessEqual(len(old.snapshot.edges)+len(new.snapshot.edges),2)
        self.assertEqual(self.finish(c).status,'GOALS_CARRIED_WITNESSED')

    def test_budget_wall_recovers_without_claiming_success(self):
        c,old,new,*_=self.build(budget=2)
        r=self.finish(c)
        self.assertEqual(r.status,'UNKNOWN_BUDGET')
        self.assertIsNone(r.selected_order)
        old.snapshot.max_edges=54;new.snapshot.max_edges=54
        self.assertEqual(self.finish(c).status,'GOALS_CARRIED_WITNESSED')

    def test_old_code_default_action_order_unchanged(self):
        c,*_=self.build()
        self.assertEqual(c.extenders['AB'].action_order,'AB')
        self.assertEqual(c.extenders['BA'].action_order,'BA')
        self.assertEqual(c.extenders['AB'].queue[0][1],'A')
        self.assertEqual(c.extenders['BA'].queue[0][1],'B')

    def test_source_revision_invalidates_all_candidates(self):
        c,old,new,_,owner=self.build()
        self.finish(c)
        owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        new.ask('pin current version')
        r=c.advance(max_new_edges_per_candidate=0)
        self.assertEqual(r.status,'UNKNOWN_VERSION')
        self.assertIsNone(r.selected_order)

    def test_corrupted_edge_disallows_selection(self):
        c,old,new,*_=self.build()
        self.finish(c)
        e=c.extenders['BA']
        s,a,t,ns,nt=e.new_edges[0]
        old.snapshot.edges[(s,a)]=((2,2,2) if t!=(2,2,2) else (1,1,1))
        r=c.advance(max_new_edges_per_candidate=0)
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertIsNone(r.selected_order)

    def test_remote_owner_is_not_promoted(self):
        c,*_=self.build(remote=True)
        r=self.finish(c)
        self.assertEqual(r.status,'GOALS_CARRIED_REMOTE_REPORTED')

    def test_invalid_goals_and_budget(self):
        c,*_=self.build()
        for bad in (-1,109,True,1.5):
            with self.assertRaises(ValueError):
                c.advance(max_new_edges_per_candidate=bad)
        with self.assertRaises(ValueError):
            AlternativeExtensionChooser(PathUnionAgent(c.extenders['AB'].discovered,((0,0,0),)),())

if __name__=='__main__':unittest.main()
