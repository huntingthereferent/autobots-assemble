"""Proof-scoped pruning: cached required-edge contradictions only."""
import unittest

import test_ab_chatbot_path_union as path_fixture
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_evidence_prefilter import (
    RequiredEdgePortfolio, inspect_required_edge)

OLD, NEW = (0,0,1), (0,0,0)
GOALS = ((0,1,1), (0,2,0))
REQUIRED = ((0,0,0), 'B')
OPTIONS = dict(max_depth=6,variants_per_goal=4,candidate_limit=7,max_trials=12)


def complete(agent):
    for _ in range(40):
        report=agent.advance(max_new_edges=108)
        if report.status not in ('SEARCHING','EVALUATING'):
            return report
    raise AssertionError('bounded test failed to terminate')


class EvidencePrefilterTests(unittest.TestCase):
    def make(self, *,remote_new=False):
        helper=path_fixture.PathUnionTests()
        self.addCleanup(helper.doCleanups)
        _, old, new, _, _=helper.make(OLD,NEW,depth=0,budget=54,remote_new=remote_new)
        return old,new

    def test_preprune_and_actual_trial_savings(self):
        old,new=self.make()
        guarded=RequiredEdgePortfolio(old,new,GOALS,required_edge=REQUIRED,**OPTIONS)
        report=complete(guarded)
        self.assertEqual((guarded.before_filter,len(guarded.selections)),(11,9))
        self.assertEqual(len(guarded.certificates),2)
        self.assertEqual(report.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(len(report.selected.carried),1)
        self.assertEqual(len(guarded.finished),9)
        self.assertTrue(all(cert.action=='B' for cert in guarded.certificates))
        self.assertTrue(any(REQUIRED in e.edges for e in guarded._extenders))
        for cert,seed in zip(guarded.certificates,guarded._rejected_selections):
            self.assertEqual(inspect_required_edge(old,new,seed,REQUIRED).certificate,cert)
        self.assertEqual((report.observed_old,report.observed_new),(26,18))

    def test_unpruned_eligible_oracle_does_not_claim_more_goals(self):
        old,new=self.make()
        baseline=PostExtensionPortfolio(old,new,GOALS,**OPTIONS)
        prior=complete(baseline)
        self.assertEqual(len(baseline.finished),11)
        valid=[trial for trial,ext in zip(baseline.finished,baseline._extenders)
               if REQUIRED in ext.edges]
        self.assertTrue(valid)
        best=max(valid,key=lambda t:(len(t.carried),t.admitted_edges,t.paired_states,
                                       -t.excluded_edges,tuple((-len(w),w) for w in t.words)))
        old2,new2=self.make()
        improved=RequiredEdgePortfolio(old2,new2,GOALS,required_edge=REQUIRED,**OPTIONS)
        outcome=complete(improved)
        self.assertEqual(outcome.selected,best)
        # The unconstrained winner of course may violate the newly declared edge.
        self.assertEqual(len(prior.selected.carried),2)
        self.assertEqual(len(outcome.selected.carried),1)
        self.assertEqual((prior.observed_old,prior.observed_new),(28,18))
        self.assertEqual((outcome.observed_old,outcome.observed_new),(26,18))

    def test_missing_observation_does_not_authorize_pruning(self):
        old,new=self.make()
        agent=RequiredEdgePortfolio(old,new,GOALS,required_edge=REQUIRED,**OPTIONS)
        agent.advance(max_new_edges=108)
        candidate=agent.selections[0]
        old.snapshot.edges.pop(REQUIRED)
        self.assertEqual(inspect_required_edge(old,new,candidate,REQUIRED).verdict,'UNDECIDED')
        self.assertEqual(agent.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_tampered_required_edge_revokes_certificates(self):
        old,new=self.make()
        agent=RequiredEdgePortfolio(old,new,GOALS,required_edge=REQUIRED,**OPTIONS)
        agent.advance(max_new_edges=108)
        self.assertEqual(len(agent.certificates),2)
        old.snapshot.edges[REQUIRED]=(2,2,2)
        self.assertEqual(agent.advance(max_new_edges=0).status,'WALL_OBSERVATION')

    def test_stale_version_revokes_filter(self):
        old,new=self.make()
        agent=RequiredEdgePortfolio(old,new,GOALS,required_edge=REQUIRED,**OPTIONS)
        agent.advance(max_new_edges=108)
        old.snapshot.revision += 1
        self.assertEqual(agent.advance(max_new_edges=0).status,'UNKNOWN_VERSION')

    def test_remote_source_does_not_become_local_pruning_proof(self):
        old,new=self.make(remote_new=True)
        agent=RequiredEdgePortfolio(old,new,GOALS,required_edge=REQUIRED,**OPTIONS)
        report=agent.advance(max_new_edges=108)
        self.assertIn(report.status,('EVALUATING','SEARCHING'))
        self.assertEqual(len(agent.certificates),0)

    def test_no_candidate_can_satisfy_required_edge(self):
        old,new=self.make()
        agent=RequiredEdgePortfolio(old,new,GOALS,
                                    required_edge=((0,0,1),'A'),**OPTIONS)
        result=complete(agent)
        self.assertEqual(result.status,'REQUIRED_EDGE_UNPROVED')
        self.assertIsNone(result.selected)

    def test_validation_of_finite_requirement(self):
        old,new=self.make()
        for edge in (((3,0,0),'B'),((0,0,0),'C'),('bad','B'),None):
            with self.assertRaises(ValueError):
                RequiredEdgePortfolio(old,new,GOALS,required_edge=edge,**OPTIONS)

if __name__=='__main__':unittest.main()
