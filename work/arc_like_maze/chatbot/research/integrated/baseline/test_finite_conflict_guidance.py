"""Finite mathematical oracle checks, independent of the integrated chatbot."""
import unittest
from finite_goal_priority import Law
from finite_conflict_guidance import extend,choose_alternative

FIRST=('AAAB','BBBB','BAABA','ABAABB')
SECOND=('AAAB','ABBAA','BAABA')

class FiniteGuidanceWitness(unittest.TestCase):
    def test_specific_rejected_edge_is_admitted_under_alternate_pairing(self):
        old,new=Law((0,0,1)),Law((1,0,1))
        first,second,match=choose_alternative(old,new,FIRST,(SECOND,))
        self.assertEqual((len(first.mapping),len(first.admitted)),(27,41))
        self.assertEqual((len(second.mapping),len(second.admitted)),(24,40))
        self.assertIsNotNone(match)
        r,e=match
        self.assertEqual((r.source,r.action),e[:2])
        self.assertEqual(r.target,e[2])
        self.assertNotEqual(r.assigned_target,r.new_target)
        self.assertEqual(e[4],r.new_target)
        self.assertNotEqual(r.old_equal,r.new_equal)
        self.assertEqual(r.old_equal,old.follow(r.left_word)==old.follow(r.right_word))
        self.assertEqual(r.new_equal,new.follow(r.left_word)==new.follow(r.right_word))

    def test_identical_laws_admit_all_edges(self):
        law=Law((0,0,1))
        r=extend(law,law,('ABAA',))
        self.assertEqual((len(r.mapping),len(r.admitted),len(r.rejected)),(27,54,0))

    def test_no_conflict_no_repair_label(self):
        law=Law((0,0,1))
        first,other,match=choose_alternative(law,law,('ABAA',),(('B',),))
        self.assertIsNone(other)
        self.assertIsNone(match)

    def test_counterexamples_replay_across_two_law_pairs(self):
        for phi in ((1,0,1),(0,0,0)):
            old,new=Law((0,0,1)),Law(phi)
            record=extend(old,new,FIRST) if phi==(1,0,1) else extend(old,new,('ABAA','ABBABA'))
            forward=dict(record.mapping)
            self.assertEqual(len(forward),len(set(forward.values())))
            for s,a,t,ns,nt in record.admitted:
                self.assertEqual((old.step(s,a),new.step(ns,a)),(t,nt))
                self.assertEqual((forward[s],forward[t]),(ns,nt))
            for w in record.rejected:
                self.assertNotEqual(w.old_equal,w.new_equal)
                self.assertEqual(w.old_equal,old.follow(w.left_word)==old.follow(w.right_word))
                self.assertEqual(w.new_equal,new.follow(w.left_word)==new.follow(w.right_word))

if __name__=='__main__':unittest.main()
