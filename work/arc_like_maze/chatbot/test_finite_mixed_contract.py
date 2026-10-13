"""Independent finite replay against complete declared laws."""
import unittest
from finite_goal_priority import ROOT,Law
from finite_mixed_contract import inspect,verdict

OLD,NEW=Law((0,0,1)),Law((0,0,0))
COMMON={'edges':((ROOT,'A'),),
        'paths':(('ABAA',(0,2,0),(0,2,0)),('ABBABA',(0,1,1),(0,1,0))),
        'destinations':(((0,1,1),(0,1,0)),)}

class TypedFiniteOracleTests(unittest.TestCase):
    def test_full_typed_conjunction_verified_in_one_pairing(self):
        result,witness,checks=verdict(OLD,NEW,('ABAA','ABBABA'),**COMMON)
        self.assertEqual(result,'ALL_REQUIRED_WITNESSED')
        self.assertEqual([t for t,_,_ in checks],['EDGE','DESTINATION','PATH','PATH'])
        self.assertTrue(all(c[2] for c in checks))
        self.assertEqual((len(witness.mapping),len(witness.admitted)),(9,13))

    def test_separate_successes_do_not_combine(self):
        r1,one,c1=verdict(OLD,NEW,('ABAA','ABBABA'),edges=((ROOT,'B'),),
            paths=(('ABBABA',(0,1,1),(0,1,0)),))
        r2,two,c2=verdict(OLD,NEW,('BB','ABAA'),edges=((ROOT,'B'),),
            paths=(('ABBABA',(0,1,1),(0,1,0)),))
        self.assertEqual((r1,r2),('REQUIREMENTS_UNPROVED','REQUIREMENTS_UNPROVED'))
        self.assertEqual(tuple(x[2] for x in c1),(False,True))
        self.assertEqual(tuple(x[2] for x in c2),(True,False))

    def test_destination_does_not_replace_missing_path(self):
        _,w,checks=verdict(OLD,NEW,('ABAA','ABBABA'),
                destinations=(((0,1,1),(0,1,0)),),
                paths=(('B',(0,1,0),(0,1,0)),))
        self.assertEqual(tuple(r[2] for r in checks),(True,False))

    def test_identical_law(self):
        r,w,checks=verdict(OLD,OLD,('ABAA','ABBABA'),
            edges=((ROOT,'B'),),paths=(('ABBABA',(0,1,1),(0,1,1)),),
            destinations=(((0,1,1),(0,1,1)),))
        self.assertEqual(r,'ALL_REQUIRED_WITNESSED')
        self.assertEqual((len(w.mapping),len(w.admitted)),(27,54))

    def test_owner_law_replay_of_every_retained_edge(self):
        for words in (('ABAA','ABBABA'),('BB','ABAA')):
            witness,_=inspect(OLD,NEW,words)
            f=dict(witness.mapping)
            for s,a,t,ns,nt in witness.admitted:
                self.assertEqual((OLD.step(s,a),NEW.step(ns,a)),(t,nt))
                self.assertEqual((f[s],f[t]),(ns,nt))

if __name__=='__main__':unittest.main()
