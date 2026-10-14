import unittest
from finite_route_refresh_dependency import select_routes

B={'donor':'d0','left_middle':'l0','right_middle':'r0','final':'f0'}

class SelectiveFiniteTests(unittest.TestCase):
    def test_no_change_is_cached_not_proof(self):
        x=select_routes(B,B)
        self.assertEqual(x.affected,())
        self.assertEqual(x.skipped,('left','right'))
        self.assertFalse(x.comparison_usable)
    def test_left_middle_selects_only_left(self):
        x=select_routes(B,dict(B,left_middle='l1'))
        self.assertEqual((x.affected,x.skipped),(('left',),('right',)))
    def test_right_middle_selects_only_right(self):
        x=select_routes(B,dict(B,right_middle='r1'))
        self.assertEqual((x.affected,x.skipped),(('right',),('left',)))
    def test_shared_dependency_selects_both(self):
        for dep in ('donor','final'):
            x=select_routes(B,dict(B,**{dep:'new'}))
            self.assertEqual(x.affected,('left','right'))
    def test_declaration_mutation_is_conservative(self):
        self.assertEqual(select_routes(B,B,changed_declaration=True).affected,('left','right'))
    def test_forced_route_still_not_full_comparison(self):
        x=select_routes(B,B,force=('left',))
        self.assertEqual(x.affected,('left',))
        self.assertFalse(x.comparison_usable)
    def test_multiple_middle_changes_both(self):
        x=select_routes(B,dict(B,left_middle='l1',right_middle='r1'))
        self.assertEqual(x.affected,('left','right'))
    def test_invalid_graph_and_force(self):
        for after in ({},dict(B,foreign=1)):
            with self.assertRaises(ValueError):select_routes(B,after)
        with self.assertRaises(ValueError):select_routes(B,B,force=('invalid',))

if __name__=='__main__':unittest.main()
