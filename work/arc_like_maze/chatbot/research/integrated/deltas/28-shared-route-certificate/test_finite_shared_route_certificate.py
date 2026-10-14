import unittest
from dataclasses import replace
from finite_shared_route_certificate import evaluate, fixture, Task


class SharedFiniteTests(unittest.TestCase):
    def setUp(self):
        self.r,self.t,self.l,self.p=fixture()
    def run_case(self,**kw):
        return evaluate(self.r,self.t,self.l,self.p,self.p,**kw)
    def test_two_tasks_one_route(self):
        v=self.run_case(force=('left_a','left_b'))
        self.assertEqual(v.audited_routes,('left',))
        self.assertEqual(v.replayed_tasks,('left_a','left_b'))
        self.assertEqual([x for n,x in v.status][:2],
                         ['TASK_COMPLETED_ON_SELECTED_ROUTE']*2)
    def test_forced_one_leaves_sibling_cached(self):
        v=self.run_case(force=('left_a',))
        self.assertEqual(dict(v.status)['left_b'],'CACHED_NOT_REPLAYED')
    def test_idle_all_cached(self):
        v=self.run_case();self.assertEqual(v.audited_routes,())
        self.assertEqual(len(v.cached_tasks),3)
    def test_right_change_only_right(self):
        v=self.run_case(changed=('right_middle',))
        self.assertEqual(v.replayed_tasks,('right_a',))
    def test_shared_final_change_audits_two_routes(self):
        v=self.run_case(changed=('final',))
        self.assertEqual(v.audited_routes,('left','right'))
    def test_stale_pin_all_dependent_tasks_withdrawn(self):
        self.p['left_middle']='v2'
        v=self.run_case(changed=('left_middle',))
        self.assertEqual(dict(v.status)['left_a'],'SOURCE_PIN_UNPROVED')
        self.assertEqual(dict(v.status)['left_b'],'SOURCE_PIN_UNPROVED')
    def test_mid_audit_source_change_rejects_shared(self):
        after=dict(self.p);after['left_middle']='v2'
        v=evaluate(self.r,self.t,self.l,self.p,after,force=('left_a','left_b'))
        self.assertEqual([x for n,x in v.status][:2],['SOURCE_MOVED_DURING_AUDIT']*2)
    def test_task_fingerprint_mismatch_is_individual(self):
        self.t['left_b']=replace(self.t['left_b'],fingerprint='wrong')
        v=self.run_case(force=('left_a','left_b'))
        self.assertEqual(dict(v.status)['left_a'],'TASK_COMPLETED_ON_SELECTED_ROUTE')
        self.assertEqual(dict(v.status)['left_b'],'ROUTE_DECLARATION_CHANGED')
    def test_missing_edge_never_borrowed_from_right(self):
        self.t['left_b']=Task('left','left-pinned',(('r0','B'),))
        v=self.run_case(force=('left_a','left_b'))
        self.assertEqual(dict(v.status)['left_b'],'ROUTE_TASK_REQUIREMENTS_UNPROVED')
    def test_unproved_route_law_blocks_tasks(self):
        self.l['left']=(('s0','B'),)
        v=self.run_case(force=('left_a','left_b'))
        self.assertEqual(dict(v.status)['left_a'],'ROUTE_EDGE_UNPROVED')
    def test_bad_force_rejected(self):
        with self.assertRaises(ValueError):self.run_case(force=('left_a','left_a'))
    def test_bad_changed_rejected(self):
        with self.assertRaises(ValueError):self.run_case(changed=('unknown',))
    def test_empty_task_obligation_rejected(self):
        self.t['left_b']=Task('left','left-pinned',())
        with self.assertRaises(ValueError):self.run_case(force=('left_a',))
    def test_duplicated_route_pins_rejected(self):
        self.r['left']=replace(self.r['left'],pins=(('donor','v1'),('donor','v1')))
        with self.assertRaises(ValueError):self.run_case(force=('left_a',))

if __name__=='__main__':unittest.main()
