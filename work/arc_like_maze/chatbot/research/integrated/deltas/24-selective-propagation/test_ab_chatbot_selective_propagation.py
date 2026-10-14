"""Multiple independent comparisons: only dependent certificates fully replay."""
import unittest
from ab_chatbot_selective_propagation import SelectivePropagationPortfolio
from ab_chatbot_source_change_propagation import SourceChangePropagation
from test_ab_chatbot_two_route_comparison import TwoRouteTests


class SelectivePortfolioTests(unittest.TestCase):
    def fixture(self, n=2):
        named={};fixtures={}
        for i in range(n):
            cmp,l,r,m,reg,p,q=TwoRouteTests.fixture(self,same_middle=(i==1))
            history=SourceChangePropagation(cmp)
            self.assertEqual(history.advance().status,'BASELINE_WITNESSED')
            name=f'comparison_{i}'
            named[name]=history
            fixtures[name]=(cmp,l,r,m,reg,p,q)
        return SelectivePropagationPortfolio(named),fixtures

    def test_no_changes_skip_full_replay_not_claim_fresh_proof(self):
        port,_=self.fixture()
        old={k:len(v.history) for k,v in port.named.items()}
        result=port.advance()
        self.assertEqual(result.audited,())
        self.assertEqual(result.skipped,('comparison_0','comparison_1'))
        self.assertTrue(all(not x.proof_fresh and x.mode=='CACHED_NOT_REPLAYED' for x in result.records))
        self.assertEqual(result.owner_observations_before,result.owner_observations_after)
        self.assertEqual({k:len(v.history) for k,v in port.named.items()},old)

    def test_one_changed_middle_replays_only_dependent_comparison(self):
        port,fx=self.fixture()
        _,_,_,_,reg,_,pin=fx['comparison_0']
        reg.revoke(pin.token)
        result=port.advance()
        self.assertEqual(result.audited,('comparison_0',))
        self.assertEqual(result.skipped,('comparison_1',))
        self.assertEqual(result.records[0].outcome,'COMPARISON_WITHDRAWN')
        self.assertTrue(result.records[0].proof_fresh)
        self.assertEqual(result.records[1].outcome,'BASELINE_WITNESSED')
        self.assertFalse(result.records[1].proof_fresh)
        self.assertEqual(len(port.named['comparison_1'].history),1)
        self.assertEqual(result.owner_observations_before,result.owner_observations_after)

    def test_multi_source_change_replays_both_only_when_both_affected(self):
        port,fx=self.fixture()
        fx['comparison_0'][4].revoke(fx['comparison_0'][6].token)
        fx['comparison_1'][1].final.registry.revoke(fx['comparison_1'][1].final._base._tokens[0])
        result=port.advance()
        self.assertEqual(result.audited,('comparison_0','comparison_1'))
        self.assertEqual(result.skipped,())
        self.assertTrue(all(x.outcome=='COMPARISON_WITHDRAWN' for x in result.records))
        self.assertEqual(result.owner_observations_before,result.owner_observations_after)

    def test_unused_cached_evidence_change_triggers_conservative_replay(self):
        port,fx=self.fixture()
        # Cached snapshot changes are conservative even when unrelated to path.
        snap=fx['comparison_0'][3].old.snapshot
        snap.edges[((2,2,2),'A')]=(0,0,0)
        result=port.advance()
        self.assertEqual(result.audited,('comparison_0',))
        self.assertEqual(result.skipped,('comparison_1',))
        self.assertIn('CACHED_EVIDENCE_CHANGED',result.changed_dependencies[0][2])

    def test_structure_swap_does_not_hide_under_identical_source_stamps(self):
        port,fx=self.fixture()
        cmp=fx['comparison_0'][0]
        cmp.right.first=cmp.left.first
        result=port.advance()
        self.assertEqual(result.audited,('comparison_0',))
        self.assertEqual(result.records[0].outcome,'COMPARISON_WITHDRAWN')
        self.assertEqual(result.changed_dependencies[0][1],'DECLARATION')

    def test_mapping_mutation_requires_replay_not_cache(self):
        port,fx=self.fixture()
        right=fx['comparison_0'][2]
        right.new_map[(1,2,1)]=(0,0,0)
        result=port.advance()
        self.assertEqual(result.audited,('comparison_0',))
        self.assertNotEqual(result.records[0].outcome,'COMPARISON_PRESERVED')

    def test_verify_for_use_audits_even_unchanged_record(self):
        port,_=self.fixture()
        self.assertFalse(port.advance().records[1].proof_fresh)
        row=port.verify_for_use('comparison_1')
        self.assertTrue(row.proof_fresh)
        self.assertEqual(row.mode,'REPLAYED')
        self.assertEqual(row.outcome,'COMPARISON_PRESERVED')
        self.assertEqual(len(port.named['comparison_1'].history),2)

    def test_unchanged_current_revision_does_not_invalidate_selected_historical_pin(self):
        port,fx=self.fixture()
        from ab_chatbot_discovered_correspondence import DOMAIN
        from ab_chatbot_stability_witness import TransportedLaw
        fx['comparison_0'][3].old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        result=port.advance()
        self.assertEqual(result.audited,('comparison_0',))
        self.assertEqual(result.records[0].outcome,'COMPARISON_PRESERVED')
        self.assertEqual(result.skipped,('comparison_1',))

    def test_invalid_inputs_and_unknown_forced_name_no_observations(self):
        with self.assertRaises(ValueError):SelectivePropagationPortfolio({})
        port,_=self.fixture()
        baseline=port._counts()
        with self.assertRaises(ValueError):port.advance(force=('missing',))
        with self.assertRaises(ValueError):port.verify_for_use('missing')
        self.assertEqual(port._counts(),baseline)

if __name__=='__main__':unittest.main()
