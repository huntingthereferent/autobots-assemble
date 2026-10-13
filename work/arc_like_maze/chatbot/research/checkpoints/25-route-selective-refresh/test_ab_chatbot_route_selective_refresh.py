"""Observed selective route replay, pin revocation, and no cache promotion."""
import unittest
from ab_chatbot_route_selective_refresh import RouteSelectiveRefresh
from ab_chatbot_source_change_propagation import SourceChangePropagation
from test_ab_chatbot_two_route_comparison import TwoRouteTests


class RouteSelectiveTests(unittest.TestCase):
    def fixture(self, agree=False):
        cmp,left,right,middle,registry,oldpin,newpin=TwoRouteTests.fixture(
            self,same_middle=agree)
        ledger=SourceChangePropagation(cmp)
        self.assertEqual(ledger.advance().status,'BASELINE_WITNESSED')
        return RouteSelectiveRefresh(ledger),cmp,left,right,middle,registry,oldpin,newpin

    def spy(self,left,right):
        counter={'left':0,'right':0}
        for name,route in [('left',left),('right',right)]:
            original=route.advance
            def wrapped(*args, _name=name, _orig=original, **kwargs):
                counter[_name]+=1
                return _orig(*args,**kwargs)
            route.advance=wrapped
        return counter

    def test_stable_cache_replays_neither_route(self):
        port,_,left,right,*_=self.fixture()
        count=self.spy(left,right)
        a=port.advance()
        self.assertEqual(a.status,'COMPARISON_CACHED_NOT_REPLAYED')
        self.assertEqual((a.audited,a.skipped),((),('left','right')))
        self.assertFalse(a.proof_for_use)
        self.assertEqual(count,{'left':0,'right':0})
        self.assertTrue(all(not x.proof_fresh for x in a.routes))
        self.assertEqual(a.observations_before,a.observations_after)

    def test_revoked_right_middle_checks_right_not_left(self):
        port,_,left,right,middle,registry,_,pin=self.fixture()
        spy=self.spy(left,right)
        registry.revoke(pin.token)
        result=port.advance()
        self.assertEqual(result.status,'COMPARISON_WITHDRAWN')
        self.assertEqual((result.audited,result.skipped),(('right',),('left',)))
        self.assertEqual(spy['left'],0)
        self.assertGreaterEqual(spy['right'],1)
        self.assertFalse(result.routes[0].proof_fresh)
        self.assertNotEqual(result.routes[1].outcome,'TWO_HOP_CHAIN_WITNESSED')
        self.assertFalse(result.proof_for_use)
        self.assertEqual(result.observations_before,result.observations_after)

    def test_left_middle_revocation_checks_only_left(self):
        port,_,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
        r=port.advance()
        self.assertEqual((r.audited,r.skipped),(('left',),('right',)))
        self.assertGreater(spy['left'],0)
        self.assertEqual(spy['right'],0)
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')

    def test_shared_final_revocation_rechecks_both(self):
        port,_,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        left.final.registry.revoke(left.final._base._tokens[0])
        r=port.advance()
        self.assertEqual(r.audited,('left','right'))
        self.assertGreater(spy['left'],0)
        self.assertGreater(spy['right'],0)
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')

    def test_unused_cached_edge_change_only_rechecks_dependent_route(self):
        port,_,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        right.first.recipient.old.snapshot.edges[((2,2,2),'A')]=(0,0,0)
        r=port.advance()
        self.assertEqual(r.audited,('right',))
        self.assertEqual(spy['left'],0)
        self.assertEqual(r.observations_before,r.observations_after)
        self.assertFalse(r.proof_for_use)

    def test_tampered_used_edge_on_left_cannot_promote_old_comparison(self):
        port,_,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        left.first.recipient.old.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        r=port.advance()
        self.assertEqual(r.audited,('left',))
        self.assertEqual(spy['right'],0)
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')
        self.assertFalse(r.proof_for_use)
        self.assertEqual(r.historical_comparison.status,'ROUTE_COMPOSED_MAP_CONFLICT')

    def test_new_owner_head_on_right_rechecks_only_right_but_does_not_promote(self):
        port,_,left,right,middle,*_=self.fixture()
        from ab_chatbot_discovered_correspondence import DOMAIN
        from ab_chatbot_stability_witness import TransportedLaw
        spy=self.spy(left,right)
        middle.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        r=port.advance()
        self.assertEqual(r.audited,('right',))
        self.assertEqual(spy['left'],0)
        self.assertEqual(r.routes[1].outcome,'TWO_HOP_CHAIN_WITNESSED')
        self.assertEqual(r.status,'COMPARISON_REQUIRES_FULL_AUDIT')
        self.assertFalse(r.proof_for_use)

    def test_explicit_use_replays_both_and_proves_conflict(self):
        port,_,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        self.assertEqual(port.advance().status,'COMPARISON_CACHED_NOT_REPLAYED')
        r=port.verify_for_use()
        self.assertEqual(r.status,'COMPARISON_FULLY_WITNESSED')
        self.assertEqual(r.current_comparison.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertTrue(r.proof_for_use)
        self.assertTrue(all(x.proof_fresh for x in r.routes))
        self.assertGreater(spy['left'],0)
        self.assertGreater(spy['right'],0)
        self.assertEqual(r.observations_before,r.observations_after)

    def test_explicit_use_proves_agreement_not_just_conflict(self):
        port,*_=self.fixture(agree=True)
        r=port.verify_for_use()
        self.assertEqual(r.status,'COMPARISON_FULLY_WITNESSED')
        self.assertEqual(r.current_comparison.status,'ROUTES_AGREE_ON_SELECTED_EDGE')

    def test_explicit_use_cannot_succeed_after_changed_pin(self):
        port,_,left,right,middle,registry,_,pin=self.fixture()
        registry.revoke(pin.token)
        r=port.verify_for_use()
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')
        self.assertFalse(r.proof_for_use)
        self.assertEqual(r.current_comparison.status,'ROUTE_EVIDENCE_UNPROVED')

    def test_route_map_mutation_forces_conservative_both_and_no_success(self):
        port,cmp,left,right,*_=self.fixture()
        right.new_map[(1,2,1)]=(0,0,0)
        r=port.advance()
        self.assertEqual(r.audited,('left','right'))
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')
        self.assertFalse(r.proof_for_use)
        self.assertEqual(port.verify_for_use().status,'COMPARISON_WITHDRAWN')

    def test_source_swap_forces_conservative_rejection(self):
        port,cmp,left,right,*_=self.fixture()
        right.first=left.first
        r=port.advance()
        self.assertEqual(r.audited,('left','right'))
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')
        self.assertFalse(port.verify_for_use().proof_for_use)

    def test_explicit_one_sided_force_is_only_route_freshness(self):
        port,_,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        r=port.advance(force_routes=('right',))
        self.assertEqual(r.status,'COMPARISON_REQUIRES_FULL_AUDIT')
        self.assertEqual(r.audited,('right',))
        self.assertEqual(spy['left'],0)
        self.assertFalse(r.proof_for_use)

    def test_invalid_force_and_unwitnessed_initialization(self):
        port,*_=self.fixture()
        before=port._counts()
        for names in (('wrong',),('right','right'),['left']):
            with self.assertRaises(ValueError):port.advance(force_routes=names)
        self.assertEqual(port._counts(),before)
        with self.assertRaises(ValueError):RouteSelectiveRefresh(object())

if __name__=='__main__':unittest.main()
