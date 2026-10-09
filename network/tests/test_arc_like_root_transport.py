import unittest
from itertools import product
from collections import Counter
from work.arc_like_maze.root_transport import *
from work.arc_like_maze.root_transport import (
    MarkedWorld, marked_map, verify_marked_pair, transported_marked_worlds,
    compose_witness, invert_witness,
)

class TransportTests(unittest.TestCase):
    def test_specific_root_reset_break(self):
        p=Process.repeat(ZERO,(0,0,1));q=Process.repeat(ZERO,(0,1,0))
        original=find(p,q,1)
        self.assertEqual(original.status,'ALIGNED')
        shifted_fixed=find(p.shift(1),q.shift(1),1)
        self.assertEqual(shifted_fixed.status,'OPEN')
        transported=transport(p,q,original,1)
        self.assertEqual((original.scale(0),transported.incoming),(2,2))
        self.assertEqual(transported.status,'ALIGNED')
        self.assertTrue(verify(p.shift(1),q.shift(1),transported))

    def test_incoming_is_a_boundary_datum_not_ordinary_rooted_conjugacy(self):
        p=Process.repeat(ZERO,(0,0,1)).shift(1)
        q=Process.repeat(ZERO,(0,1,0)).shift(1)
        self.assertEqual(find(p,q,1).status,'OPEN')
        self.assertEqual(find(p,q,2).status,'ALIGNED')

    def test_shift_transport_of_underdetermined_zero_rules(self):
        p=Process.repeat(ZERO,(0,0,1));q=Process.repeat(ZERO,(0,1,0))
        witness=find(p,q)
        for turns in range(1,16):
            result=transport(p,q,witness,turns)
            self.assertEqual(result.status,'ALIGNED')
            self.assertTrue(verify(p.shift(turns),q.shift(turns),result))

    def test_all_order_two_equivalences_transport_and_shift_descends_to_free_boundary_quotient(self):
        streams,_=classify()
        aligned_pairs=0
        for i,p in enumerate(streams):
            for q in streams[i:]:
                for incoming in (1,2):
                    w=find(p,q,incoming)
                    if w.status=='ALIGNED':
                        aligned_pairs+=1
                        for turn in range(1,4):
                            result=transport(p,q,w,turn)
                            self.assertEqual(result.status,'ALIGNED')
        self.assertEqual(aligned_pairs,276)

    def test_free_boundary_is_still_an_equivalence_relation_for_81_templates(self):
        streams,groups=classify(mark_free=True)
        index={p:i for i,g in enumerate(groups) for p in g}
        for a in streams:
            for b in streams:
                same=any(find(a,b,mark).status=='ALIGNED' for mark in (1,2))
                self.assertEqual(same,index[a]==index[b])
                self.assertEqual(same,any(find(b,a,mark).status=='ALIGNED' for mark in (1,2)))
                if same:self.assertEqual(index[a.shift(1)],index[b.shift(1)])
        sizes=Counter(map(len,groups))
        self.assertEqual(len(groups),23)
        self.assertEqual(sorted(sizes.items()),[(1,1),(2,4),(4,18)])

    def test_additive_rule_is_not_restored_by_boundary_freedom(self):
        a=Process.repeat(IDENTITY);b=Process.repeat(NEGATIVE)
        self.assertEqual(find(a,b).status,'ALIGNED')
        def add_one(x):return Process(x.stem,tuple(tuple((v+d)%3 for v,d in zip(r,IDENTITY)) for r in x.period))
        qa,qb=add_one(a),add_one(b)
        for mark in (1,2):self.assertEqual(find(qa,qb,mark).status,'OPEN')

    def test_long_hidden_break_cannot_be_resolved_by_altering_boundary(self):
        p=Process.repeat(IDENTITY)
        q=Process((IDENTITY,)*75,((0,1,1),))
        for mark in (1,2):
            w=find(p,q,mark)
            self.assertEqual(w.status,'OPEN')
            self.assertGreaterEqual(w.first_failure_depth,78)

    def test_mark_compose_and_inverse_from_witness_sequence(self):
        p=Process.repeat(ZERO,(0,0,1));q=Process.repeat(ZERO,(0,1,0))
        first=find(p,q,1);back=find(q,p,1)
        self.assertEqual((first.status,back.status),('ALIGNED','ALIGNED'))
        for i in range(100):self.assertEqual(first.scale(i)*back.scale(i)%3,1)
        transported=transport(p,q,first,1)
        self.assertEqual(transported.incoming,first.scale(0))

    def test_marked_A_B_action_restores_full_state_alignment_after_shift(self):
        p=Process.repeat(ZERO,(0,0,1));q=Process.repeat(ZERO,(0,1,0))
        original=find(p,q)
        before=(MarkedWorld(p,1),MarkedWorld(q,1))
        for depth in range(3,8):
            self.assertTrue(verify_marked_pair(*before,original,depth))
        src,tgt,witness=transported_marked_worlds(p,q,original,1)
        self.assertEqual((src.gain,tgt.gain,witness.incoming),(1,2,2))
        for depth in range(3,8):
            self.assertTrue(verify_marked_pair(src,tgt,witness,depth))
        # If target root gain is incorrectly reset to 1, the conjugacy fails.
        self.assertFalse(verify_marked_pair(src,MarkedWorld(tgt.process,1),witness,4))

    def test_marked_transport_after_many_shifts(self):
        p=Process.repeat(ZERO,(0,0,1));q=Process.repeat(ZERO,(0,1,0))
        original=find(p,q)
        for turns in range(1,13):
            src,tgt,w=transported_marked_worlds(p,q,original,turns)
            for depth in range(3,7):
                self.assertTrue(verify_marked_pair(src,tgt,w,depth))

    def test_quotient_shift_orbit_has_five_fixed_classes_and_nine_pairs(self):
        streams,groups=classify(mark_free=True)
        index={p:i for i,g in enumerate(groups) for p in g}
        permutation={i:index[g[0].shift(1)] for i,g in enumerate(groups)}
        self.assertEqual(sum(i==j for i,j in permutation.items()),5)
        self.assertEqual((len(groups)-5)//2,9)
        self.assertTrue(all(permutation[permutation[i]]==i for i in permutation))

    def test_marked_alignments_form_a_composition_groupoid(self):
        p=Process.repeat(ZERO,(0,0,1));q=Process.repeat(ZERO,(0,1,0))
        a=find(p,q);b=invert_witness(p,q,a)
        self.assertTrue(verify(q,p,b))
        identity=compose_witness(p,q,p,a,b)
        self.assertEqual(identity.incoming,1)
        for i in range(100):self.assertEqual(identity.scale(i),1)
        for depth in range(3,8):
            for state in product(range(3),repeat=depth):
                one=marked_map(state,a)
                self.assertEqual(marked_map(one,b),marked_map(state,identity))

    def test_unverified_witness_is_never_transportable(self):
        p=Process.repeat(IDENTITY);q=Process.repeat(NEGATIVE)
        with self.assertRaises(ValueError):
            transport(p,q,Witness('ALIGNED',1,(),(1,)),1)

    def test_reject_invalid_root(self):
        with self.assertRaises(ValueError):find(Process.repeat(IDENTITY),Process.repeat(IDENTITY),0)

if __name__=='__main__':unittest.main(verbosity=2)
