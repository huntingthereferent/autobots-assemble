"""Mixed finite tasks keep edge, path and destination witness contracts separate."""
import copy
import unittest

from ab_chatbot_mixed_obligations import (read_mixed_task,MixedTaskSession,MixedObligationPortfolio)
import test_ab_chatbot_evidence_prefilter as fx

GOALS=[[0,1,1],[0,2,0]]
PATH1={'word':'ABAA','old_destination':[0,2,0],'new_destination':[0,2,0]}
PATH2={'word':'ABBABA','old_destination':[0,1,1],'new_destination':[0,1,0]}
D1={'source':[0,1,1],'image':[0,1,0]}
D2={'source':[0,2,0],'image':[0,2,0]}
EDGE_A={'state':[0,0,0],'action':'A'}
EDGE_B={'state':[0,0,0],'action':'B'}
TASK={'goals':GOALS,'required_edges':[EDGE_A],
      'required_paths':[PATH1,PATH2], 'required_destinations':[D1,D2]}

def completed(agent):
    for _ in range(50):
        r=agent.advance(max_new_edges=108)
        if r.status not in ('SEARCHING','EVALUATING'):
            return r
    raise AssertionError('bounded task did not finish')

class MixedTests(unittest.TestCase):
    def make(self,**kwargs):
        helper=fx.EvidencePrefilterTests()
        self.addCleanup(helper.doCleanups)
        return helper.make(**kwargs)

    def test_accepts_typed_input_and_preserves_original(self):
        a=read_mixed_task(TASK)
        self.assertEqual(a.status,'TASK_ACCEPTED')
        self.assertEqual(len(a.contract.required_paths),2)
        self.assertEqual(len(a.contract.required_destinations),2)
        clone=copy.deepcopy(TASK)
        clone['required_paths'].reverse()
        clone['required_destinations'].reverse()
        self.assertEqual(a.contract.fingerprint,read_mixed_task(clone).contract.fingerprint)
        self.assertIn('ABBABA',a.contract.original_input)

    def test_all_three_types_admitted_in_same_extension(self):
        old,new=self.make()
        sess=MixedTaskSession(old,new,TASK,**fx.OPTIONS)
        self.assertIsInstance(sess.agent,MixedObligationPortfolio)
        res=completed(sess.agent)
        self.assertEqual(res.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(len(res.selected.carried),2)
        results=dict(sess.agent.obligation_results)
        selected=results[res.selected.words]
        self.assertEqual([r.kind for r in selected],['EDGE','DESTINATION','DESTINATION','PATH','PATH'])
        self.assertTrue(all(r.satisfied for r in selected))
        self.assertEqual((res.observed_old,res.observed_new),(28,18))
        self.assertEqual(sess.advance(max_new_edges=0).status,'GOALS_CARRIED_WITNESSED')

    def test_incompatible_edges_and_paths_cannot_be_composed_across_candidates(self):
        old,new=self.make()
        task=copy.deepcopy(TASK)
        task['required_edges']=[EDGE_B]
        session=MixedTaskSession(old,new,task,**fx.OPTIONS)
        r=completed(session.agent)
        self.assertEqual(r.status,'REQUIREMENTS_UNPROVED')
        self.assertIsNone(r.selected)
        self.assertEqual(r.possible_goal_images,())
        self.assertTrue(session.agent.obligation_results)
        self.assertFalse(any(all(p.satisfied for p in items) for _,items in session.agent.obligation_results))

    def test_destination_identity_does_not_substitute_for_path_history(self):
        old,new=self.make()
        agent=MixedTaskSession(old,new,TASK,**fx.OPTIONS).agent
        completed(agent)
        winner=next(ext for ext in agent._extenders if ext.forward.get((0,1,1))==(0,1,0))
        self.assertTrue(any(r.kind=='PATH' and r.satisfied for r in agent._check(winner)))
        removed=winner.edges.pop(((0,0,0),'A'))
        try:
            checks=agent._check(winner)
            self.assertTrue(any(r.kind=='DESTINATION' and r.satisfied for r in checks))
            self.assertTrue(any(r.kind=='PATH' and not r.satisfied for r in checks))
        finally:
            winner.edges[((0,0,0),'A')]=removed

    def test_inconsistent_identity_fails_without_observations(self):
        old,new=self.make()
        task=copy.deepcopy(TASK)
        task['required_destinations']=[{'source':[0,1,1],'image':[0,2,0]}]
        session=MixedTaskSession(old,new,task,**fx.OPTIONS)
        self.assertEqual(session.advance().status,'INCONSISTENT_TASK')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_ambiguous_input_never_executes(self):
        old,new=self.make()
        session=MixedTaskSession(old,new,'keep the endpoints and history',**fx.OPTIONS)
        self.assertEqual(session.advance().status,'UNKNOWN_TASK')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_malformed_input_collections_and_unknown_keys(self):
        for task in [
            {'goals':GOALS,'required_paths':{}},
            {'goals':GOALS,'required_paths':[{'word':'AC','old_destination':[0,0,0],'new_destination':[0,0,0]}]},
            {'goals':GOALS,'required_destinations':[{'source':[0,0,True],'image':[0,0,0]}]},
            {'goals':GOALS,'required_destinations':[D1,D1]},
            {'goals':GOALS,'required_edges':False,'required_paths':[PATH1]},
            {'goals':GOALS,'required_paths':[PATH1],'extra':'ignored?'},
        ]:
            with self.subTest(task=task):
                self.assertIsNone(read_mixed_task(task).contract)

    def test_revision_change_revokes_claim(self):
        old,new=self.make()
        sess=MixedTaskSession(old,new,TASK,**fx.OPTIONS)
        completed(sess.agent)
        old.snapshot.revision+=1
        r=sess.advance(max_new_edges=0)
        self.assertEqual(r.status,'UNKNOWN_VERSION')
        self.assertIsNone(r.report.selected)

    def test_admitted_edge_tampering_causes_wall(self):
        old,new=self.make()
        sess=MixedTaskSession(old,new,TASK,**fx.OPTIONS)
        completed(sess.agent)
        old.snapshot.edges[((0,0,0),'A')]=(2,2,2)
        r=sess.advance(max_new_edges=0)
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertIsNone(r.report.selected)

    def test_short_budget_resumes_and_keeps_fingerprint(self):
        old,new=self.make()
        sess=MixedTaskSession(old,new,TASK,**fx.OPTIONS)
        r=sess.advance(max_new_edges=0)
        self.assertEqual(r.status,'SEARCHING')
        self.assertEqual(r.contract.fingerprint,sess.intake.contract.fingerprint)
        self.assertEqual(completed(sess.agent).status,'GOALS_CARRIED_WITNESSED')

    def test_remote_cannot_be_reported_as_local_witness(self):
        old,new=self.make(remote_new=True)
        sess=MixedTaskSession(old,new,TASK,**fx.OPTIONS)
        r=completed(sess.agent)
        self.assertNotIn(r.status,('GOALS_CARRIED_WITNESSED','PARTIAL_GOALS_WITNESSED'))

    def test_goal_or_edge_only_uses_original_session(self):
        old,new=self.make()
        s=MixedTaskSession(old,new,{'goals':GOALS},**fx.OPTIONS)
        self.assertIsNone(s.agent)
        self.assertIsNotNone(s.legacy)
        s=MixedTaskSession(old,new,{'goals':GOALS,'required_edges':[EDGE_A,EDGE_B]},**fx.OPTIONS)
        self.assertIsNone(s.agent)
        self.assertIsNotNone(s.legacy)
        s=MixedTaskSession(old,new,{'goals':GOALS,'required_edge':EDGE_B},**fx.OPTIONS)
        self.assertIsNone(s.agent)
        self.assertIsNotNone(s.legacy)
        s=MixedTaskSession(old,new,'goals: (0,1,1), (0,2,0); require: edge (0,0,0) B',**fx.OPTIONS)
        self.assertIsNone(s.agent)
        self.assertIsNotNone(s.legacy)
        s=MixedTaskSession(old,new,{'goals':GOALS,'required_edge':EDGE_B},**fx.OPTIONS)
        self.assertIsNone(s.agent)
        self.assertIsNotNone(s.legacy)
        s=MixedTaskSession(old,new,'goals: (0,1,1), (0,2,0); require: edges (0,0,0) B, (0,1,0) B',**fx.OPTIONS)
        self.assertIsNone(s.agent)
        self.assertIsNotNone(s.legacy)

if __name__=='__main__':unittest.main()
