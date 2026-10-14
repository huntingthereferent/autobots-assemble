"""Independent finite-law scoring and evidence controls for completed extensions."""
import unittest
from dataclasses import replace
from itertools import combinations

from ab_chatbot_backtracked_extension import BacktrackedGoalExtender
from ab_chatbot_extension_portfolio import CompletedExtensionPortfolio
from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_language_bridge import PinnedEdges
import test_ab_chatbot_path_union as fixture

G0, G1 = (0,1,0), (0,1,1)

class ExtensionPortfolioTests(unittest.TestCase):
    def build(self, a=(0,0,1), b=(0,0,0), *, remote=False, finish=True):
        source=fixture.PathUnionTests()
        self.addCleanup(source.doCleanups)
        _, old, new, _, new_owner=source.make(a,b,depth=0,budget=54,remote_new=remote)
        agents=tuple(BacktrackedGoalExtender(old,new,g,max_depth=6)
                     for g in (G0,G1))
        if finish:
            for x in agents:
                for _ in range(100):
                    r=x.advance(max_new_edges=108)
                    if r.status not in ('SEARCHING','EXTENDING'):
                        break
                self.assertIn(r.status,('GOAL_CARRIED_WITNESSED','GOAL_CARRIED_REMOTE_REPORTED'))
        return agents,old,new,new_owner

    @staticmethod
    def independent_reference(candidates,oldlaw,newlaw,goals):
        """Compute subsets separately, replaying finite rules without bridge caches."""
        best=None
        count=0
        for n in range(1,len(candidates)+1):
            for indices in combinations(range(len(candidates)),n):
                forward={}; reverse={}; edges={}; valid=True
                for i in indices:
                    r=candidates[i].last_extension
                    for state,image in r.state_pairs:
                        if state in forward and forward[state]!=image or image in reverse and reverse[image]!=state:
                            valid=False;break
                        forward[state]=image; reverse[image]=state
                    if not valid:break
                    for edge in r.admitted_edges:
                        s,a,t,ns,nt=edge
                        if (s,a) in edges and edges[(s,a)]!=edge:
                            valid=False;break
                        edges[(s,a)]=edge
                    if not valid:break
                if not valid:continue
                for s,a,t,ns,nt in edges.values():
                    if (forward.get(s),forward.get(t))!=(ns,nt) or (oldlaw.step(s,a),newlaw.step(ns,a))!=(t,nt):
                        valid=False;break
                if not valid:continue
                count+=1
                score=(sum(g in forward for g in goals),len(edges),len(forward),-n)
                if best is None or score>best:
                    best=score
        return best,count

    def test_independently_completed_extensions_can_be_incompatible(self):
        agents,old,new,_=self.build()
        r=CompletedExtensionPortfolio(agents,(G0,G1)).run()
        self.assertEqual(r.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(len(r.selected.carried_goals),1)
        self.assertEqual(r.selected.candidate_indices,(0,))
        self.assertEqual((len(r.selected.paired_states),len(r.selected.admitted_edges)),(9,15))
        self.assertEqual(r.compatible_subsets,2)
        self.assertEqual(len(r.conflicts),1)
        self.assertEqual(r.conflicts[0].cause,'TARGET_COLLISION')
        w=r.conflicts[0].witness
        self.assertNotEqual(w.old_equal,w.new_equal)
        a,b=FiniteSystem((0,0,1)),FiniteSystem((0,0,0))
        self.assertEqual(w.old_equal,a.follow(w.left_word)==a.follow(w.right_word))
        self.assertEqual(w.new_equal,b.follow(w.left_word)==b.follow(w.right_word))
        self.assertEqual(self.independent_reference(agents,a,b,(G0,G1)),((1,15,9,-1),2))
        self.assertEqual(r.possible_goal_images[1][1],((0,1,0),))

    def test_compatible_identical_extensions_do_not_invent_extra_coverage(self):
        agents,old,new,_=self.build(b=(0,0,1))
        r=CompletedExtensionPortfolio(agents,(G0,G1)).run()
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((len(r.selected.carried_goals),len(r.selected.paired_states),
                          len(r.selected.admitted_edges)),(2,27,54))
        self.assertEqual(r.selected.candidate_indices,(0,))
        self.assertFalse(r.conflicts)
        self.assertEqual(r.compatible_subsets,3)

    def test_independent_reference_three_finite_rule_pairs(self):
        laws=[((0,0,1),(0,0,0)),((0,0,1),(0,0,1)),((1,0,1),(1,0,1))]
        for left,right in laws:
            with self.subTest(left=left,right=right):
                agents,*_=self.build(left,right)
                r=CompletedExtensionPortfolio(agents,(G0,G1)).run()
                score=(len(r.selected.carried_goals),len(r.selected.admitted_edges),
                       len(r.selected.paired_states),-len(r.selected.candidate_indices))
                self.assertEqual((score,r.compatible_subsets),
                                 self.independent_reference(agents,FiniteSystem(left),
                                                            FiniteSystem(right),(G0,G1)))

    def test_no_new_reads_and_repeated_result(self):
        agents,old,new,_=self.build()
        before=(dict(old.snapshot.edges),dict(new.snapshot.edges))
        p=CompletedExtensionPortfolio(agents,(G0,G1))
        one=p.run()
        self.assertEqual(p.run(),one)
        self.assertEqual(before,(old.snapshot.edges,new.snapshot.edges))

    def test_corrupted_admitted_edge_fails_closed(self):
        agents,old,new,_=self.build()
        s,a,t,ns,nt=agents[0].last_extension.admitted_edges[0]
        old.snapshot.edges[(s,a)]=(1,1,2) if t!=(1,1,2) else (2,2,2)
        self.assertEqual(CompletedExtensionPortfolio(agents,(G0,G1)).run().status,
                         'WALL_OBSERVATION')

    def test_repin_invalidates_completed_selection(self):
        agents,old,new,owner=self.build()
        self.assertEqual(CompletedExtensionPortfolio(agents,(G0,G1)).run().status,
                         'PARTIAL_GOALS_WITNESSED')
        owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        new.ask('pin current version')
        self.assertEqual(CompletedExtensionPortfolio(agents,(G0,G1)).run().status,
                         'UNKNOWN_VERSION')

    def test_unfinished_candidates_are_not_passes(self):
        agents,*_=self.build(finish=False)
        self.assertEqual(CompletedExtensionPortfolio(agents,(G0,G1)).run().status,
                         'UNKNOWN_INCOMPLETE')

    def test_remote_origin_is_labeled_as_reported(self):
        agents,*_=self.build(remote=True)
        self.assertEqual(CompletedExtensionPortfolio(agents,(G0,G1)).run().status,
                         'PARTIAL_GOALS_REMOTE_REPORTED')

    def test_reject_unsupported_inputs_and_mixed_sources(self):
        agents,*_=self.build()
        for goals in ((),(G0,G0),((5,1,1),)):
            with self.assertRaises(ValueError):
                CompletedExtensionPortfolio(agents,goals)
        with self.assertRaises(ValueError):
            CompletedExtensionPortfolio((agents[0],agents[0]),(G0,))
        agents2,*_=self.build()
        with self.assertRaises(ValueError):
            CompletedExtensionPortfolio((agents[0],agents2[1]),(G0,G1))

    def test_counterexample_changes_with_goal_not_global_claim(self):
        agents,*_=self.build()
        solo=CompletedExtensionPortfolio(agents,(G1,)).run()
        self.assertEqual(solo.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(solo.selected.candidate_indices,(1,))
        dual=CompletedExtensionPortfolio(agents,(G0,G1)).run()
        self.assertEqual(dual.status,'PARTIAL_GOALS_WITNESSED')

if __name__=='__main__':unittest.main()
