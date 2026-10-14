"""Comparison must independently replay each pin, not copy old evidence."""
import unittest
from ab_chatbot_cross_pin_comparison import CrossPinComparison
from ab_chatbot_owner_pin_contract import OwnerPinRegistry
from ab_chatbot_http_snapshot import SourceOwnedHTTP,LoopbackHTTP,RemoteObserver
from ab_chatbot_language_bridge import LanguageBridge
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw

IDENT=tuple(DOMAIN)

class CrossPinTests(unittest.TestCase):
    def make(self,oldlaw=(0,0,0),newlaw=(0,1,2),budget=54,repin_owner=True):
        owner=SourceOwnedHTTP(TransportedLaw(oldlaw,IDENT))
        server=LoopbackHTTP(owner);server.__enter__()
        self.addCleanup(server.__exit__,None,None,None)
        def observer():
            return LanguageBridge(RemoteObserver(server.url,bound_loopback=server),owner=owner,edge_budget=budget)
        old=observer()
        if repin_owner:owner.replace(TransportedLaw(newlaw,IDENT))
        new=observer()
        reg=OwnerPinRegistry();p=reg.issue(old);q=reg.issue(new,predecessor=p.token)
        return old,new,owner,reg,p,q
    def task(self,p,q,pairs):
        return {'required_owner_pins':{'old':p.token,'new':q.token},'compare_words':[list(pair) for pair in pairs]}
    def compare(self,old,new,reg,p,q,pairs):
        return CrossPinComparison(old,new,self.task(p,q,pairs),registry=reg)
    def settle(self,agent,cap=108):
        for _ in range(20):
            r=agent.advance(max_new_edges=cap)
            if r.status!='SEARCHING':return r
        self.fail('bounded comparison not settled')

    def test_retained_historical_owner_comparison_change_and_preservation(self):
        old,new,owner,reg,p,q=self.make()
        agent=self.compare(old,new,reg,p,q,(('','AAA'),('BA','ABB')))
        result=self.settle(agent)
        self.assertEqual(result.status,'RELATION_CHANGED_WITNESSED')
        self.assertEqual([(c.old_equal,c.new_equal) for c in result.comparisons],[(True,True),(True,False)])
        self.assertEqual(result.old_version[1],0)
        self.assertEqual(result.new_version[1],1)
        self.assertEqual(q.predecessor,p.token)
        self.assertEqual(result.old_observed,len(old.snapshot.edges))
        self.assertEqual(result.new_observed,len(new.snapshot.edges))
        self.assertGreater(result.new_observed,0)
        self.assertIsNot(old.snapshot.edges,new.snapshot.edges)

    def test_preserved_word_equalities_do_not_claim_system_equivalence(self):
        old,new,_,reg,p,q=self.make(newlaw=(0,0,0))
        outcome=self.settle(self.compare(old,new,reg,p,q,(('','AAA'),)))
        self.assertEqual(outcome.status,'DECLARED_EQUALITY_PRESERVED_WITNESSED')
        self.assertEqual(len(outcome.comparisons),1)

    def test_old_evidence_reused_only_on_historical_side(self):
        old,new,_,reg,p,q=self.make()
        original=self.settle(self.compare(old,new,reg,p,q,(('','AAA'),)))
        self.assertEqual(original.status,'DECLARED_EQUALITY_PRESERVED_WITNESSED')
        old_count=len(old.snapshot.edges);new_count=len(new.snapshot.edges)
        self.assertGreater(old_count,0)
        fresh=LanguageBridge(old.remote,owner=old.owner,edge_budget=54)
        fresh_pin=reg.issue(fresh,predecessor=p.token)
        again=self.compare(fresh,new,reg,fresh_pin,q,(('','AAA'),))
        self.assertEqual(len(fresh.snapshot.edges),0)
        self.assertEqual(again.advance(max_new_edges=0).status,'SEARCHING')
        self.assertEqual(len(fresh.snapshot.edges),0)
        self.assertEqual(len(old.snapshot.edges),old_count)
        self.assertEqual(len(new.snapshot.edges),new_count)

    def test_zero_budget_is_resumable_not_claimed(self):
        old,new,_,reg,p,q=self.make()
        agent=self.compare(old,new,reg,p,q,(('BA','ABB'),))
        self.assertEqual(agent.advance(max_new_edges=0).status,'SEARCHING')
        for _ in range(30):
            before=len(old.snapshot.edges)+len(new.snapshot.edges)
            result=agent.advance(max_new_edges=1)
            after=len(old.snapshot.edges)+len(new.snapshot.edges)
            self.assertLessEqual(after-before,1)
            if result.status!='SEARCHING':break
        self.assertEqual(result.status,'RELATION_CHANGED_WITNESSED')

    def test_tampered_old_cached_edge_rejected_on_zero_read(self):
        old,new,_,reg,p,q=self.make()
        agent=self.compare(old,new,reg,p,q,(('BA','ABB'),))
        self.assertEqual(self.settle(agent).status,'RELATION_CHANGED_WITNESSED')
        edge=next(iter(old.snapshot.edges))
        old.snapshot.edges[edge]=(2,2,2)
        r=agent.advance(max_new_edges=0)
        self.assertEqual(r.status,'WALL_OBSERVATION')
        self.assertFalse(r.comparisons)

    def test_new_pin_revocation_revokes_former_completion(self):
        old,new,_,reg,p,q=self.make()
        agent=self.compare(old,new,reg,p,q,(('','AAA'),))
        self.assertEqual(self.settle(agent).status,'DECLARED_EQUALITY_PRESERVED_WITNESSED')
        reg.revoke(q.token)
        r=agent.advance(max_new_edges=0)
        self.assertEqual(r.status,'OWNER_PIN_UNPROVED')
        self.assertFalse(r.comparisons)

    def test_revision_edit_is_not_transport_proof(self):
        old,new,_,reg,p,q=self.make()
        agent=self.compare(old,new,reg,p,q,(('','AAA'),))
        new.snapshot.revision+=1
        self.assertEqual(agent.advance().status,'UNKNOWN_VERSION')
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_same_metadata_new_snapshot_cannot_borrow_token(self):
        old,new,_,reg,p,q=self.make()
        duplicate=LanguageBridge(new.remote,owner=new.owner,edge_budget=54)
        self.assertEqual(self.compare(old,duplicate,reg,p,q,(('','AAA'),)).advance().status,'OWNER_PIN_UNPROVED')
        self.assertEqual(len(duplicate.snapshot.edges),0)

    def test_unknown_pin_or_ambiguous_request_observe_nothing(self):
        old,new,_,reg,p,q=self.make()
        valid=self.task(p,q,(('BA','ABB'),))
        for req in ({**valid,'required_owner_pins':{'old':'a'*48,'new':q.token}},
                    {**valid,'compare_words':[['BA','BA']]},
                    {**valid,'compare_words':[['BAD','ABB']]},
                    {**valid,'note':'same owner'},
                    {**valid,'compare_words':[]}):
            agent=CrossPinComparison(old,new,req,registry=reg)
            self.assertIn(agent.advance().status,('UNKNOWN_OWNER_PIN','INVALID_TASK'))
        self.assertEqual((len(old.snapshot.edges),len(new.snapshot.edges)),(0,0))

    def test_budgets_stop_without_false_conclusion(self):
        old,new,_,reg,p,q=self.make(budget=2)
        result=self.settle(self.compare(old,new,reg,p,q,(('BA','ABB'),)))
        self.assertEqual(result.status,'UNKNOWN_BUDGET')
        self.assertFalse(result.comparisons)

if __name__=='__main__':unittest.main()
