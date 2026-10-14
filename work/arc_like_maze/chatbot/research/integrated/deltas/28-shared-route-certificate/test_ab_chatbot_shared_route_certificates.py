"""CP-28 in-process owner-pinned integration and negative controls."""
import unittest
from ab_chatbot_shared_route_certificate import SharedRouteTaskPortfolio
from test_ab_chatbot_multi_task_dependency import MultiRouteTaskDependencyTests
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests


class SharedRouteTaskTests(unittest.TestCase):
    def fixture(self, extra=None):
        refresh,_,left,right,middle,reg,_,pin=RouteBoundTaskTests.fixture(self)
        factory=RouteBoundTaskTests.task
        named={
          'left_a':factory(self,refresh,'left',required_edges=[{'state':[1,0,0],'action':'B'}]),
          'left_b':factory(self,refresh,'left',required_edges=[{'state':[1,1,2],'action':'A'}]),
          'right_a':factory(self,refresh,'right',required_edges=[{'state':[0,1,2],'action':'B'}])}
        if extra is not None:named.update(extra(refresh))
        p=SharedRouteTaskPortfolio(named)
        spy=MultiRouteTaskDependencyTests.spy(self,left,right)
        return p,left,right,reg,pin,spy

    def test_shared_left_audit_two_replays_not_four(self):
        p,_,_,_,_,spy=self.fixture()
        r=p.advance(force_tasks=('left_a','left_b'))
        self.assertEqual(r.audited,('left_a','left_b'))
        self.assertEqual(p.last_route_audits,1)
        self.assertEqual(spy,{'left':2,'right':0})
        self.assertTrue(all(e.proof_for_use for e in r.entries[:2]))
        self.assertFalse(r.entries[2].fresh)
        self.assertIs(r.entries[0].result.route_certificate,
                      r.entries[1].result.route_certificate)
        self.assertNotEqual(r.entries[0].result.task_fingerprint,
                            r.entries[1].result.task_fingerprint)

    def test_each_task_obligation_is_independent(self):
        def extra(refresh):
            return {'left_unproved':RouteBoundTaskTests.task(self,refresh,'left',required_edges=[
                {'state':[0,1,2],'action':'B'}])}
        p,_,_,_,_,spy=self.fixture(extra)
        r=p.advance(force_tasks=tuple(p.named))
        self.assertEqual(spy,{'left':2,'right':2})
        self.assertEqual(p.last_route_audits,2)
        self.assertEqual([e.status for e in r.entries],
            ['TASK_COMPLETED_ON_SELECTED_ROUTE','TASK_COMPLETED_ON_SELECTED_ROUTE',
             'TASK_COMPLETED_ON_SELECTED_ROUTE','ROUTE_TASK_REQUIREMENTS_UNPROVED'])
        self.assertFalse(r.entries[-1].proof_for_use)

    def test_idle_is_cached_never_fresh(self):
        p,_,_,_,_,spy=self.fixture();r=p.advance()
        self.assertEqual(r.audited,());self.assertEqual(p.last_route_audits,0)
        self.assertEqual(spy,{'left':0,'right':0})
        self.assertTrue(all(e.mode=='CACHED_NOT_REPLAYED' and not e.fresh for e in r.entries))

    def test_right_revocation_only_right_audited(self):
        p,_,_,reg,pin,spy=self.fixture();reg.revoke(pin.token)
        r=p.advance();self.assertEqual(r.audited,('right_a',))
        self.assertEqual(spy,{'left':0,'right':2})
        self.assertEqual(r.entries[-1].status,'OWNER_PIN_UNPROVED')
        self.assertTrue(all(not e.proof_for_use for e in r.entries))

    def test_left_revocation_two_tasks_one_failed_audit(self):
        p,left,_,_,_,spy=self.fixture()
        left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
        r=p.advance();self.assertEqual(r.audited,('left_a','left_b'))
        self.assertEqual(spy,{'left':2,'right':0})
        self.assertTrue(all(e.status=='OWNER_PIN_UNPROVED' for e in r.entries[:2]))

    def test_shared_source_change_one_audit_each_route(self):
        p,left,_,_,_,spy=self.fixture()
        left.final.old.snapshot.revision+=1
        r=p.advance();self.assertEqual(r.audited,('left_a','left_b','right_a'))
        self.assertEqual(spy,{'left':2,'right':2})
        self.assertFalse(any(e.proof_for_use for e in r.entries))

    def test_force_only_one_task_no_sibling_promotion(self):
        p,_,_,_,_,spy=self.fixture();r=p.verify_for_use('left_b')
        self.assertEqual(spy,{'left':2,'right':0})
        self.assertEqual(r.name,'left_b');self.assertTrue(r.proof_for_use)
        self.assertFalse(p.history[-1].entries[0].fresh)

    def test_route_map_change_withholds_shared_success(self):
        p,left,_,_,_,_=self.fixture()
        left.old_map[(1,2,0)]=(2,2,2)
        r=p.advance()
        self.assertTrue(all(e.status=='TASK_DECLARATION_CHANGED' for e in r.entries[:2]))

    def test_task_obligation_tamper_only_flags_that_task(self):
        p,_,_,_,_,spy=self.fixture()
        p.named['left_a'].task.edges=(((1,1,2),'A'),)
        r=p.advance()
        self.assertEqual(r.audited,('left_a',))
        self.assertEqual(r.entries[0].status,'TASK_DECLARATION_CHANGED')
        self.assertEqual(spy,{'left':0,'right':0})

    def test_mid_audit_change_withholds_both_siblings(self):
        p,left,_,_,_,_=self.fixture();old=left.advance
        calls={'count':0}
        def moving():
            result=old();calls['count']+=1
            if calls['count']==1:left.first.recipient.old.snapshot.revision+=1
            return result
        left.advance=moving
        r=p.advance(force_tasks=('left_a','left_b'))
        self.assertEqual(r.status,'SOURCE_MOVED_DURING_AUDIT')
        self.assertFalse(r.entries[0].proof_for_use)
        self.assertFalse(r.entries[1].proof_for_use)
        self.assertIn('left_a',p._dirty);self.assertIn('left_b',p._dirty)

    def test_malformed_force_rejected(self):
        p,_,_,_,_,_=self.fixture()
        with self.assertRaises(ValueError):p.advance(force_tasks=('left_a','left_a'))

    def test_historical_baseline_intact(self):
        p,_,_,reg,pin,_=self.fixture()
        orig=p.history[0].entries[-1]
        reg.revoke(pin.token);p.advance()
        self.assertEqual(p.history[0].entries[-1],orig)

    def test_fresh_one_audit_matches_individual_prior_results(self):
        p,_,_,_,_,_=self.fixture();r=p.advance(force_tasks=('left_a','left_b'))
        for e in r.entries[:2]:
            individual=p.named[e.name].advance()
            self.assertEqual(e.status,individual.status)
            self.assertEqual(e.result.obligations,individual.obligations)
            self.assertEqual(e.result.route_certificate,individual.route_certificate)

if __name__=='__main__':unittest.main()
