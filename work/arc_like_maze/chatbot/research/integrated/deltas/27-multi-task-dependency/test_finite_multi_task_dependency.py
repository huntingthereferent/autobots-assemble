import unittest
from finite_multi_task_dependency import plan

class FiniteMultiTaskDependencyTests(unittest.TestCase):
    def setUp(self):
        self.dep={'left_a':('donor','left_middle','final'),
                  'left_b':('donor','left_middle','final'),
                  'right':('donor','right_middle','final'),
                  'other':('different_donor','different_middle','different_final')}
    def test_left_change(self):
        r=plan(self.dep,('left_middle',))
        self.assertEqual(r.replay,('left_a','left_b'))
        self.assertEqual(r.cached,('right','other'))
    def test_right_change(self):
        self.assertEqual(plan(self.dep,('right_middle',)).replay,('right',))
    def test_shared_final_change(self):
        self.assertEqual(plan(self.dep,('final',)).replay,('left_a','left_b','right'))
    def test_unrelated_change(self):
        self.assertEqual(plan(self.dep,('different_middle',)).replay,('other',))
    def test_multiple_sources_deduplicated(self):
        r=plan(self.dep,('left_middle','final','different_middle'))
        self.assertEqual(len(r.replay),4)
        self.assertEqual(r.impact[0][1],('left_middle','final'))
    def test_force_only_one(self):
        r=plan(self.dep,(),force=('left_a',))
        self.assertEqual(r.replay,('left_a',))
        self.assertTrue(all(label!='FRESH_PROOF' for _,label in r.outcomes))
    def test_no_changes_is_only_cache(self):
        r=plan(self.dep,())
        self.assertFalse(r.replay)
        self.assertEqual(r.cached,tuple(self.dep))
    def test_invalid_declaration(self):
        for deps,changes,force in (({'one':('x',)},(),()),
            (self.dep,('nonexistent',),()),
            (self.dep,('final','final'),()),
            (self.dep,(),('bad',)),
            (self.dep,(),('left_a','left_a')),
            (self.dep,['donor'],())):
            with self.assertRaises(ValueError):plan(deps,changes,force=force)

if __name__=='__main__':unittest.main()
