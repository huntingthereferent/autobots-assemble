import unittest
from finite_goal_priority import Law
from finite_cross_pin_relation import compare,path

class CrossPinFiniteReferenceTests(unittest.TestCase):
    def test_one_preserved_and_one_broken_relation(self):
        checks=compare(Law((0,0,0)),Law((0,1,2)),0,1,(('','AAA'),('BA','ABB')))
        self.assertEqual([c.status for c in checks],['EQUALITY_PRESERVED','RELATION_CHANGED'])
        self.assertEqual([(c.old_equal,c.new_equal) for c in checks],[(True,True),(True,False)])
    def test_histories_have_independent_revision_labels(self):
        check=compare(Law((0,0,0)),Law((0,1,2)),0,1,(('BA','ABB'),))[0]
        self.assertEqual({p.revision for p in check.old_histories},{0})
        self.assertEqual({p.revision for p in check.new_histories},{1})
        self.assertNotEqual(check.old_histories[1].states,check.new_histories[1].states)
    def test_no_universal_conjugacy_claim(self):
        cases=compare(Law((0,0,0)),Law((0,1,2)),0,1,(('','AAA'),))
        self.assertEqual(cases[0].status,'EQUALITY_PRESERVED')
        self.assertEqual(len(cases),1)
    def test_same_laws_preserve_declared_relation(self):
        checks=compare(Law((0,1,2)),Law((0,1,2)),0,1,(('BA','ABB'),))
        self.assertTrue(checks[0].old_equal==checks[0].new_equal)
    def test_bounded_input(self):
        a=Law((0,0,0))
        for args in ((0,0, (('','AAA'),)),(0,1,()),(0,1,(('BA','BA'),)),(0,1,(('B','C'),))):
            with self.assertRaises(ValueError):compare(a,a,*args)
        with self.assertRaises(ValueError):path(a,0,'BAA'+ 'B'*13)
if __name__=='__main__':unittest.main()
