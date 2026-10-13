"""Real in-process owners; one chosen route is auditable despite neighbor changes."""
import unittest
from copy import deepcopy
from ab_chatbot_route_bound_task import RouteBoundTask
from test_ab_chatbot_route_selective_refresh import RouteSelectiveTests

class RouteBoundTaskTests(unittest.TestCase):
    def fixture(self):
        return RouteSelectiveTests.fixture(self)

    def task(self,refresh,side='left',**requirements):
        d={'route':side,'route_fingerprint':refresh.comparison.expected[0 if side=='left' else 1]}
        d.update(requirements or {'required_edges':[{'state':[1,0,0] if side=='left' else [0,1,2],'action':'B'}]})
        return RouteBoundTask(refresh,d)

    def spies(self,left,right):
        counts={'left':0,'right':0}
        for side,route in [('left',left),('right',right)]:
            underlying=route.advance
            def wrapper(*args, _orig=underlying, _side=side, **kwargs):
                counts[_side]+=1
                return _orig(*args,**kwargs)
            route.advance=wrapper
        return counts

    def test_one_route_completes_despite_neighbor_revocation(self):
        refresh,comparison,left,right,middle,registry,_,pin=self.fixture()
        spies=self.spies(left,right)
        task=self.task(refresh,'left',required_edges=[{'state':[1,0,0],'action':'B'},
                                                     {'state':[1,1,2],'action':'A'}])
        registry.revoke(pin.token)
        before=tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges))
              for p in (left.first.donor,left.first.recipient,left.final))
        r=task.advance()
        self.assertEqual(r.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(spies,{'left':2,'right':0})
        self.assertEqual(len(r.obligations),2)
        self.assertEqual(r.observations_before,r.observations_after)
        self.assertEqual(before,r.observations_after)
        self.assertEqual(refresh.verify_for_use().status,'COMPARISON_WITHDRAWN')

    def test_reverse_neighbor_revocation_right_still_works(self):
        refresh,comparison,left,right,*_=self.fixture()
        task=self.task(refresh,'right',required_edges=[{'state':[0,1,2],'action':'B'}])
        spies=self.spies(left,right)
        left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
        r=task.advance()
        self.assertEqual(r.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(spies,{'left':0,'right':2})

    def test_right_only_edge_not_borrowed_by_left(self):
        refresh,*_=self.fixture()
        r=self.task(refresh,'left',required_edges=[{'state':[0,1,2],'action':'B'}]).advance()
        self.assertEqual(r.status,'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual(len(r.obligations),1)
        self.assertFalse(r.obligations[0].admitted)

    def test_both_route_required_edges_never_merged(self):
        refresh,*_=self.fixture()
        req=[{'state':[1,0,0],'action':'B'},{'state':[0,1,2],'action':'B'}]
        self.assertEqual(self.task(refresh,'left',required_edges=req).advance().status,
                         'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        self.assertEqual(self.task(refresh,'right',required_edges=req).advance().status,
                         'ROUTE_TASK_REQUIREMENTS_UNPROVED')

    def test_route_tasks_different_destination_images(self):
        refresh,*_=self.fixture()
        task1=self.task(refresh,'left',required_destinations=[
            {'source':[1,2,2],'image':[1,2,2]}])
        task2=self.task(refresh,'right',required_destinations=[
            {'source':[0,2,2],'image':[0,2,1]}])
        self.assertEqual(task1.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(task2.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertNotEqual(task1.task_fingerprint,task2.task_fingerprint)

    def test_selected_route_exact_path_and_goal(self):
        refresh,*_=self.fixture()
        result=self.task(refresh,'right',goals=[[0,2,2]],
            required_paths=[{'word':'BB','old_end':[0,2,2],'new_end':[0,2,1]}]).advance()
        self.assertEqual(result.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual([o.kind for o in result.obligations],['GOAL','PATH'])

    def test_mismatched_path_and_unwitnessed_extension_rejected(self):
        refresh,*_=self.fixture()
        bad=self.task(refresh,'right',required_paths=[
            {'word':'BB','old_end':[0,2,2],'new_end':[0,2,2]}]).advance()
        self.assertEqual(bad.status,'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        noedge=self.task(refresh,'left',required_paths=[
            {'word':'BB','old_end':[0,2,2],'new_end':[0,2,1]}]).advance()
        self.assertEqual(noedge.status,'ROUTE_TASK_REQUIREMENTS_UNPROVED')

    def test_revoked_selected_route_pin_withholds_completion(self):
        refresh,cmp,left,right,middle,reg,_,pin=self.fixture()
        t=self.task(refresh,'right')
        self.assertEqual(t.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        reg.revoke(pin.token)
        self.assertEqual(t.advance().status,'OWNER_PIN_UNPROVED')

    def test_selected_revision_or_tampered_edge_withholds_completion(self):
        refresh,cmp,left,right,*_=self.fixture()
        t=self.task(refresh,'left')
        self.assertEqual(t.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        left.final.old.snapshot.revision+=1
        self.assertEqual(t.advance().status,'UNKNOWN_VERSION')
        refresh2,cmp2,left2,*_=self.fixture()
        task=self.task(refresh2,'left')
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        left2.first.recipient.new.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        self.assertEqual(task.advance().status,'WALL_OBSERVATION')

    def test_selected_route_declaration_substitution_rejected(self):
        refresh,cmp,left,right,*_=self.fixture()
        t=self.task(refresh,'left')
        left.old_map[(1,2,0)]=(2,2,2)
        self.assertEqual(t.advance().status,'ROUTE_DECLARATION_CHANGED')

    def test_neighbor_route_declaration_change_does_not_supply_evidence(self):
        refresh,cmp,left,right,*_=self.fixture()
        t=self.task(refresh,'left')
        spies=self.spies(left,right)
        right.old_map[(0,2,2)]=(2,2,2)
        self.assertEqual(t.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(spies,{'left':2,'right':0})

    def test_comparison_route_swap_rejected_even_if_matching_label(self):
        refresh,cmp,left,right,*_=self.fixture()
        t=self.task(refresh,'left')
        cmp.left=right
        self.assertEqual(t.advance().status,'ROUTE_DECLARATION_CHANGED')

    def test_invalid_input_causes_no_replay(self):
        refresh,cmp,left,right,*_=self.fixture()
        spies=self.spies(left,right)
        for bad in ({'route':'middle','route_fingerprint':cmp.expected[0],
                     'required_edges':[{'state':[1,0,0],'action':'B'}]},
                    {'route':'left','route_fingerprint':'0'*64,
                     'required_edges':[{'state':[1,0,0],'action':'B'}]},
                    {'route':'left','route_fingerprint':cmp.expected[0]},
                    {'route':'left','route_fingerprint':cmp.expected[0],
                     'required_edges':[{'state':[1,0,0],'action':'C'}]},
                    {'route':'left','route_fingerprint':cmp.expected[0],
                     'required_edges':[{'state':[1,0,0],'action':'B'}],
                     'unrecognized':1}):
            r=RouteBoundTask(refresh,bad).advance()
            self.assertEqual(r.status,'INVALID_TASK')
        self.assertEqual(spies,{'left':0,'right':0})

    def test_normalized_input_is_immutable_after_construction(self):
        refresh,*_=self.fixture()
        d={'route':'right','route_fingerprint':refresh.comparison.expected[1],
           'required_edges':[{'state':[0,1,2],'action':'B'}]}
        t=RouteBoundTask(refresh,d)
        d['required_edges'][0]['state'][0]=2
        d['route']='left'
        self.assertEqual(t.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')

    def test_source_change_during_two_pass_replay_cannot_finish(self):
        refresh,cmp,left,right,*_=self.fixture()
        task=self.task(refresh,'left')
        original=left.advance
        calls={'n':0}
        def moving():
            result=original()
            calls['n']+=1
            if calls['n']==1:
                left.final.old.snapshot.revision+=1
            return result
        left.advance=moving
        report=task.advance()
        self.assertEqual(report.status,'SOURCE_MOVED_DURING_AUDIT')
        self.assertEqual(calls['n'],2)
        self.assertFalse(report.obligations)

    def test_prior_selective_refresh_does_not_become_current_proof(self):
        refresh,cmp,left,right,middle,reg,_,pin=self.fixture()
        task=self.task(refresh,'left')
        reg.revoke(pin.token)
        partial=refresh.advance()
        self.assertEqual(partial.status,'COMPARISON_WITHDRAWN')
        self.assertEqual(partial.skipped,('left',))
        result=task.advance()
        self.assertEqual(result.status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(result.historical_comparison.status,'ROUTE_COMPOSED_MAP_CONFLICT')

    def test_source_revocation_after_completion_is_not_cached_success(self):
        refresh,cmp,left,right,*_=self.fixture()
        task=self.task(refresh,'left')
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')
        left.first.donor.registry.revoke(left.first.donor._base._tokens[0])
        result=task.advance()
        self.assertEqual(result.status,'OWNER_PIN_UNPROVED')
        self.assertFalse(result.obligations)

    def test_owner_head_advances_but_original_pinned_view_remains_valid(self):
        from ab_chatbot_discovered_correspondence import DOMAIN
        from ab_chatbot_stability_witness import TransportedLaw
        refresh,cmp,left,right,*_=self.fixture()
        t=self.task(refresh,'right')
        right.first.recipient.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        self.assertEqual(t.advance().status,'TASK_COMPLETED_ON_SELECTED_ROUTE')

if __name__=='__main__':unittest.main()
