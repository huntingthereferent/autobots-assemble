import unittest
from finite_selective_dependency import plan

D={'route_comparison_1':('donor','middle_left','middle_right','final'),
   'route_comparison_2':('donor','middle_other','final'),
   'independent':('outside_old','outside_new')}
S={k:'WITNESSED' for k in D}

class DependencyPlanningTests(unittest.TestCase):
    def test_single_middle_change_replays_one_certificate(self):
        p=plan(D,('middle_left',),S)
        self.assertEqual(p.audited,('route_comparison_1',))
        self.assertEqual(p.skipped,('route_comparison_2','independent'))
    def test_shared_donor_change_replays_both_dependent_certificates(self):
        p=plan(D,('donor',),S)
        self.assertEqual(p.audited,('route_comparison_1','route_comparison_2'))
        self.assertEqual(p.skipped,('independent',))
    def test_multiple_changes_select_exact_union_of_dependencies(self):
        p=plan(D,('middle_left','outside_new'),S)
        self.assertEqual(p.audited,('route_comparison_1','independent'))
    def test_no_changes_means_cached_not_verified(self):
        p=plan(D,(),S)
        self.assertEqual(p.audited,())
        self.assertTrue(all(status=='CACHED_NOT_REPLAYED' for _,status in p.candidate_status))
    def test_force_audit_possible_even_with_no_changes(self):
        p=plan(D,(),S,force=('independent',))
        self.assertEqual(p.audited,('independent',))
    def test_invalid_source_or_graph_rejected(self):
        with self.assertRaises(ValueError):plan(D,('invented',),S)
        with self.assertRaises(ValueError):plan({'one':('x',)},(),{'one':'x'})
        with self.assertRaises(ValueError):plan(D,('donor','donor'),S)

if __name__=='__main__':unittest.main()
