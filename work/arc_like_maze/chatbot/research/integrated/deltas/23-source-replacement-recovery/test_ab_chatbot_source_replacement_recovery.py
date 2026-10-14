"""New source is independently pinned and observed; old history never transferred."""
import unittest
from ab_chatbot_source_change_propagation import SourceChangePropagation
from ab_chatbot_source_replacement_recovery import SourceReplacementRecovery
from ab_chatbot_two_route_comparison import TwoRouteComparison
from ab_chatbot_two_hop_transport import TwoHopTransport
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import current_digest
from test_ab_chatbot_two_route_comparison import TwoRouteTests
from test_ab_chatbot_cross_pin_comparison import CrossPinTests


class SourceReplacementRecoveryTests(unittest.TestCase):
    def fixture(self, *, agreeing=True, revoke=True):
        cmp,left,right,old_middle,old_registry,old_pin,old_new_pin=TwoRouteTests.fixture(self)
        history=SourceChangePropagation(cmp)
        baseline=history.advance()
        self.assertEqual(baseline.status,'BASELINE_WITNESSED')
        if revoke:old_registry.revoke(old_new_pin.token)
        old_after=history.advance()
        self.assertEqual(old_after.right_route,'WITHDRAWN' if revoke else 'PRESERVED')
        # New owner, HTTP loopback, observer objects, snapshot objects, registry,
        # and owner pins: none may be borrowed from the historical middle.
        law=(0,0,0) if agreeing else (1,1,0)
        law_new=(0,1,2) if agreeing else (1,1,1)
        a,b,owner,registry,p,q=CrossPinTests.make(self,oldlaw=law,newlaw=law_new)
        fresh=CrossPinJoin(a,b,{'required_owner_pins':{'old':p.token,'new':q.token},
                   'join_words':['A','BAA']},registry=registry)
        self.assertEqual(len(a.snapshot.edges),len(b.snapshot.edges),0)
        joined=fresh.advance(max_new_edges=108)
        self.assertEqual(joined.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        donor=left.first.donor
        if agreeing:
            mo=[{'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,0]}]
            mn=[{'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,1],'recipient':[1,2,0]}]
            fo=[{'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,2]}]
            fn=fo.copy()
        else:
            mo=[{'donor':[1,0,0],'recipient':[0,1,1]},
                {'donor':[1,2,0],'recipient':[0,2,2]}]
            mn=[{'donor':[1,0,0],'recipient':[0,1,1]},
                {'donor':[1,2,1],'recipient':[0,2,2]}]
            fo=[{'donor':[0,1,1],'recipient':[0,1,2]},
                {'donor':[0,2,2],'recipient':[0,2,2]}]
            fn=[{'donor':[0,1,1],'recipient':[0,1,2]},
                {'donor':[0,2,2],'recipient':[0,2,1]}]
        first=CrossScopeIntertwiningTransfer(fresh,donor,{
          'recipient_fingerprint':current_digest(fresh),
          'donor_fingerprint':current_digest(donor),
          'selected_donor_edge':{'state':[1,0,0],'action':'B'},
          'old_state_transport':mo,'new_state_transport':mn})
        l1=first.advance()
        self.assertEqual(l1.status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        route=TwoHopTransport(first,left.final,{
          'first_link_fingerprint':l1.derived_fingerprint,
          'final_join_fingerprint':current_digest(left.final),
          'old_state_transport':fo,'new_state_transport':fn})
        result=route.advance()
        self.assertEqual(result.status,'TWO_HOP_CHAIN_WITNESSED')
        declaration={'historical_left_fingerprint':cmp.expected[0],
                     'historical_right_fingerprint':cmp.expected[1],
                     'replacement_right_fingerprint':result.fingerprint}
        recovered=SourceReplacementRecovery(history,route,declaration)
        self.assertEqual(recovered.status,'RECOVERY_DECLARED')
        return recovered, history,cmp,left,right,old_middle,old_registry,old_new_pin,fresh,registry,p,q

    def test_agreeing_replacement_creates_new_agreement(self):
        r,*_=self.fixture()
        result=r.advance()
        self.assertEqual(result.status,'RECOVERY_AGREEMENT_WITNESSED')
        self.assertEqual(result.recovered_comparison.status,'ROUTES_AGREE_ON_SELECTED_EDGE')
        self.assertEqual(result.historical.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual(result.historical_refresh.right_route,'WITHDRAWN')
        self.assertIsNot(result.earlier_right_scope,result.replacement_scope)
        self.assertEqual(result.observations_before,result.observations_after)

    def test_conflicting_replacement_is_still_valid_recovery(self):
        r,*_=self.fixture(agreeing=False)
        result=r.advance()
        self.assertEqual(result.status,'RECOVERY_CONFLICT_WITNESSED')
        self.assertEqual(result.recovered_comparison.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual(len(result.recovered_comparison.disagreement),4)
        self.assertEqual(result.observations_before,result.observations_after)

    def test_old_middle_retains_observations_but_no_proof(self):
        r,h,cmp,left,right,oldmiddle,reg,token,fresh,*_=self.fixture()
        old_edges=(len(oldmiddle.old.snapshot.edges),len(oldmiddle.new.snapshot.edges))
        result=r.advance()
        self.assertEqual(result.historical_refresh.right_route,'WITHDRAWN')
        self.assertEqual((len(oldmiddle.old.snapshot.edges),len(oldmiddle.new.snapshot.edges)),old_edges)
        self.assertEqual(cmp.advance().status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertEqual(left.advance().status,'TWO_HOP_CHAIN_WITNESSED')
        self.assertEqual(fresh.advance(max_new_edges=0).status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')

    def test_repeat_recovery_does_not_observe_again(self):
        r,*_=self.fixture()
        a=r.advance();b=r.advance()
        self.assertEqual(a.status,b.status)
        self.assertEqual(a.observations_after,b.observations_after)
        self.assertEqual(b.observations_before,b.observations_after)
        self.assertEqual(len(r.records),2)

    def test_replacement_pin_revocation_withholds_success(self):
        r,*rest=self.fixture()
        self.assertEqual(r.advance().status,'RECOVERY_AGREEMENT_WITNESSED')
        fresh,reg,p,q=rest[-4:]
        reg.revoke(q.token)
        report=r.advance()
        self.assertEqual(report.status,'REPLACEMENT_EVIDENCE_UNPROVED')
        self.assertNotIn(report.recovered_comparison.status,('ROUTES_AGREE_ON_SELECTED_EDGE','ROUTE_COMPOSED_MAP_CONFLICT'))

    def test_forged_replacement_observation_stops_recovery(self):
        r,*_=self.fixture()
        self.assertEqual(r.advance().status,'RECOVERY_AGREEMENT_WITNESSED')
        fresh=r.new_middle
        fresh.new.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        report=r.advance()
        self.assertEqual(report.status,'REPLACEMENT_EVIDENCE_UNPROVED')
        self.assertEqual(report.recovered_comparison.status,'ROUTE_EVIDENCE_UNPROVED')

    def test_left_pin_revoked_makes_recovery_impossible(self):
        r,h,cmp,left,*_=self.fixture()
        self.assertEqual(r.advance().status,'RECOVERY_AGREEMENT_WITNESSED')
        left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
        result=r.advance()
        self.assertEqual(result.status,'RECOVERY_LEFT_EVIDENCE_UNPROVED')

    def test_old_right_still_valid_is_not_silently_replaced(self):
        r,*_=self.fixture(revoke=False)
        self.assertEqual(r.advance().status,'RECOVERY_NOT_NEEDED')

    def test_mismatched_historical_fingerprint_rejected(self):
        r,h,cmp,*_=self.fixture()
        bad=SourceReplacementRecovery(h,r.replacement,{
            'historical_left_fingerprint':'0'*64,
            'historical_right_fingerprint':cmp.expected[1],
            'replacement_right_fingerprint':r.expected[2]})
        self.assertEqual(bad.advance().status,'INVALID_RECOVERY')

    def test_historical_scope_reuse_is_not_replacement(self):
        r,h,cmp,left,right,*_=self.fixture()
        old=SourceReplacementRecovery(h,right,{
            'historical_left_fingerprint':cmp.expected[0],
            'historical_right_fingerprint':cmp.expected[1],
            'replacement_right_fingerprint':cmp.expected[1]})
        self.assertEqual(old.advance().status,'INVALID_RECOVERY')

    def test_replacement_identity_swap_cannot_keep_success(self):
        r,*_=self.fixture()
        self.assertEqual(r.advance().status,'RECOVERY_AGREEMENT_WITNESSED')
        r.replacement.first.recipient=r.old_middle
        self.assertEqual(r.advance().status,'RECOVERY_SCOPE_CHANGED')

    def test_current_owner_revision_does_not_revoke_valid_historical_snapshot(self):
        r,h,cmp,left,right,oldmiddle,*_=self.fixture()
        from ab_chatbot_discovered_correspondence import DOMAIN
        from ab_chatbot_stability_witness import TransportedLaw
        self.assertEqual(r.advance().status,'RECOVERY_AGREEMENT_WITNESSED')
        r.new_middle.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        result=r.advance()
        self.assertEqual(result.status,'RECOVERY_AGREEMENT_WITNESSED')
        self.assertEqual(result.observations_before,result.observations_after)

    def test_invalid_contract_zero_new_observations(self):
        r,*_=self.fixture()
        before=r._counts()
        bad=SourceReplacementRecovery(r.history,r.replacement,{'recovery':'yes'})
        self.assertEqual(bad.advance().status,'INVALID_RECOVERY')
        self.assertEqual(r._counts(),before)

if __name__=='__main__':unittest.main()
