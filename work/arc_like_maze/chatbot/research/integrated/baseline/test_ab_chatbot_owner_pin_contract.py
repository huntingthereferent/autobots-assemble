"""Exact local-owner identity and explicit re-pin, under the existing observer."""
import copy
import unittest
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_owner_pin_contract import OwnerPinRegistry, ExactOwnerTaskSession
from ab_chatbot_provenance_contract import LOCAL
from ab_chatbot_stability_witness import TransportedLaw
from test_ab_chatbot_mixed_obligations import TASK
import test_ab_chatbot_evidence_prefilter as fixture

class ExactOwnerTests(unittest.TestCase):
    def make(self, remote_new=False):
        f=fixture.EvidencePrefilterTests()
        self.addCleanup(f.doCleanups)
        return f.make(remote_new=remote_new)

    def session(self, old, new, registry, token, side='old'):
        return ExactOwnerTaskSession(old,new,{**TASK,'required_owner_pins':{side:token}},
                                     registry=registry,**fixture.OPTIONS)

    def complete(self, session):
        for _ in range(48):
            result=session.advance()
            if result.status not in ('SEARCHING','EVALUATING'):
                return result
        self.fail('incomplete bounded test')

    def test_issued_pin_completes_then_replays_without_new_observations(self):
        old,new=self.make();register=OwnerPinRegistry()
        a=register.issue(old);b=register.issue(new)
        self.assertNotEqual(a.token,b.token)
        session=ExactOwnerTaskSession(old,new,{**TASK,'required_owner_pins':{
                'old':a.token,'new':b.token}},registry=register,**fixture.OPTIONS)
        self.assertEqual(session.status,'TASK_ACCEPTED')
        result=self.complete(session)
        self.assertEqual(result.status,'GOALS_CARRIED_WITNESSED')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(28,18))
        self.assertEqual(session.advance(max_new_edges=0).status,'GOALS_CARRIED_WITNESSED')
        self.assertTrue(all(entry[2] for entry in result.pins))

    def test_equal_claimed_metadata_is_not_same_owner(self):
        old,new=self.make();register=OwnerPinRegistry()
        issued=register.issue(old)
        self.assertEqual(self.session(old,new,register,issued.token).status,'TASK_ACCEPTED')
        # A new observer over the SAME remote and owner is not the identical pin.
        other=LanguageBridge(old.remote,owner=old.owner,edge_budget=54)
        self.assertEqual(self.session(other,new,register,issued.token).advance().status,
                         'OWNER_PIN_UNPROVED')
        self.assertEqual((len(other.snapshot.edges),len(new.snapshot.edges)),(0,0))
        self.assertEqual(other.snapshot.digest,issued.digest)

    def test_substituted_owner_invalidates_permanently(self):
        old,new=self.make();register=OwnerPinRegistry();pin=register.issue(old)
        session=self.session(old,new,register,pin.token)
        owner=old.owner
        old.owner=copy.copy(owner)
        self.assertEqual(session.advance().status,'OWNER_PIN_UNPROVED')
        old.owner=owner
        self.assertEqual(session.advance().status,'OWNER_PIN_UNPROVED')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_changed_snapshot_and_revision_invalidates_old_pin(self):
        old,new=self.make();registry=OwnerPinRegistry();pin=registry.issue(old)
        session=self.session(old,new,registry,pin.token)
        old.snapshot.revision+=1
        self.assertEqual(session.advance().status,'OWNER_PIN_UNPROVED')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_explicit_repin_new_referent_new_session(self):
        old,new=self.make();registry=OwnerPinRegistry();prior=registry.issue(old)
        first=self.session(old,new,registry,prior.token)
        self.assertEqual(self.complete(first).status,'GOALS_CARRIED_WITNESSED')
        old.owner.replace(TransportedLaw((0,0,1),tuple((i,j,k)
                             for i in range(3) for j in range(3) for k in range(3))))
        # owner moved head; the observer must opt into the new source version.
        second_bridge=LanguageBridge(old.remote,owner=old.owner,edge_budget=54)
        self.assertEqual(second_bridge.snapshot.revision,prior.revision+1)
        second=registry.issue(second_bridge,predecessor=prior.token)
        self.assertNotEqual(prior.token,second.token)
        self.assertEqual(second.predecessor,prior.token)
        self.assertNotEqual(second.revision,prior.revision)
        blocked=self.session(second_bridge,new,registry,prior.token)
        self.assertEqual(blocked.advance().status,'OWNER_PIN_UNPROVED')
        renewed=self.session(second_bridge,new,registry,second.token)
        self.assertEqual(renewed.advance(max_new_edges=0).status,'SEARCHING')
        self.assertEqual(len(second_bridge.snapshot.edges),0)
        # Existing first task evidence remains rooted in first captured snapshot.
        self.assertEqual(len(old.snapshot.edges),28)

    def test_remote_owner_cannot_issue_pin(self):
        old,new=self.make(remote_new=True)
        reg=OwnerPinRegistry()
        with self.assertRaises(ValueError):reg.issue(new)
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_revocation_blocks_even_zero_read_success(self):
        old,new=self.make();registry=OwnerPinRegistry();pin=registry.issue(old)
        session=self.session(old,new,registry,pin.token)
        self.assertEqual(self.complete(session).status,'GOALS_CARRIED_WITNESSED')
        registry.revoke(pin.token)
        result=session.advance(max_new_edges=0)
        self.assertEqual(result.status,'OWNER_PIN_UNPROVED')
        self.assertIsNone(result.base_outcome)

    def test_unknown_or_invalid_or_ambiguous_pin_zero_observations(self):
        old,new=self.make();registry=OwnerPinRegistry()
        for request in ({'old':'a'*48},{'old':'not-a-token'},{},
                        {'third':'a'*48}):
            session=ExactOwnerTaskSession(old,new,{**TASK,
                         'required_owner_pins':request},registry=registry,**fixture.OPTIONS)
            self.assertIn(session.advance().status,('UNKNOWN_OWNER_PIN','INVALID_TASK'))
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_pin_scope_request_cannot_downgrade_local_constraint(self):
        old,new=self.make();registry=OwnerPinRegistry();pin=registry.issue(old)
        s=ExactOwnerTaskSession(old,new,{**TASK,
             'required_owner_pins':{'old':pin.token},
             'required_provenance':{'old':'REMOTE_ORIGIN_UNVERIFIED'}},
             registry=registry,**fixture.OPTIONS)
        self.assertEqual(s.advance().status,'INVALID_TASK')
        self.assertEqual(len(old.snapshot.edges),0)

    def test_predecessor_must_be_registry_issued(self):
        old,new=self.make();registry=OwnerPinRegistry()
        with self.assertRaises(ValueError):registry.issue(old,predecessor='a'*48)

if __name__=='__main__':unittest.main()
