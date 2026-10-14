"""Live pinned-owner integration: tasks share sources, but not task certificates."""
import unittest
from ab_chatbot_multi_task_dependency import MultiRouteTaskDependencies
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests


class MultiRouteTaskDependencyTests(unittest.TestCase):
    def fixture(self,extra=False):
        refresh,cmp,left,right,middle,reg,pold,pnew=RouteBoundTaskTests.fixture(self)
        factory=RouteBoundTaskTests.task
        left_a=factory(self,refresh,'left',required_edges=[{'state':[1,0,0],'action':'B'}])
        left_b=factory(self,refresh,'left',required_edges=[{'state':[1,1,2],'action':'A'}])
        right_a=factory(self,refresh,'right',required_edges=[{'state':[0,1,2],'action':'B'}])
        named={'left_a':left_a,'left_b':left_b,'right_a':right_a}
        other=None
        if extra:
            second=RouteBoundTaskTests.fixture(self)
            other=factory(self,second[0],'left',required_edges=[{'state':[1,0,0],'action':'B'}])
            named['other']=other
        ledger=MultiRouteTaskDependencies(named)
        self.assertEqual(ledger.history[0].status,'BASELINE_AUDITED')
        self.assertEqual(tuple(e.status for e in ledger.history[0].entries),
                         ('TASK_COMPLETED_ON_SELECTED_ROUTE',)*len(named))
        return ledger,left,right,middle,reg,pnew,other

    def spy(self,left,right):
        counts={'left':0,'right':0}
        for n,r in [('left',left),('right',right)]:
            orig=r.advance
            def wrapper(*a,_n=n,_orig=orig,**kw):
                counts[_n]+=1
                return _orig(*a,**kw)
            r.advance=wrapper
        return counts

    def test_initial_dependency_graph_has_exact_shared_scopes(self):
        p,*_=self.fixture()
        dep=p._depend
        self.assertEqual(dep['left_a'],dep['left_b'])
        self.assertEqual(dep['left_a'][0],dep['right_a'][0])
        self.assertEqual(dep['left_a'][2],dep['right_a'][2])
        self.assertNotEqual(dep['left_a'][1],dep['right_a'][1])
        self.assertEqual(len(p.dependencies()),4)

    def test_idle_causes_zero_route_replays_and_only_cached_status(self):
        p,left,right,*_=self.fixture()
        spies=self.spy(left,right)
        r=p.advance()
        self.assertEqual(r.status,'TASKS_CACHED_NOT_REPLAYED')
        self.assertEqual(r.audited,())
        self.assertEqual(r.cached,('left_a','left_b','right_a'))
        self.assertTrue(all(not x.fresh for x in r.entries))
        self.assertEqual(spies,{'left':0,'right':0})
        self.assertEqual(r.observations_before,r.observations_after)

    def test_right_middle_revocation_refreshes_only_right_task(self):
        p,left,right,middle,reg,pin,*_=self.fixture()
        spy=self.spy(left,right)
        reg.revoke(pin.token)
        r=p.advance()
        self.assertEqual(r.audited,('right_a',))
        self.assertEqual(r.cached,('left_a','left_b'))
        self.assertEqual([e.status for e in r.entries],
           ['TASK_COMPLETED_ON_SELECTED_ROUTE','TASK_COMPLETED_ON_SELECTED_ROUTE','OWNER_PIN_UNPROVED'])
        self.assertEqual(spy,{'left':0,'right':2})
        self.assertEqual(r.observations_before,r.observations_after)
        self.assertFalse(r.entries[0].fresh)

    def test_left_middle_revocation_refreshes_both_left_tasks_not_right(self):
        p,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
        r=p.advance()
        self.assertEqual(r.audited,('left_a','left_b'))
        self.assertEqual(r.cached,('right_a',))
        self.assertEqual(spy,{'left':4,'right':0})
        self.assertTrue(all(x.status=='OWNER_PIN_UNPROVED' for x in r.entries[:2]))

    def test_shared_donor_pin_affects_all_three(self):
        p,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        left.first.donor.registry.revoke(left.first.donor._base._tokens[0])
        r=p.advance()
        self.assertEqual(r.audited,('left_a','left_b','right_a'))
        self.assertEqual(spy,{'left':4,'right':2})
        self.assertTrue(all(e.status=='OWNER_PIN_UNPROVED' for e in r.entries))

    def test_shared_final_tamper_affects_all_three(self):
        p,left,right,*_=self.fixture()
        left.final.old.snapshot.revision+=1
        r=p.advance()
        self.assertEqual(r.audited,('left_a','left_b','right_a'))
        self.assertTrue(all(e.status!='TASK_COMPLETED_ON_SELECTED_ROUTE' for e in r.entries))

    def test_no_cross_network_replay_for_distinct_comparison(self):
        p,left,right,middle,reg,pin,other=self.fixture(extra=True)
        spy=self.spy(left,right)
        reg.revoke(pin.token)
        r=p.advance()
        self.assertEqual(r.audited,('right_a',))
        self.assertIn('other',r.cached)
        self.assertEqual(spy,{'left':0,'right':2})

    def test_verify_for_use_only_selected_task_no_cached_laundering(self):
        p,left,right,middle,reg,pin,*_=self.fixture()
        spy=self.spy(left,right)
        p.advance()
        r=p.verify_for_use('left_a')
        self.assertTrue(r.fresh)
        self.assertEqual(r.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(spy,{'left':2,'right':0})
        reg.revoke(pin.token)
        r2=p.verify_for_use('right_a')
        self.assertEqual(r2.status,'OWNER_PIN_UNPROVED')
        self.assertEqual(spy,{'left':2,'right':2})

    def test_individual_requirements_not_merged_between_tasks(self):
        p,left,right,*_=self.fixture()
        t=p.named['left_a']
        t.task.edges=(((0,1,2),'B'),)
        r=p.advance()
        self.assertIn('left_a',r.audited)
        self.assertNotEqual(r.entries[0].status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(r.entries[1].mode,'CACHED_NOT_REPLAYED')

    def test_mutating_obligations_to_another_valid_edge_still_refused(self):
        p,left,right,*_=self.fixture()
        p.named['left_a'].task.edges=(((1,1,2),'A'),)
        r=p.advance()
        self.assertEqual(r.audited,('left_a',))
        self.assertEqual(r.entries[0].status,'TASK_DECLARATION_CHANGED')
        self.assertFalse(r.entries[0].proof_for_use)

    def test_movement_after_one_task_audit_withholds_all_affected_freshness(self):
        p,left,right,*_=self.fixture()
        old=left.advance
        calls={'n':0}
        def moving():
            r=old()
            calls['n']+=1
            # First task may complete, but a shared source then moves
            # during its sibling's audit. The first result is no longer fresh.
            if calls['n']==3:
                left.first.recipient.old.snapshot.revision+=1
            return r
        left.advance=moving
        r=p.advance(force_tasks=('left_a','left_b'))
        self.assertEqual(r.status,'SOURCE_MOVED_DURING_AUDIT')
        self.assertFalse(r.entries[0].proof_for_use)
        self.assertFalse(r.entries[1].proof_for_use)
        self.assertFalse(r.entries[0].fresh)
        self.assertIn('left_a',p._dirty)
        self.assertIn('left_b',p._dirty)
        self.assertNotIn('right_a',p._dirty)

    def test_declared_notification_forces_reaudit_even_without_stamp_change(self):
        p,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        changed=p._depend['right_a'][1]
        r=p.advance(changed_sources=(changed,))
        self.assertEqual(r.audited,('right_a',))
        self.assertEqual(spy,{'left':0,'right':2})
        self.assertEqual(r.changed_sources,(changed,))
        self.assertEqual(r.observations_before,r.observations_after)

    def test_force_task_does_not_audit_siblings(self):
        p,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        r=p.advance(force_tasks=('left_b',))
        self.assertEqual(r.audited,('left_b',))
        self.assertEqual(spy,{'left':2,'right':0})

    def test_malformed_notification_rejected_without_replay(self):
        p,left,right,*_=self.fixture()
        spy=self.spy(left,right)
        for notify,force in ((('wrong',),()),((),('wrong',)),
                ((p._depend['left_a'][1],)*2,()),((),('left_a','left_a')),
                (['bad'],())):
            with self.assertRaises(ValueError):p.advance(changed_sources=notify,force_tasks=force)
        self.assertEqual(spy,{'left':0,'right':0})

    def test_prior_history_preserved_after_withdrawal(self):
        p,left,right,middle,reg,pin,*_=self.fixture()
        prior=p.history[0].entries[-1]
        self.assertEqual(prior.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        reg.revoke(pin.token)
        result=p.advance()
        self.assertEqual(result.entries[-1].status,'OWNER_PIN_UNPROVED')
        self.assertEqual(p.history[0].entries[-1],prior)

    def test_independent_owner_head_new_revision_preserves_exact_old_pin(self):
        from ab_chatbot_discovered_correspondence import DOMAIN
        from ab_chatbot_stability_witness import TransportedLaw
        p,left,right,middle,*_=self.fixture()
        middle.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        r=p.advance()
        self.assertEqual(r.audited,('right_a',))
        self.assertEqual(r.entries[-1].status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(r.observations_before,r.observations_after)

    def test_source_moves_during_audit_cannot_keep_fresh_success(self):
        p,left,right,*_=self.fixture()
        old=right.advance
        calls={'n':0}
        def moving():
            result=old()
            calls['n']+=1
            if calls['n']==2:
                right.final.old.snapshot.revision+=1
            return result
        right.advance=moving
        r=p.advance(force_tasks=('right_a',))
        self.assertEqual(r.status,'SOURCE_MOVED_DURING_AUDIT')
        self.assertEqual(r.entries[-1].status,'SOURCE_MOVED_DURING_AUDIT')
        self.assertFalse(r.entries[-1].fresh)
        self.assertEqual(r.cached,('left_a','left_b'))
        follow=p.advance()
        self.assertIn('right_a',follow.audited)
        self.assertIn('left_a',follow.audited)
        self.assertIn('left_b',follow.audited)

    def test_invalid_registration(self):
        p,*_=self.fixture()
        with self.assertRaises(ValueError):MultiRouteTaskDependencies({'one':p.named['left_a']})
        with self.assertRaises(ValueError):MultiRouteTaskDependencies({'a':p.named['left_a'],'b':p.named['left_a']})
        with self.assertRaises(ValueError):MultiRouteTaskDependencies({'a':p.named['left_a'],'b':object()})

    def test_unrelated_route_substitution_cannot_prove_task(self):
        p,left,right,*_=self.fixture()
        p.named['left_a']._comparison.left=right
        r=p.advance()
        self.assertIn('left_a',r.audited)
        self.assertIn('left_b',r.audited)
        self.assertNotEqual(r.entries[0].status,'TASK_COMPLETED_ON_SELECTED_ROUTE')

if __name__=='__main__':unittest.main()
