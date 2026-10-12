"""Independent finite controls; not integration/CI status."""
import unittest
from finite_goal_priority import ROOT, Law
from finite_required_edge_guard import seed_map, preflight

CANDIDATES=(
    ('ABAA','ABBABA'),('ABAA','AAABB','BAAAB'),('ABAA','BAAAB'),
    ('AAABB','BAAAB'),('ABAA','AAABB'),('ABBABA',),
    ('BB','ABAA'),('AAABB',),('BAAAB',),('ABAA',),('BB',)
)

class FiniteGuardTests(unittest.TestCase):
    def test_only_two_specific_candidates_excluded(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        verdicts=[preflight(a,b,w,(ROOT,'B')) for w in CANDIDATES]
        self.assertEqual([i for i,v in enumerate(verdicts)
                          if v=='CONTRADICTED'],[0,5])
        self.assertEqual(verdicts.count('NOT_CONTRADICTED'),9)

    def test_target_image_collision_is_explicit(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        fwd=seed_map(a,b,CANDIDATES[0])
        original_target=a.step(ROOT,'B')
        mapped_target=b.step(fwd[ROOT],'B')
        self.assertNotIn(original_target,fwd)
        inverse={v:k for k,v in fwd.items()}
        self.assertIn(mapped_target,inverse)
        self.assertNotEqual(original_target,inverse[mapped_target])

    def test_other_pairing_is_not_globally_disqualified(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        self.assertEqual(preflight(a,b,CANDIDATES[1],(ROOT,'B')),'NOT_CONTRADICTED')
        self.assertEqual(preflight(a,a,CANDIDATES[0],(ROOT,'B')),'NOT_CONTRADICTED')

    def test_seed_incompatibility_is_detected(self):
        a,b=Law((0,0,1)),Law((0,0,0))
        with self.assertRaises(ValueError):
            seed_map(a,b,('B','ABBABA'))

if __name__=='__main__':
    unittest.main()
