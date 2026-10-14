"""CP-29 owner-backed handoff: distinct invocations, negative controls."""
import json
import unittest

from ab_chatbot_certificate_handoff import (issue_handoff,accept_handoff,_digest)
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
from test_ab_chatbot_multi_task_dependency import MultiRouteTaskDependencyTests


class HandoffOwnerTests(unittest.TestCase):
    def fixture(self):
        x=RouteBoundTaskTests('runTest')
        refresh,_,left,right,_,registry,_,right_pin=x.fixture()
        make=lambda side,state,action:x.task(refresh,side,required_edges=[
            {'state':list(state),'action':action}])
        a=make('left',(1,0,0),'B')
        b=make('left',(1,1,2),'A')
        unproved=make('left',(0,1,2),'B')
        other=make('right',(0,1,2),'B')
        return (a,b,unproved,other,left,right,registry,right_pin,refresh,make)

    def test_issue_then_new_call_replays_twice(self):
        a,b,_,_,left,right,_,_,_,_=self.fixture()
        token=issue_handoff(a)
        self.assertEqual(token.status,'HANDOFF_REFERENCE_ISSUED')
        spy=MultiRouteTaskDependencyTests.spy(self,left,right)
        result=accept_handoff(token.receipt,{'a':a,'b':b})
        self.assertEqual(spy,{'left':2,'right':0})
        self.assertEqual(result.replay_calls,2)
        self.assertTrue(result.proof_for_use)
        self.assertEqual(result.usable,('a','b'))
        self.assertEqual(len(set((a.task_fingerprint,b.task_fingerprint))),2)

    def test_receipt_is_json_roundtrip_without_task_constraints(self):
        a,_,_,_,_,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        data=json.loads(receipt)
        self.assertEqual(data['kind'],'selected-route-handoff/v1')
        self.assertNotIn('task_fingerprint',data)
        self.assertNotIn('required_edges',data)
        self.assertEqual(json.dumps(data,sort_keys=True,separators=(',',':')),receipt)

    def test_second_receive_is_another_fresh_replay(self):
        a,b,_,_,left,right,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        spy=MultiRouteTaskDependencyTests.spy(self,left,right)
        for i in range(2):
            self.assertTrue(accept_handoff(receipt,{'new':b}).proof_for_use)
        self.assertEqual(spy,{'left':4,'right':0})

    def test_new_task_consumer_not_exporters_old_obligations(self):
        a,b,_,_,_,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        result=accept_handoff(receipt,{'different':b})
        self.assertEqual(result.task_status,(('different','TASK_COMPLETED_ON_SELECTED_ROUTE'),))
        self.assertTrue(result.proof_for_use)

    def test_unproved_obligation_independent(self):
        a,b,unproved,_,_,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        result=accept_handoff(receipt,{'a':a,'unproved':unproved,'b':b})
        self.assertEqual(result.usable,('a','b'))
        self.assertEqual(dict(result.task_status)['unproved'],'ROUTE_TASK_REQUIREMENTS_UNPROVED')

    def test_neighbor_route_is_not_borrowed(self):
        a,_,_,other,left,right,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        spy=MultiRouteTaskDependencyTests.spy(self,left,right)
        result=accept_handoff(receipt,{'left':a,'right':other})
        self.assertEqual(result.status,'HANDOFF_ROUTE_MISMATCH')
        self.assertEqual(result.replay_calls,0)
        self.assertEqual(spy,{'left':0,'right':0})

    def test_source_pin_revocation_withholds(self):
        a,_,_,_,left,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        middle=left.first.recipient
        middle.registry.revoke(middle._base._tokens[0])
        result=accept_handoff(receipt,{'a':a})
        self.assertEqual(result.status,'HANDOFF_REAUDIT_UNPROVED')
        self.assertFalse(result.proof_for_use)

    def test_neighbor_revoked_left_handoff_still_current(self):
        a,_,_,_,_,_,registry,right_pin,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        registry.revoke(right_pin.token)
        self.assertTrue(accept_handoff(receipt,{'a':a}).proof_for_use)

    def test_changed_pin_or_source_digest_is_rejected(self):
        a,_,_,_,left,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        left.final.old.snapshot.revision+=1
        result=accept_handoff(receipt,{'a':a})
        self.assertIn(result.status,('HANDOFF_REAUDIT_UNPROVED','HANDOFF_EVIDENCE_CHANGED'))
        self.assertFalse(result.proof_for_use)

    def test_corrupt_receipt_fails_before_route_replay(self):
        a,_,_,_,left,right,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        spy=MultiRouteTaskDependencyTests.spy(self,left,right)
        result=accept_handoff(receipt.replace('left','liFt'),{'a':a})
        self.assertEqual(result.status,'HANDOFF_INVALID_RECEIPT')
        self.assertEqual(spy,{'left':0,'right':0})

    def test_rehashed_forged_witness_cannot_pass_new_replay(self):
        a,_,_,_,_,_,_,_,_,_=self.fixture()
        data=json.loads(issue_handoff(a).receipt)
        data['witness_sha256']='0'*64
        data['receipt_sha256']=_digest({k:v for k,v in data.items() if k!='receipt_sha256'})
        result=accept_handoff(json.dumps(data),{'a':a})
        self.assertEqual(result.status,'HANDOFF_EVIDENCE_CHANGED')
        self.assertFalse(result.proof_for_use)

    def test_task_mutation_fails_closed_even_when_receipt_valid(self):
        a,b,_,_,left,right,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        b.task.edges=(((0,1,2),'B'),)
        spy=MultiRouteTaskDependencyTests.spy(self,left,right)
        result=accept_handoff(receipt,{'a':a,'b':b})
        self.assertEqual(result.status,'TASK_DECLARATION_CHANGED')
        self.assertEqual(spy,{'left':0,'right':0})

    def test_source_moving_during_receiver_replay_rejected(self):
        a,b,_,_,left,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        original=left.advance;calls=[0]
        def moving():
            r=original();calls[0]+=1
            if calls[0]==1:left.first.recipient.old.snapshot.revision+=1
            return r
        left.advance=moving
        result=accept_handoff(receipt,{'a':a,'b':b})
        self.assertEqual(result.status,'SOURCE_MOVED_DURING_HANDOFF')
        self.assertFalse(result.proof_for_use)

    def test_different_inprocess_route_fails(self):
        a,_,_,_,left,right,_,_,refresh,make=self.fixture()
        receipt=issue_handoff(a).receipt
        b=make('right',(0,1,2),'B')
        self.assertEqual(accept_handoff(receipt,{'other':b}).status,'HANDOFF_ROUTE_MISMATCH')

    def test_source_observations_not_added(self):
        a,_,_,_,left,_,_,_,_,_=self.fixture()
        scopes=(left.first.donor,left.first.recipient,left.final)
        counts=lambda:tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in scopes)
        before=counts();receipt=issue_handoff(a).receipt
        result=accept_handoff(receipt,{'a':a})
        self.assertTrue(result.proof_for_use)
        self.assertEqual(before,counts())

    def test_invalid_receipts_and_task_sets(self):
        a,_,_,_,_,_,_,_,_,_=self.fixture()
        receipt=issue_handoff(a).receipt
        for bad in ('', '{}', '{not json}', 42, None):
            self.assertEqual(accept_handoff(bad,{'a':a}).status,'HANDOFF_INVALID_RECEIPT')
        self.assertEqual(accept_handoff(receipt,{}).status,'HANDOFF_INVALID_TASK_SET')
        self.assertEqual(accept_handoff(receipt,{'a':a,'alias':a}).status,'HANDOFF_INVALID_TASK_SET')

if __name__=='__main__':unittest.main()
