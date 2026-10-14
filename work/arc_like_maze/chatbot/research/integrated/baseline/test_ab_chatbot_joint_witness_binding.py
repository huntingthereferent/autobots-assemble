"""Exact witness-bound task and independent-join comparison controls."""
import unittest
from copy import deepcopy
from dataclasses import replace
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import (
    BoundJointTask,JointWitnessTaskComparison,canonical_digest,current_digest)
from test_ab_chatbot_cross_pin_join import JoinCrossPinTests

class ExactJointWitnessTests(unittest.TestCase):
    def fixture(self,words=('A','BAA')):
        fixture=JoinCrossPinTests()
        return fixture.join(words)
    def settle(self,joint):
        for _ in range(40):
            r=joint.advance(max_new_edges=3)
            if r.status!='SEARCHING':return r
        self.fail('not settled')
    def new_join(self,old,new,reg,p,q,words):
        return CrossPinJoin(old,new,{'required_owner_pins':{'old':p.token,'new':q.token},
                    'join_words':list(words)},registry=reg)
    def payload(self,joint,**task):
        return {'witness_fingerprint':current_digest(joint),**task}

    def test_exact_binding_completes_without_more_observations(self):
        joint,old,new,*_=self.fixture(); self.settle(joint)
        before=(len(old.snapshot.edges),len(new.snapshot.edges))
        task=BoundJointTask(joint,self.payload(joint,goals=[[1,0,0],[2,1,0]],
            required_edges=[{'state':[0,0,0],'action':'A'}],
            required_paths=[{'word':'BAA','old_end':[2,1,0],'new_end':[2,1,0]}]))
        result=task.advance()
        self.assertEqual(result.status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),before)
        self.assertEqual(result.observed_digest,result.expected_digest)

    def test_other_join_is_not_substitutable_even_if_same_finite_laws(self):
        joint,old,new,owner,registry,p,q=self.fixture();self.settle(joint)
        alternate=self.new_join(old,new,registry,p,q,('B','ABB'))
        self.settle(alternate)
        self.assertNotEqual(current_digest(joint),current_digest(alternate))
        task=BoundJointTask(alternate,{'witness_fingerprint':current_digest(joint),
                          'required_edges':[{'state':[0,0,0],'action':'A'}]})
        self.assertEqual(task.advance().status,'WITNESS_FINGERPRINT_MISMATCH')
        self.assertIsNone(task.advance().task_report)

    def test_digest_canonical_to_witness_not_cache_read_count(self):
        joint,old,new,*_=self.fixture();r=self.settle(joint)
        altered=replace(r,old_observed=r.old_observed+100,
                        new_observed=r.new_observed+200,details='different display')
        self.assertEqual(canonical_digest(r),canonical_digest(altered))
        changed=replace(r,admitted_edges=r.admitted_edges[:-1])
        self.assertNotEqual(canonical_digest(r),canonical_digest(changed))
        changed=replace(r,state_pairs=r.state_pairs[:-1])
        self.assertNotEqual(canonical_digest(r),canonical_digest(changed))
        changed=replace(r,words=tuple(reversed(r.words)))
        self.assertNotEqual(canonical_digest(r),canonical_digest(changed))

    def test_task_declared_wrong_digest_fails_closed(self):
        joint,old,new,*_=self.fixture();self.settle(joint)
        for bad in ('wrong','A'*64,None,18):
            request={'witness_fingerprint':bad,'goals':[[1,0,0]]}
            self.assertEqual(BoundJointTask(joint,request).advance().status,'INVALID_TASK')
        self.assertEqual(BoundJointTask(joint,{'witness_fingerprint':'0'*64,
                    'goals':[[1,0,0]]}).advance().status,'WITNESS_FINGERPRINT_MISMATCH')

    def test_unready_join_not_bound_to_speculative_digest(self):
        joint,old,new,*_=self.fixture()
        self.assertIsNone(current_digest(joint))
        bound=BoundJointTask(joint,{'witness_fingerprint':'0'*64,
                                    'goals':[[1,0,0]]})
        self.assertEqual(bound.advance().status,'SEARCHING')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_pin_revocation_downgrades_old_success(self):
        joint,old,new,owner,reg,p,q=self.fixture();self.settle(joint)
        task=BoundJointTask(joint,self.payload(joint,goals=[[1,0,0]]))
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        reg.revoke(q.token)
        result=task.advance()
        self.assertEqual(result.status,'OWNER_PIN_UNPROVED')
        self.assertIsNone(result.task_report)

    def test_changed_revision_rejects_stale_result(self):
        joint,old,new,*_=self.fixture();self.settle(joint)
        task=BoundJointTask(joint,self.payload(joint,goals=[[1,0,0]]))
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        new.snapshot.revision+=1
        self.assertEqual(task.advance().status,'UNKNOWN_VERSION')

    def test_cached_edge_forgery_revokes_status(self):
        joint,old,new,*_=self.fixture();self.settle(joint)
        task=BoundJointTask(joint,self.payload(joint,goals=[[1,0,0]]))
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        old.snapshot.edges[next(iter(old.snapshot.edges))]=(2,2,2)
        self.assertEqual(task.advance().status,'WALL_OBSERVATION')

    def test_comparison_does_not_merge_obligations_from_two_joins(self):
        j1,old,new,owner,reg,p,q=self.fixture();self.settle(j1)
        j2=self.new_join(old,new,reg,p,q,('B','ABB'));self.settle(j2)
        obligation={'required_edges':[{'state':[1,1,0],'action':'A'},
                                      {'state':[1,0,0],'action':'B'}]}
        a=BoundJointTask(j1,self.payload(j1,**obligation))
        b=BoundJointTask(j2,self.payload(j2,**obligation))
        result=JointWitnessTaskComparison((('left',a),('right',b))).advance()
        self.assertEqual(result.status,'TASK_UNPROVED_ACROSS_TESTED_WITNESSES')
        self.assertEqual([c.admitted_obligations for c in result.candidates],[1,1])
        self.assertEqual(result.completed_by,())
        self.assertTrue(all(c.total_obligations==2 for c in result.candidates))

    def test_comparison_can_select_successful_independent_join(self):
        j1,old,new,owner,reg,p,q=self.fixture();self.settle(j1)
        j2=self.new_join(old,new,reg,p,q,('B','ABB'));self.settle(j2)
        requirements={'required_edges':[{'state':[1,1,0],'action':'A'}]}
        a=BoundJointTask(j1,self.payload(j1,**requirements))
        b=BoundJointTask(j2,self.payload(j2,**requirements))
        before=(len(old.snapshot.edges),len(new.snapshot.edges))
        result=JointWitnessTaskComparison((('first',a),('second',b))).advance()
        self.assertEqual(result.status,'TASK_COMPLETED_BY_INDEPENDENT_WITNESS')
        self.assertEqual(result.completed_by,('first',))
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),before)

    def test_comparison_retains_conflict_or_unavailable(self):
        j1,old,new,owner,reg,p,q=self.fixture();self.settle(j1)
        collision=self.new_join(old,new,reg,p,q,('A','BAB'))
        self.assertEqual(self.settle(collision).status,'JOINT_RELATION_CONFLICT_WITNESSED')
        task={'required_edges':[{'state':[1,1,0],'action':'B'}]}
        one=BoundJointTask(j1,self.payload(j1,**task))
        two=BoundJointTask(collision,{'witness_fingerprint':'0'*64,**task})
        comparison=JointWitnessTaskComparison((('one',one),('collision',two)))
        r=comparison.advance()
        self.assertEqual(r.status,'COMPARISON_WITH_UNAVAILABLE_EVIDENCE')
        self.assertEqual(r.candidates[1].status,'JOINT_RELATION_CONFLICT_WITNESSED')
        self.assertIsNotNone(r.candidates[1].retained_obstruction)

    def test_competing_tasks_differ_invalid_without_observations(self):
        j1,old,new,owner,reg,p,q=self.fixture();self.settle(j1)
        j2=self.new_join(old,new,reg,p,q,('B','ABB'));self.settle(j2)
        a=BoundJointTask(j1,self.payload(j1,goals=[[1,0,0]]))
        b=BoundJointTask(j2,self.payload(j2,goals=[[0,1,0]]))
        self.assertEqual(JointWitnessTaskComparison((('a',a),('b',b))).advance().status,
                         'INVALID_COMPARISON')

if __name__=='__main__': unittest.main()
