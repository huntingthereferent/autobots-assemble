"""One independently pinned source changes; only dependent certificates withdraw."""
import unittest
from ab_chatbot_source_change_propagation import SourceChangePropagation
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw
from test_ab_chatbot_two_route_comparison import TwoRouteTests


class ChangePropagationTests(unittest.TestCase):
    def fixture(self, *, agree=False):
        cmp,left,right,middle,registry,pold,pnew=TwoRouteTests.fixture(self,same_middle=agree)
        harness=SourceChangePropagation(cmp)
        first=harness.advance()
        self.assertEqual(first.status,'BASELINE_WITNESSED')
        self.assertEqual(first.left_route,first.right_route,'PRESERVED')
        return harness,cmp,left,right,middle,registry,pold,pnew

    def test_stable_conflict_remains_conflict_without_new_reads(self):
        h,*_=self.fixture()
        r=h.advance()
        self.assertEqual(r.status,'COMPARISON_PRESERVED')
        self.assertEqual(r.comparison,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual(r.changed_scopes,())
        self.assertEqual(r.affected_routes,())
        self.assertEqual(r.observations_before,r.observations_after)
        self.assertEqual(len(h.history),2)

    def test_stable_agreement_remains_scoped_not_global(self):
        h,*_=self.fixture(agree=True)
        r=h.advance()
        self.assertEqual(r.status,'COMPARISON_PRESERVED')
        self.assertEqual(r.comparison,'ROUTES_AGREE_ON_SELECTED_EDGE')
        self.assertEqual(r.current.disagreement,())

    def test_right_middle_revocation_withdraws_only_right_route(self):
        h,cmp,left,right,m,reg,po,pn=self.fixture()
        baseline=h.history[0].current
        reg.revoke(pn.token)
        r=h.advance()
        self.assertEqual((r.status,r.left_route,r.right_route,r.comparison),
          ('COMPARISON_WITHDRAWN','PRESERVED','WITHDRAWN','ROUTE_EVIDENCE_UNPROVED'))
        self.assertEqual(r.affected_routes,('right',))
        self.assertEqual([c.scope for c in r.changed_scopes],['right_middle'])
        self.assertIn('OWNER_BINDING_CHANGED',r.changed_scopes[0].causes)
        self.assertEqual(r.historical,baseline)
        self.assertEqual(r.observations_before,r.observations_after)
        self.assertEqual(h.advance().status,'COMPARISON_WITHDRAWN')

    def test_left_middle_revocation_withdraws_only_left(self):
        h,cmp,left,right,m,reg,*_=self.fixture()
        left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
        r=h.advance()
        self.assertEqual((r.left_route,r.right_route),('WITHDRAWN','PRESERVED'))
        self.assertEqual(r.affected_routes,('left',))
        self.assertEqual(r.changed_scopes[0].scope,'left_middle')

    def test_shared_final_pin_withdraws_both(self):
        h,cmp,left,right,m,reg,*_=self.fixture()
        left.final.registry.revoke(left.final._base._tokens[1])
        r=h.advance()
        self.assertEqual((r.left_route,r.right_route),('WITHDRAWN','WITHDRAWN'))
        self.assertEqual(r.affected_routes,('left','right'))
        self.assertEqual([c.scope for c in r.changed_scopes],['final'])

    def test_shared_donor_pin_withdraws_both(self):
        h,cmp,left,right,m,*_=self.fixture()
        donor=left.first.donor
        donor.registry.revoke(donor._base._tokens[0])
        r=h.advance()
        self.assertEqual((r.left_route,r.right_route),('WITHDRAWN','WITHDRAWN'))
        self.assertEqual(r.affected_routes,('left','right'))
        self.assertEqual([c.scope for c in r.changed_scopes],['donor'])

    def test_changed_right_revision_is_not_a_repin_or_new_proof(self):
        h,cmp,left,right,m,*_=self.fixture()
        m.old.snapshot.revision+=1
        r=h.advance()
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')
        self.assertEqual((r.left_route,r.right_route),('PRESERVED','WITHDRAWN'))
        self.assertIn('SOURCE_VERSION_CHANGED',r.changed_scopes[0].causes)
        self.assertEqual(r.affected_routes,('right',))

    def test_tampered_right_cached_edge_does_not_poison_left(self):
        h,cmp,left,right,m,*_=self.fixture()
        m.new.snapshot.edges[((0,1,1),'B')]=(2,2,2)
        r=h.advance()
        self.assertEqual((r.left_route,r.right_route),('PRESERVED','WITHDRAWN'))
        self.assertEqual(r.affected_routes,('right',))
        self.assertIn('CACHED_EVIDENCE_CHANGED',r.changed_scopes[0].causes)
        self.assertEqual(r.observations_before,r.observations_after)

    def test_new_owner_head_does_not_rewrite_pinned_historical_view(self):
        h,cmp,left,right,m,*_=self.fixture()
        # Only the latest owner revision moves. Both already pinned historical
        # objects remain valid and must continue to replay their old versions.
        m.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        r=h.advance()
        self.assertEqual(r.status,'COMPARISON_PRESERVED')
        self.assertEqual((r.left_route,r.right_route),('PRESERVED','PRESERVED'))
        self.assertEqual(r.affected_routes,('right',))
        self.assertIn('SOURCE_HEAD_ADVANCED',r.changed_scopes[0].causes)
        self.assertEqual(r.observations_before,r.observations_after)

    def test_unrelated_legitimate_observation_does_not_overthrow_join(self):
        h,cmp,left,right,m,*_=self.fixture()
        before=len(m.old.snapshot.edges)
        m.old.snapshot.step((2,2,2),'A')
        self.assertEqual(len(m.old.snapshot.edges),before+1)
        r=h.advance()
        self.assertEqual(r.status,'COMPARISON_PRESERVED')
        self.assertIn('OBSERVATION_COUNT_CHANGED',r.changed_scopes[0].causes)
        self.assertEqual(r.observations_before,r.observations_after)

    def test_scope_replacement_is_not_silently_promoted(self):
        h,cmp,left,right,m,*_=self.fixture()
        # The same observer can open another pinned snapshot, but the OLD pin
        # and chain reference are not transferred into it.
        m.old.snapshot=m.old._read_version()
        r=h.advance()
        self.assertEqual((r.left_route,r.right_route),('PRESERVED','WITHDRAWN'))
        self.assertIn('SNAPSHOT_REPLACED',r.changed_scopes[0].causes)
        self.assertEqual(r.status,'COMPARISON_WITHDRAWN')

    def test_scope_identity_mutation_is_rejected(self):
        h,cmp,left,right,m,*_=self.fixture()
        right.first=left.first
        report=h.advance()
        self.assertEqual(report.status,'COMPARISON_WITHDRAWN')
        self.assertNotEqual(report.current.status,'ROUTES_AGREE_ON_SELECTED_EDGE')

    def test_wrong_input_never_registers_a_ledger(self):
        with self.assertRaises(ValueError):SourceChangePropagation(None)

if __name__=='__main__':unittest.main()
