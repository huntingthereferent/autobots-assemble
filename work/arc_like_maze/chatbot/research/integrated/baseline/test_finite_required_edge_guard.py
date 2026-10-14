import unittest
from finite_goal_priority import ROOT, Law
from finite_required_edge_guard import seed_map, preflight

CANDIDATES=(('ABAA','ABBABA'),('ABAA','AAABB','BAAAB'),('ABAA','BAAAB'),
            ('AAABB','BAAAB'),('ABAA','AAABB'),('ABBABA',),
            ('BB','ABAA'),('AAABB',),('BAAAB',),('ABAA',),('BB',))

class GuardFiniteControls(unittest.TestCase):
    def test_two_candidate_only_exclusions(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        verdicts=[preflight(a,b,w,(ROOT,'B')) for w in CANDIDATES]
        self.assertEqual([i for i,v in enumerate(verdicts) if v=='CONTRADICTED'],[0,5])
        self.assertEqual(verdicts.count('NOT_CONTRADICTED'),9)

    def test_separating_target_collision_witness(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        fwd=seed_map(a,b,CANDIDATES[0]);target=a.step(ROOT,'B')
        self.assertNotIn(target,fwd)
        new_target=b.step(fwd[ROOT],'B')
        self.assertIn(new_target,fwd.values())
        incompatible_source={v:k for k,v in fwd.items()}[new_target]
        self.assertNotEqual(target,incompatible_source)
        self.assertEqual(preflight(a,b,CANDIDATES[0],(ROOT,'B')),'CONTRADICTED')

    def test_no_global_edge_forbiddance(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        self.assertEqual(preflight(a,b,CANDIDATES[1],(ROOT,'B')),'NOT_CONTRADICTED')
        self.assertEqual(preflight(a,a,CANDIDATES[0],(ROOT,'B')),'NOT_CONTRADICTED')

    def test_inconsistent_seed_rejected_before_inspection(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        with self.assertRaises(ValueError):seed_map(a,b,('B','ABBABA'))

if __name__=='__main__':unittest.main()
