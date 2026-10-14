"""Task consumption controls: no extra observations, no claim from missing edges."""
import unittest
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_evidence_task import JointEvidenceTask
import test_ab_chatbot_cross_pin_join as join_fixture
import test_ab_chatbot_cross_pin_comparison as compare_fixture

class JointEvidenceTaskTests(unittest.TestCase):
    make = compare_fixture.CrossPinTests.make
    join = join_fixture.JoinCrossPinTests.join
    def fixture(self, words=('A','BAA'), oldlaw=(0,0,0), newlaw=(0,1,2)):
        joint,old,new,owner,registry,p,q = self.join(words,oldlaw=oldlaw,newlaw=newlaw)
        self.addCleanup(lambda: None)
        return joint,old,new,owner,registry,p,q

    def settle(self,joint):
        for _ in range(30):
            result=joint.advance(max_new_edges=2)
            if result.status!='SEARCHING':return result
        self.fail('join failed to settle')

    def contract(self):
        return {'goals':[[1,0,0],[2,1,0]],
                'required_edges':[{'state':[0,0,0],'action':'A'}, {'state':[1,1,0],'action':'A'}],
                'required_paths':[{'word':'BAA','old_end':[2,1,0],'new_end':[2,1,0]}],
                'required_destinations':[{'source':[1,0,0],'image':[1,0,0]}]}

    def test_consumes_joined_witness_no_new_transitions(self):
        joint,old,new,*_=self.fixture()
        self.assertEqual(self.settle(joint).status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        sizes=(len(old.snapshot.edges),len(new.snapshot.edges))
        task=JointEvidenceTask(joint,self.contract())
        r=task.advance()
        self.assertEqual(r.status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        self.assertEqual(len(r.obligations),6)
        self.assertTrue(all(c.admitted for c in r.obligations))
        self.assertEqual(len(r.joint.state_pairs),5)
        self.assertEqual(len(r.joint.admitted_edges),4)
        self.assertEqual(sizes,(len(old.snapshot.edges),len(new.snapshot.edges)))

    def test_declared_edge_outside_join_unproved_no_fetch(self):
        joint,old,new,*_=self.fixture()
        self.settle(joint)
        sizes=(len(old.snapshot.edges),len(new.snapshot.edges))
        r=JointEvidenceTask(joint,{'required_edges':[{'state':[1,0,0],'action':'B'}]}).advance()
        self.assertEqual(r.status,'TASK_REQUIREMENTS_UNPROVED')
        self.assertFalse(r.obligations[0].admitted)
        self.assertEqual(sizes,(len(old.snapshot.edges),len(new.snapshot.edges)))

    def test_goal_may_be_mapped_but_missing_required_path(self):
        joint,old,new,*_=self.fixture()
        self.settle(joint)
        r=JointEvidenceTask(joint,{'goals':[[1,0,0]],
            'required_paths':[{'word':'AB','old_end':[1,1,0],'new_end':[1,1,0]}]}).advance()
        self.assertEqual(r.status,'TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual([c.admitted for c in r.obligations],[True,False])
        self.assertEqual([c.kind for c in r.obligations],['GOAL','PATH'])

    def test_wrong_destination_is_not_overridden_by_goal(self):
        joint,old,new,*_=self.fixture();self.settle(joint)
        r=JointEvidenceTask(joint,{'goals':[[1,0,0]],
            'required_destinations':[{'source':[1,0,0],'image':[1,0,1]}]}).advance()
        self.assertEqual(r.status,'TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual([c.admitted for c in r.obligations],[True,False])

    def test_joins_with_collisions_do_not_satisfy_tasks(self):
        joint,old,new,*_=self.fixture(('A','BAB'))
        self.assertEqual(self.settle(joint).status,'JOINT_RELATION_CONFLICT_WITNESSED')
        r=JointEvidenceTask(joint,self.contract()).advance()
        self.assertEqual(r.status,'JOINT_RELATION_CONFLICT_WITNESSED')
        self.assertEqual(r.obligations,())
        self.assertIsNotNone(r.joint.obstruction)

    def test_not_yet_observed_join_remains_searching_zero_budget(self):
        joint,old,new,*_=self.fixture()
        r=JointEvidenceTask(joint,self.contract()).advance()
        self.assertEqual(r.status,'SEARCHING')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_tamper_after_completion_revokes_task_success(self):
        joint,old,new,*_=self.fixture()
        self.settle(joint)
        task=JointEvidenceTask(joint,self.contract())
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        edge=next(iter(old.snapshot.edges))
        old.snapshot.edges[edge]=(2,2,2)
        r=task.advance()
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertEqual(r.obligations,())

    def test_pin_withdrawal_revokes_task_success(self):
        joint,old,new,owner,registry,p,q=self.fixture()
        self.settle(joint)
        task=JointEvidenceTask(joint,self.contract())
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        registry.revoke(q.token)
        self.assertEqual(task.advance().status,'OWNER_PIN_UNPROVED')

    def test_revision_changed_revokes_success(self):
        joint,old,new,*_=self.fixture()
        self.settle(joint)
        task=JointEvidenceTask(joint,self.contract())
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        new.snapshot.revision+=1
        self.assertEqual(task.advance().status,'UNKNOWN_VERSION')

    def test_task_validation_no_fetch_and_self_conflict(self):
        joint,old,new,*_=self.fixture()
        bad=[{}, {'unknown':3},{'goals':[[3,0,0]]},
             {'required_paths':[{'word':'C','old_end':[0,0,0],'new_end':[0,0,0]}]},
             {'goals':[[1,0,0],[1,0,0]]},
             {'required_edges':[{'state':[0,0,0],'action':'C'}]}]
        for req in bad:
            self.assertEqual(JointEvidenceTask(joint,req).advance().status,'INVALID_TASK')
        conflict={'required_destinations':[{'source':[1,0,0],'image':[0,0,1]},
                                           {'source':[1,0,0],'image':[0,0,2]}]}
        self.assertEqual(JointEvidenceTask(joint,conflict).advance().status,'INCONSISTENT_TASK')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_full_joint_evidence_unchanged_after_multiple_tasks(self):
        joint,old,new,*_=self.fixture();before=self.settle(joint)
        one=JointEvidenceTask(joint,{'required_edges':[{'state':[0,0,0],'action':'A'}]})
        two=JointEvidenceTask(joint,{'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(one.advance().status,'TASK_COMPLETED_ON_JOINT_WITNESS')
        self.assertEqual(two.advance().status,'TASK_REQUIREMENTS_UNPROVED')
        after=joint.advance(max_new_edges=0)
        self.assertEqual((before.state_pairs,before.admitted_edges),
                         (after.state_pairs,after.admitted_edges))
        self.assertNotEqual(one.fingerprint,two.fingerprint)

if __name__ == '__main__': unittest.main()
