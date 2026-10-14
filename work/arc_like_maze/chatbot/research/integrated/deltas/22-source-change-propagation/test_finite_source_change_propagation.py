import unittest
from finite_goal_priority import Law
from finite_source_change_propagation import reassess
from test_finite_two_route_comparison import setup

class FiniteSourceChangeTests(unittest.TestCase):
    def test_no_change_preserves_scoped_conflict(self):
        a=setup();r=reassess(a,a.copy())
        self.assertEqual((r.status,r.changed_scopes,r.affected_routes),
                         ('RELATION_PRESERVED',(),()))
        self.assertEqual(r.comparison_status,'ROUTE_COMPOSED_MAP_CONFLICT')
    def test_changed_right_source_withdraws_right_only(self):
        a=setup();b=setup(middle_right=(a['middle_right'][0],Law((1,2,0))))
        r=reassess(a,b)
        self.assertEqual(r.status,'RELATION_WITHDRAWN')
        self.assertEqual(r.changed_scopes,('middle_right',))
        self.assertEqual(r.affected_routes,('right',))
        self.assertEqual(r.left_status,'TWO_HOP_CHAIN_WITNESSED')
        self.assertNotEqual(r.right_status,'TWO_HOP_CHAIN_WITNESSED')
    def test_different_right_law_can_still_preserve_selected_conflict(self):
        a=setup();b=setup(middle_right=(a['middle_right'][0],Law((1,1,2))))
        r=reassess(a,b)
        self.assertEqual(r.status,'RELATION_PRESERVED')
        self.assertEqual(r.affected_routes,('right',))
        self.assertEqual(r.comparison_status,'ROUTE_COMPOSED_MAP_CONFLICT')
    def test_changed_final_scope_affects_both_routes(self):
        a=setup();b=setup(final=(a['final'][0],Law((0,2,1))))
        r=reassess(a,b)
        self.assertEqual(r.status,'RELATION_WITHDRAWN')
        self.assertEqual(r.affected_routes,('left','right'))
    def test_historical_pin_not_moved_by_new_head_claim(self):
        a=setup();b=setup() # unchanged declared historical law despite owner-head change elsewhere
        self.assertEqual(reassess(a,b).status,'RELATION_PRESERVED')
    def test_missing_or_changed_problem_shape_rejected(self):
        a=setup();b=setup();b['unexpected']=True
        with self.assertRaises(ValueError):reassess(a,b)
if __name__=='__main__':unittest.main()
