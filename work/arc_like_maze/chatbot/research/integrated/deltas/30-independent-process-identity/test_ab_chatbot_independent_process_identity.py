"""CP-30 owner-backed independent subprocess verification; negative controls."""
import copy
import os
import unittest
from dataclasses import replace

from ab_chatbot_independent_process_identity import (
    new_challenge,issue_owner_attestations,receive_owner_attestations)
from finite_process_attestation import generate_fixture_keys
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
from test_ab_chatbot_multi_task_dependency import MultiRouteTaskDependencyTests


class IndependentProcessIdentityTests(unittest.TestCase):
    def setUp(self):
        fixture=RouteBoundTaskTests('runTest')
        refresh,_,self.left,self.right,_,self.registry,_,self.right_pin=fixture.fixture()
        def task(side,state,act):
            return fixture.task(refresh,side,required_edges=[{'state':list(state),'action':act}])
        self.a=task('left',(1,0,0),'B')
        self.b=task('left',(1,1,2),'A')
        self.missing=task('left',(0,1,2),'B')
        self.right_task=task('right',(0,1,2),'B')
        self.secret,self.trust=generate_fixture_keys()
        self.nonce=new_challenge()

    def issued(self):
        r=issue_owner_attestations(self.a,self.secret,self.nonce)
        self.assertEqual(r.status,'ATTESTATIONS_ISSUED')
        return r

    def recv(self,issued=None,tasks=None,trust=None,challenge=None):
        return receive_owner_attestations(
            self.issued() if issued is None else issued,
            {'a':self.a,'b':self.b} if tasks is None else tasks,
            self.trust if trust is None else trust,
            self.nonce if challenge is None else challenge)

    def test_success_two_tasks_one_fresh_route_audit(self):
        signed=self.issued()
        watch=MultiRouteTaskDependencyTests.spy(self,self.left,self.right)
        result=self.recv(signed)
        self.assertTrue(result.proof_for_use)
        self.assertEqual(result.usable,('a','b'))
        self.assertEqual(result.replay_calls,2)
        self.assertEqual(watch,{'left':2,'right':0})
        self.assertNotEqual(signed.signer_pid,result.verifier_pid)
        self.assertNotIn(os.getpid(),(signed.signer_pid,result.verifier_pid))

    def test_missing_edge_stays_unproved(self):
        r=self.recv(tasks={'a':self.a,'missing':self.missing})
        self.assertEqual(r.status,'INDEPENDENT_PROCESS_FRESHLY_VERIFIED')
        self.assertEqual(r.usable,('a',))
        self.assertEqual(dict(r.tasks)['missing'],'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        self.assertFalse(r.proof_for_use)

    def test_new_receive_requires_new_audit(self):
        signed=self.issued()
        watch=MultiRouteTaskDependencyTests.spy(self,self.left,self.right)
        for _ in range(2):
            self.assertTrue(self.recv(signed).proof_for_use)
        self.assertEqual(watch,{'left':4,'right':0})

    def test_revoked_source_withholds(self):
        signed=self.issued()
        middle=self.left.first.recipient
        middle.registry.revoke(middle._base._tokens[0])
        r=self.recv(signed)
        self.assertFalse(r.proof_for_use)
        self.assertIn(r.status,('ATTESTATION_CLAIM_MISMATCH','INDEPENDENT_PROCESS_REAUDIT_UNPROVED'))

    def test_source_revision_changed(self):
        signed=self.issued()
        self.left.final.old.snapshot.revision+=1
        self.assertFalse(self.recv(signed).proof_for_use)

    def test_attestation_signature_corrupt(self):
        signed=self.issued();wire=copy.deepcopy(signed.bundle)
        wire['attestations'][0]['signature']='AA=='
        r=self.recv(replace(signed,bundle=wire))
        self.assertEqual(r.status,'ATTESTATION_SIGNATURE_UNPROVED')
        self.assertEqual(r.replay_calls,0)

    def test_untrusted_pinning_key(self):
        signed=self.issued();_,other=generate_fixture_keys()
        trust=dict(self.trust);trust['donor']=other['donor']
        self.assertEqual(self.recv(signed,trust=trust).status,'ATTESTATION_SIGNATURE_UNPROVED')

    def test_wrong_nonce_no_use(self):
        signed=self.issued()
        self.assertEqual(self.recv(signed,challenge='ce'*24).status,'INDEPENDENT_PROCESS_INVALID_REQUEST')

    def test_different_receiving_route(self):
        signed=self.issued()
        self.assertEqual(self.recv(signed,tasks={'right':self.right_task}).status,
                         'INDEPENDENT_PROCESS_ROUTE_MISMATCH')

    def test_mixed_routes_rejected(self):
        signed=self.issued()
        self.assertEqual(self.recv(signed,tasks={'a':self.a,'right':self.right_task}).status,
                         'INDEPENDENT_PROCESS_ROUTE_MISMATCH')

    def test_sender_public_signature_mismatch_source(self):
        signed=self.issued();wire=copy.deepcopy(signed.bundle)
        wire['attestations'][1]['claim']['source_sha256']='00'*32
        self.assertEqual(self.recv(replace(signed,bundle=wire)).status,'ATTESTATION_CLAIM_MISMATCH')

    def test_task_mutation_rejected_before_subprocess(self):
        signed=self.issued()
        self.b.task.edges=(((0,1,2),'B'),)
        r=self.recv(signed)
        self.assertEqual(r.status,'INDEPENDENT_PROCESS_INVALID_REQUEST')
        self.assertIsNone(r.verifier_pid)

    def test_neighbor_pin_revoked_does_not_poison_left(self):
        signed=self.issued()
        self.registry.revoke(self.right_pin.token)
        self.assertTrue(self.recv(signed).proof_for_use)

    def test_route_moves_during_fresh_replay(self):
        signed=self.issued();original=self.left.advance;count=[0]
        def move():
            v=original();count[0]+=1
            if count[0]==1:
                self.left.final.old.snapshot.revision+=1
            return v
        self.left.advance=move
        r=self.recv(signed)
        self.assertEqual(r.status,'INDEPENDENT_PROCESS_SOURCE_MOVED')
        self.assertFalse(r.proof_for_use)

    def test_no_new_owner_edge_observations(self):
        scopes=(self.left.first.donor,self.left.first.recipient,self.left.final)
        counts=lambda:tuple((len(s.old.snapshot.edges),len(s.new.snapshot.edges)) for s in scopes)
        before=counts();r=self.recv()
        self.assertTrue(r.proof_for_use)
        self.assertEqual(before,counts())

    def test_no_keys_inside_receipt_or_bundle(self):
        issued=self.issued()
        blob=str(issued.receipt)+str(issued.bundle)
        self.assertTrue(all(v not in blob for v in self.secret.values()))

if __name__=='__main__':unittest.main()
