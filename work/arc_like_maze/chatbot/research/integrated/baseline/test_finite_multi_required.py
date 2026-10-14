import unittest
from finite_goal_priority import ROOT,Law
from finite_multi_required import CANDIDATES,inspect_all,classify

class FiniteMultiRequiredTests(unittest.TestCase):
    def setUp(self):
        self.old=Law((0,0,1));self.new=Law((0,0,0))

    def test_two_replayed_requirement_sets(self):
        a,b=classify(self.old,self.new,CANDIDATES,((ROOT,'B'),((0,1,0),'B')))
        self.assertEqual((len(a),len(b)),(9,2))
        a,b=classify(self.old,self.new,CANDIDATES,((ROOT,'B'),((1,2,0),'B')))
        self.assertEqual((len(a),len(b),sum(len(c) for _,c in b)),(7,4,4))
        self.assertEqual({(s,a) for _,certs in b for s,a,_,_ in certs},
                         {(ROOT,'B'),((1,2,0),'B')})

    def test_independent_collision_replay(self):
        req=((ROOT,'B'),((1,2,0),'B'))
        good,bad=classify(self.old,self.new,CANDIDATES,req)
        for words,conflicts in bad:
            from finite_required_edge_guard import seed_map
            forward=seed_map(self.old,self.new,words)
            backward={y:x for x,y in forward.items()}
            for source,action,status,cert in conflicts:
                self.assertEqual(status,'CONTRADICTED')
                cause,s,a,t,ns,nt,assigned,preimage=cert
                self.assertEqual((s,a),(source,action))
                self.assertEqual(t,self.old.step(s,a))
                self.assertEqual(nt,self.new.step(ns,a))
                self.assertTrue(t in forward and assigned!=nt or
                                nt in backward and preimage!=t)

    def test_no_inference_or_global_exclusion(self):
        a,b=classify(self.old,self.new,CANDIDATES,((ROOT,'B'),))
        self.assertEqual((len(a),len(b)),(9,2))
        a,b=classify(self.old,self.new,CANDIDATES,(((1,2,0),'B'),))
        self.assertEqual((len(a),len(b)),(9,2))
        a,b=classify(self.old,self.old,CANDIDATES,((ROOT,'B'),((1,2,0),'B')))
        self.assertEqual((len(a),len(b)),(11,0))

    def test_bad_requirements_rejected(self):
        for req in ((),((ROOT,'B'),(ROOT,'B'))):
            with self.assertRaises(ValueError):inspect_all(self.old,self.new,CANDIDATES[0],req)

if __name__=='__main__':unittest.main()
