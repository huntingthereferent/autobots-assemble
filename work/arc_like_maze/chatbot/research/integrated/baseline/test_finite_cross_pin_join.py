import unittest
from finite_goal_priority import Law
from finite_cross_pin_join import join

class FiniteCrossPinJoinTests(unittest.TestCase):
    def test_partial_union_does_not_add_unwitnessed_edges(self):
        r=join(Law((0,0,0)),Law((0,1,2)),('A','BAA'))
        self.assertEqual((r.status,len(r.state_pairs),len(r.admitted_edges)),
                         ('JOINT_PARTIAL_CORRESPONDENCE_WITNESSED',5,4))
        self.assertLess(len(r.admitted_edges),2*len(r.state_pairs))
    def test_source_collision_has_word_equality_counterexample(self):
        old,new=Law((0,0,0)),Law((0,1,2))
        r=join(old,new,('A','BAB'))
        w1,w2,cause,oe,ne,old_equal,new_equal=r.contradiction
        self.assertEqual((w1,w2,cause),('A','BAB','SOURCE_STATE_CONFLICT'))
        self.assertEqual((old.follow(w1)==old.follow(w2),new.follow(w1)==new.follow(w2)),
                         (old_equal,new_equal))
        self.assertNotEqual(old_equal,new_equal)
    def test_target_collision_has_reverse_equality_counterexample(self):
        old,new=Law((0,0,1)),Law((0,0,0))
        r=join(old,new,('B','ABBABA'))
        self.assertEqual(r.contradiction[2],'TARGET_STATE_CONFLICT')
        self.assertEqual(r.contradiction[-2:],(False,True))
    def test_several_compatible_words_preserve_only_seed_union(self):
        old,new=Law((0,0,1)),Law((0,0,0))
        r=join(old,new,('ABAA','ABBABA','A'))
        self.assertEqual(r.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        self.assertEqual(len(r.state_pairs),8)
        f=dict(r.state_pairs)
        for s,a,t,ns,nt in r.admitted_edges:
            self.assertEqual((f[s],f[t]),(ns,nt))
            self.assertEqual((old.step(s,a),new.step(ns,a)),(t,nt))
    def test_identity_laws_and_invalid_input(self):
        a=Law((0,0,1))
        r=join(a,a,('ABAA','ABBABA'))
        self.assertEqual(r.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        self.assertTrue(all(s==t for s,t in r.state_pairs))
        for words in (('A',),('A','A'),('A','C'),('','B')):
            with self.assertRaises(ValueError):join(a,a,words)

if __name__=='__main__':unittest.main()
