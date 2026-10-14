"""Tests for all-of requirements, task provenance, replay, unknown boundaries."""
import copy
import unittest

from ab_chatbot_multi_required import (read_multi_task, MultiTaskSession,
                                       MultiRequiredEdgePortfolio)
from ab_chatbot_task_contract import TaskContractSession
import test_ab_chatbot_evidence_prefilter as fixture

GOALS=((0,1,1),(0,2,0))
BOTH=(((0,0,0),'B'),((0,1,0),'B'))
UNPROVED=(((0,0,0),'B'),((0,0,1),'A'))
TASK='goals: (0,1,1), (0,2,0); require: edges (0,0,0) B, (0,1,0) B'
DICT={'goals': [[0,1,1],[0,2,0]],'required_edges': [
    {'state':[0,0,0], 'action':'B'}, {'state':[0,1,0],'action':'B'}]}


def completed(agent):
    for _ in range(45):
        result=agent.advance(max_new_edges=108)
        if result.status not in ('SEARCHING','EVALUATING'):
            return result
    raise AssertionError('did not terminate under tested bounds')

class MultiRequiredTests(unittest.TestCase):
    def make(self,remote_new=False):
        helper=fixture.EvidencePrefilterTests()
        self.addCleanup(helper.doCleanups)
        return helper.make(remote_new=remote_new)

    def test_grammar_schema_equivalent_with_original_text_retained(self):
        a,b=read_multi_task(TASK),read_multi_task(DICT)
        self.assertEqual((a.status,b.status),('TASK_ACCEPTED','TASK_ACCEPTED'))
        self.assertEqual(a.contract.fingerprint,b.contract.fingerprint)
        self.assertEqual(a.contract.goals,GOALS)
        self.assertEqual(a.contract.required_edges,BOTH)
        self.assertNotEqual(a.contract.original_input,b.contract.original_input)
        reverse=copy.deepcopy(DICT)
        reverse['required_edges'].reverse()
        self.assertEqual(read_multi_task(reverse).contract.fingerprint,a.contract.fingerprint)

    def test_bad_and_ambiguous_inputs_never_create_agent(self):
        bad=[{'goals':[[0,1,1]],'required_edges':[]},
             {'goals':[[0,1,1]],'required_edges':[{'state':[0,0,0],'action':'B'}]},
             {'goals':[[0,1,1]],'required_edges':[
                {'state':[0,0,0],'action':'B'},{'state':[0,0,0],'action':'B'}]},
             {'goals':[[0,1,1]],'required_edges':[
                {'state':[0,0,0],'action':'B'},{'state':[0,1,True],'action':'A'}]},
             {'goals':[[0,1,1]],'required_edges':[
                {'state':[0,0,0],'action':'b'},{'state':[0,1,0],'action':'A'}]},
             {'goals':[[0,1,1]],'required_edges':[], 'required_edge':{'state':[0,0,0],'action':'B'}},
             'goals: (0,1,1); keep B and A',
             'goals: (0,1,1); require: edges (0,0,0) B, (0,1,0) C']
        for item in bad:
            with self.subTest(item=item):
                r=read_multi_task(item)
                self.assertIn(r.status,('INVALID_TASK','UNSUPPORTED_TASK','UNKNOWN_TASK'))
                self.assertIsNone(r.contract)
        old,new=self.make()
        s=MultiTaskSession(old,new,'keep B and A')
        self.assertEqual(s.advance().status,'UNKNOWN_TASK')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_explicit_multiple_edges_are_jointly_admitted(self):
        old,new=self.make()
        s=MultiTaskSession(old,new,TASK,**fixture.OPTIONS)
        self.assertIsInstance(s.agent,MultiRequiredEdgePortfolio)
        report=completed(s.agent)
        self.assertEqual(report.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(len(report.selected.carried),1)
        self.assertEqual((s.agent.before_filter,len(s.agent.selections)),(11,9))
        self.assertEqual((report.observed_old,report.observed_new),(26,18))
        index=next(i for i,t in enumerate(s.agent.finished) if t == report.selected)
        self.assertTrue(all(edge in s.agent._extenders[index].edges for edge in BOTH))
        self.assertTrue(all(missing==() for _,missing in s.agent.missing_by_trial))
        self.assertEqual(len(s.agent.exclusions),2)
        self.assertEqual(s.advance(max_new_edges=0).status,'PARTIAL_GOALS_WITNESSED')

    def test_unproved_conjunction_does_not_lie_about_completion(self):
        old,new=self.make()
        data={'goals':DICT['goals'],'required_edges':[
            {'state':[0,0,0],'action':'B'},{'state':[0,0,1],'action':'A'}]}
        s=MultiTaskSession(old,new,data,**fixture.OPTIONS)
        r=completed(s.agent)
        self.assertEqual(r.status,'REQUIREMENTS_UNPROVED')
        self.assertIsNone(r.selected)
        self.assertTrue(s.agent.missing_by_trial)
        self.assertTrue(all(UNPROVED[1] in miss for _,miss in s.agent.missing_by_trial))
        self.assertEqual(r.possible_goal_images,())
        self.assertEqual((r.observed_old,r.observed_new),(26,18))

    def test_single_and_goal_only_fallback_preserves_legacy_routes(self):
        old,new=self.make()
        single={'goals':DICT['goals'],'required_edge':{'state':[0,0,0],'action':'B'}}
        self.assertEqual(MultiTaskSession(old,new,single,**fixture.OPTIONS).agent.__class__.__name__,'RequiredEdgePortfolio')
        self.assertEqual(MultiTaskSession(old,new,{'goals':DICT['goals']},**fixture.OPTIONS).agent.__class__.__name__,
                         'PostExtensionPortfolio')
        self.assertEqual(read_multi_task(single).contract.required_edges,(BOTH[0],))
        self.assertEqual(read_multi_task({'goals':DICT['goals']}).contract.required_edges,())

    def test_revision_invalidates_every_claim(self):
        old,new=self.make()
        s=MultiTaskSession(old,new,DICT,**fixture.OPTIONS)
        completed(s.agent)
        old.snapshot.revision+=1
        r=s.advance(max_new_edges=0)
        self.assertEqual(r.status,'UNKNOWN_VERSION')
        self.assertIsNone(r.report.selected)

    def test_cache_tampering_invalidates_any_saved_certificate(self):
        old,new=self.make()
        s=MultiTaskSession(old,new,DICT,**fixture.OPTIONS)
        s.advance(max_new_edges=108)
        self.assertEqual(len(s.agent.exclusions),2)
        old.snapshot.edges[BOTH[0]]=(2,2,2)
        r=s.advance(max_new_edges=0)
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertIsNone(r.report.selected)

    def test_remote_does_not_authorize_local_exclusion(self):
        old,new=self.make(remote_new=True)
        s=MultiTaskSession(old,new,DICT,**fixture.OPTIONS)
        r=s.advance(max_new_edges=108)
        self.assertIn(r.status,('SEARCHING','EVALUATING'))
        self.assertEqual(s.agent.exclusions,())

    def test_short_budget_preserves_contract_and_resumes(self):
        old,new=self.make()
        s=MultiTaskSession(old,new,DICT,**fixture.OPTIONS)
        first=s.advance(max_new_edges=0)
        self.assertEqual(first.status,'SEARCHING')
        last=completed(s.agent)
        self.assertEqual(last.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(first.contract.fingerprint,s.intake.contract.fingerprint)

    def test_existing_single_edge_result_matches_multi_edge_compatible_result(self):
        old,new=self.make()
        single=TaskContractSession(old,new,
                    {'goals':DICT['goals'],'required_edge':{'state':[0,0,0],'action':'B'}},
                    **fixture.OPTIONS)
        r1=completed(single.agent)
        old2,new2=self.make()
        s=MultiTaskSession(old2,new2,DICT,**fixture.OPTIONS)
        r2=completed(s.agent)
        self.assertEqual(r2.selected,r1.selected)
        self.assertEqual((r2.observed_old,r2.observed_new),(r1.observed_old,r1.observed_new))

    def test_two_independent_requirements_generate_distinct_collision_certificates(self):
        old,new=self.make()
        edges=(((0,0,0),'B'),((1,2,0),'B'))
        agent=MultiRequiredEdgePortfolio(old,new,GOALS,required_edges=edges,**fixture.OPTIONS)
        r=completed(agent)
        self.assertEqual((agent.before_filter,len(agent.selections)),(11,7))
        self.assertEqual(len(agent.exclusions),4)
        self.assertEqual({edge for words,edge,cert in agent.exclusions},set(edges))
        self.assertEqual(r.status,'PARTIAL_GOALS_WITNESSED')
        for words,edge,cert in agent.exclusions:
            from ab_chatbot_evidence_prefilter import inspect_required_edge
            selection=agent._excluded_selections[words]
            self.assertEqual(inspect_required_edge(old,new,selection,edge).certificate,cert)

    def test_identical_laws_admit_multiple_edges_and_close_component(self):
        helper=fixture.path_fixture.PathUnionTests()
        self.addCleanup(helper.doCleanups)
        _,old,new,_,_=helper.make((0,0,1),(0,0,1),depth=0,budget=54)
        agent=MultiRequiredEdgePortfolio(old,new,GOALS,required_edges=BOTH,**fixture.OPTIONS)
        r=completed(agent)
        self.assertEqual(r.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((r.selected.paired_states,r.selected.admitted_edges),(27,54))
        self.assertEqual(len(r.selected.carried),2)

    def test_invalid_requirement_edge_types_do_not_crash(self):
        old,new=self.make()
        for edges in ((([0,0,0],'B'),((0,1,0),'A')),
                      (((0,0,0),'C'),((0,1,0),'A')),
                      (((0,0,0),'B'),((0,0,0),'B'))):
            with self.subTest(edges=edges):
                with self.assertRaises(ValueError):
                    MultiRequiredEdgePortfolio(old,new,GOALS,required_edges=edges)

if __name__=='__main__':unittest.main()
