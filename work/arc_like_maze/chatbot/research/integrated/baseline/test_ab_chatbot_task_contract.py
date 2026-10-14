"""Explicit task provenance/requirements and finite owner replay checks."""
import copy
import unittest

from ab_chatbot_task_contract import read_task, TaskContractSession
import test_ab_chatbot_evidence_prefilter as prefilter_fixture
from test_ab_chatbot_evidence_prefilter import GOALS, REQUIRED, OPTIONS, complete
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_evidence_prefilter import RequiredEdgePortfolio

GRAMMAR = 'goals: (0,1,1), (0,2,0); require: edge (0,0,0) B'
SCHEMA = {'goals': [[0,1,1], [0,2,0]],
          'required_edge': {'state': [0,0,0], 'action': 'B'}}


class ExplicitTaskTests(unittest.TestCase):
    def make(self, *, remote_new=False):
        helper = prefilter_fixture.EvidencePrefilterTests()
        self.addCleanup(helper.doCleanups)
        return helper.make(remote_new=remote_new)

    def test_grammar_schema_equivalent_but_provenance_distinct(self):
        a,b = read_task(GRAMMAR), read_task(SCHEMA)
        self.assertEqual((a.status,b.status), ('TASK_ACCEPTED','TASK_ACCEPTED'))
        self.assertEqual(a.contract.fingerprint, b.contract.fingerprint)
        self.assertEqual(a.contract.goals, GOALS)
        self.assertEqual(b.contract.required_edge, REQUIRED)
        self.assertEqual((a.contract.declared_by,b.contract.declared_by),
                         ('EXPLICIT_GRAMMAR','EXPLICIT_SCHEMA'))
        self.assertNotEqual(a.contract.original_input,b.contract.original_input)

    def test_goals_only_do_not_create_requirement(self):
        a=read_task('goals: (0,1,1), (0,2,0)')
        b=read_task({'goals': [[0,1,1],[0,2,0]]})
        self.assertEqual(a.contract.fingerprint,b.contract.fingerprint)
        self.assertIsNone(a.contract.required_edge)
        self.assertIsNone(b.contract.required_edge)

    def test_ambiguous_language_never_becomes_edge_requirement(self):
        for text in ('keep the B relation and find both goals',
                     'goals: (0,1,1), (0,2,0); preserve B',
                     'goals: (0,1,1); require: edge (0,0,0) C',
                     'goals: (0,1,1); require: edge (3,0,0) B',
                     'goals: (0,1,1); and also guess other constraints'):
            with self.subTest(text=text):
                result=read_task(text)
                self.assertEqual(result.status,'UNKNOWN_TASK')
                self.assertIsNone(result.contract)

    def test_invalid_unknown_and_multiple_fields_not_silently_ignored(self):
        inputs = [
            {'goals': [[0,1,1]], 'required_edges': [{'state':[0,0,0], 'action':'B'}]},
            {'goals': [[0,1,1]], 'constraint': 'keep B'},
            {'goals': [[0,1,1]], 'required_edge': None},
            {'goals': [[0,1,1]], 'required_edge': {'state':[0,0,0]}},
            {'goals': [[0,1,1]], 'required_edge': {'state':[0,0,0], 'action':'b'}},
            {'goals': [[0,1,True]]}, {'goals': [[0,1,1],[0,1,1]]},
            {'goals': [[0,1,3]]}, {}, None,
        ]
        for payload in inputs:
            with self.subTest(payload=payload):
                r=read_task(payload)
                self.assertIn(r.status, ('INVALID_TASK','UNSUPPORTED_TASK'))
                self.assertIsNone(r.contract)

    def test_session_unknown_language_requires_no_owner_observations(self):
        old,new=self.make()
        before=(len(old.snapshot.edges),len(new.snapshot.edges))
        session=TaskContractSession(old,new,'keep B and solve these')
        r=session.advance(max_new_edges=108)
        self.assertEqual(r.status,'UNKNOWN_TASK')
        self.assertIsNone(r.report)
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),before)

    def test_structured_task_snapshot_immutable_after_input_mutation(self):
        old,new=self.make()
        payload=copy.deepcopy(SCHEMA)
        session=TaskContractSession(old,new,payload,**OPTIONS)
        payload['goals'][0][1]=2
        payload['required_edge']['action']='A'
        self.assertEqual(session.intake.contract.goals, GOALS)
        self.assertEqual(session.intake.contract.required_edge,REQUIRED)
        self.assertIsInstance(session.agent,RequiredEdgePortfolio)

    def test_explicit_edge_changes_task_and_routes_into_existing_prefilter(self):
        old,new=self.make()
        session=TaskContractSession(old,new,GRAMMAR,**OPTIONS)
        self.assertIsInstance(session.agent,RequiredEdgePortfolio)
        result=complete(session.agent)
        via_task=session.advance(max_new_edges=0)
        self.assertEqual(via_task.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(via_task.contract.required_edge,REQUIRED)
        self.assertEqual(len(via_task.report.selected.carried),1)
        self.assertEqual((session.agent.before_filter,len(session.agent.selections)),(11,9))
        self.assertEqual((via_task.report.observed_old,via_task.report.observed_new),(26,18))

    def test_goal_only_does_not_shrink_task_or_prune(self):
        old,new=self.make()
        session=TaskContractSession(old,new,{'goals':SCHEMA['goals']},**OPTIONS)
        self.assertIsInstance(session.agent,PostExtensionPortfolio)
        self.assertNotIsInstance(session.agent,RequiredEdgePortfolio)
        report=complete(session.agent)
        self.assertEqual(report.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual(len(report.selected.carried),2)
        self.assertEqual(len(session.agent.finished),11)

    def test_captured_requirements_are_replayed_and_staleness_blocks(self):
        old,new=self.make()
        session=TaskContractSession(old,new,SCHEMA,**OPTIONS)
        complete(session.agent)
        old.snapshot.revision += 1
        report=session.advance(max_new_edges=0)
        self.assertEqual(report.status,'UNKNOWN_VERSION')
        self.assertIsNone(report.report.selected)

    def test_remote_task_stays_reported_not_locally_verified(self):
        old,new=self.make(remote_new=True)
        session=TaskContractSession(old,new,SCHEMA,**OPTIONS)
        result=session.advance(max_new_edges=108)
        self.assertIn(result.status,('EVALUATING','SEARCHING'))
        self.assertEqual(len(session.agent.certificates),0)

    def test_small_budget_retains_same_declared_task(self):
        old,new=self.make()
        session=TaskContractSession(old,new,SCHEMA,**OPTIONS)
        first=session.advance(max_new_edges=0)
        self.assertIn(first.status,('SEARCHING','EVALUATING'))
        self.assertEqual(first.contract.fingerprint,session.intake.contract.fingerprint)
        for _ in range(100):
            last=session.advance(max_new_edges=108)
            if last.status not in ('SEARCHING','EVALUATING'):break
        self.assertEqual(last.status,'PARTIAL_GOALS_WITNESSED')
        self.assertEqual(last.contract.fingerprint,first.contract.fingerprint)

if __name__=='__main__':unittest.main()
