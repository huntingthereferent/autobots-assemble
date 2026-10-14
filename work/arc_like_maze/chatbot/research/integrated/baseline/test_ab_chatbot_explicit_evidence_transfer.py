"""Transfer is opt-in, rooted, edge-selective and requires live evidence on both sides."""
import unittest
from copy import deepcopy
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import current_digest,BoundJointTask
from ab_chatbot_explicit_evidence_transfer import ExplicitEvidenceTransfer,TransferredEvidenceTask
from test_ab_chatbot_cross_pin_join import JoinCrossPinTests

ONE=((1,0,0),'B')
SECOND=((1,2,0),'B')

class ExplicitTransferTests(unittest.TestCase):
    def fixture(self,recipient_words=('A','BAA'),donor_words=('B','ABB')):
        owner_fixture=JoinCrossPinTests()
        a,old,new,owner,reg,p,q=owner_fixture.join(recipient_words)
        b=CrossPinJoin(old,new,{'required_owner_pins':{'old':p.token,'new':q.token},
                   'join_words':list(donor_words)},registry=reg)
        for joint in (a,b):
            for _ in range(45):
                result=joint.advance(max_new_edges=3)
                if result.status!='SEARCHING':break
            self.assertEqual(result.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        return a,b,old,new,owner,reg,p,q

    def transfer(self,a,b,keys=(ONE,)):
        declaration={'recipient_fingerprint':current_digest(a),
          'donor_fingerprint':current_digest(b),
          'transfer_edges':[{'state':list(s),'action':action} for s,action in keys]}
        return ExplicitEvidenceTransfer(a,b,declaration)

    def test_one_edge_transfer_is_rooted_and_read_free(self):
        a,b,old,new,*_=self.fixture()
        before=(len(old.snapshot.edges),len(new.snapshot.edges))
        r=self.transfer(a,b).advance()
        self.assertEqual(r.status,'TRANSFER_PARTIAL_CORRESPONDENCE_WITNESSED')
        self.assertEqual((len(r.state_pairs),len(r.admitted_edges)),(6,5))
        self.assertIn((ONE[0],ONE[1],('donor',)),r.provenance)
        self.assertEqual(before,(len(old.snapshot.edges),len(new.snapshot.edges)))
        self.assertEqual(len(r.derived_digest),64)

    def test_task_requires_two_edges_from_distinct_histories(self):
        a,b,*_=self.fixture()
        req={'required_edges':[{'state':[1,1,0],'action':'A'},
                               {'state':[1,0,0],'action':'B'}]}
        baseline=[BoundJointTask(j,{'witness_fingerprint':current_digest(j),**req}).advance()
                  for j in (a,b)]
        self.assertTrue(all(r.status=='TASK_REQUIREMENTS_UNPROVED' for r in baseline))
        transfer=self.transfer(a,b); evidence=transfer.advance()
        task=TransferredEvidenceTask(transfer,{'transfer_fingerprint':evidence.derived_digest,**req})
        result=task.advance()
        self.assertEqual(result.status,'TASK_COMPLETED_ON_TRANSFER_WITNESS')
        self.assertEqual([x[2] for x in result.obligations],[True,True])

    def test_conflicting_second_edge_is_rejected_atomically(self):
        a,b,*_=self.fixture()
        result=self.transfer(a,b,(ONE,SECOND)).advance()
        self.assertEqual(result.status,'TRANSFER_STATE_CONFLICT')
        self.assertEqual((result.state_pairs,result.admitted_edges,result.derived_digest),((),(),None))
        c=result.obstruction
        self.assertEqual((c.cause,c.retained_word,c.donor_word),
                         ('SOURCE_STATE_CONFLICT','BA','ABB'))
        self.assertEqual((c.old_equal,c.new_equal),(True,False))

    def test_unrooted_transfer_cannot_invent_missing_prefix(self):
        a,b,*_=self.fixture()
        result=self.transfer(a,b,(SECOND,)).advance()
        self.assertEqual(result.status,'TRANSFER_UNROOTED')
        self.assertFalse(result.admitted_edges)

    def test_edge_not_in_donor_is_unproved(self):
        a,b,*_=self.fixture()
        result=self.transfer(a,b,(((1,1,0),'B'),)).advance()
        self.assertEqual(result.status,'TRANSFER_EDGE_UNPROVED')

    def test_wrong_witness_fingerprint_rejected(self):
        a,b,*_=self.fixture()
        t=self.transfer(a,b)
        t.expected=('0'*64,t.expected[1])
        self.assertEqual(t.advance().status,'WITNESS_FINGERPRINT_MISMATCH')
        correct=self.transfer(a,b)
        report=correct.advance()
        task=TransferredEvidenceTask(correct,{'transfer_fingerprint':'0'*64,
                                 'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(task.advance().status,'TRANSFER_FINGERPRINT_MISMATCH')
        self.assertNotEqual(report.derived_digest,'0'*64)

    def test_source_revocation_withdraws_success(self):
        a,b,old,new,owner,reg,p,q=self.fixture()
        t=self.transfer(a,b);r=t.advance()
        done=TransferredEvidenceTask(t,{'transfer_fingerprint':r.derived_digest,
                   'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(done.advance().status,'TASK_COMPLETED_ON_TRANSFER_WITNESS')
        reg.revoke(q.token)
        self.assertEqual(done.advance().status,'OWNER_PIN_UNPROVED')

    def test_version_and_observation_forgery_withdrawn(self):
        a,b,old,new,*_=self.fixture()
        t=self.transfer(a,b)
        self.assertEqual(t.advance().status,'TRANSFER_PARTIAL_CORRESPONDENCE_WITNESSED')
        new.snapshot.revision+=1
        self.assertEqual(t.advance().status,'UNKNOWN_VERSION')
        c,d,old2,new2,*_=self.fixture()
        u=self.transfer(c,d)
        self.assertEqual(u.advance().status,'TRANSFER_PARTIAL_CORRESPONDENCE_WITNESSED')
        old2.snapshot.edges[next(iter(old2.snapshot.edges))]=(2,2,2)
        self.assertEqual(u.advance().status,'WALL_OBSERVATION')

    def test_different_registry_or_source_objects_not_implicitly_equivalent(self):
        a,b,*_=self.fixture()
        c,d,*_=self.fixture()
        transfer=ExplicitEvidenceTransfer(a,d,{
           'recipient_fingerprint':current_digest(a),'donor_fingerprint':current_digest(d),
           'transfer_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(transfer.advance().status,'TRANSFER_SOURCE_SCOPE_UNPROVED')

    def test_malformed_inputs_do_not_create_observations(self):
        a,b,old,new,*_=self.fixture()
        before=(len(old.snapshot.edges),len(new.snapshot.edges))
        for keys in ([],[{'state':[1,0,0],'action':'C'}],
                     [{'state':[1,0,0],'action':'B'}]*2):
            req={'recipient_fingerprint':current_digest(a),'donor_fingerprint':current_digest(b),
                 'transfer_edges':keys}
            self.assertEqual(ExplicitEvidenceTransfer(a,b,req).advance().status,'INVALID_TRANSFER')
        self.assertEqual(before,(len(old.snapshot.edges),len(new.snapshot.edges)))

    def test_transfer_task_rejects_unknown_keys_and_forged_digest(self):
        a,b,*_=self.fixture()
        t=self.transfer(a,b);r=t.advance()
        for payload in (
            {'transfer_fingerprint':r.derived_digest,'required_edges':[{'state':[1,0,0],'action':'B'}], 'unknown':1},
            {'transfer_fingerprint':'G'*64,'required_edges':[{'state':[1,0,0],'action':'B'}]}):
            self.assertEqual(TransferredEvidenceTask(t,payload).advance().status,'INVALID_TASK')

    def test_old_joints_are_not_mutated_by_transfer(self):
        a,b,*_=self.fixture()
        ra,rb=a.advance(max_new_edges=0),b.advance(max_new_edges=0)
        self.transfer(a,b).advance()
        self.assertEqual(ra,a.advance(max_new_edges=0))
        self.assertEqual(rb,b.advance(max_new_edges=0))

    def test_path_requirement_must_use_derived_admitted_steps(self):
        a,b,*_=self.fixture()
        t=self.transfer(a,b);r=t.advance()
        full=TransferredEvidenceTask(t,{'transfer_fingerprint':r.derived_digest,
            'required_paths':[{'word':'AB','old_end':[1,2,0],'new_end':[1,2,0]}]})
        self.assertEqual(full.advance().status,'TASK_COMPLETED_ON_TRANSFER_WITNESS')
        unobserved=TransferredEvidenceTask(t,{'transfer_fingerprint':r.derived_digest,
            'required_paths':[{'word':'ABB','old_end':[1,1,0],'new_end':[1,1,2]}]})
        self.assertEqual(unobserved.advance().status,'TASK_REQUIREMENTS_UNPROVED')

if __name__=='__main__':unittest.main()
