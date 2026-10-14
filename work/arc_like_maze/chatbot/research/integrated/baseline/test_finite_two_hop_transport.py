import unittest
from finite_goal_priority import Law
from finite_two_hop_transport import chain
from finite_cross_pin_join import join

D=(Law((0,0,1)),Law((1,0,1)))
M=(Law((0,0,0)),Law((0,1,2)))
F=(Law((2,0,0)),Law((2,2,1)))
OA=(((1,0,0),(1,0,0)),((1,2,0),(1,2,0)))
NA=(((1,0,0),(1,0,0)),((1,2,1),(1,2,0)))
OB=(((1,0,0),(1,0,0)),((1,2,0),(1,2,2)))
NB=OB

def calc(**kwargs):
    inputs={'donor':D,'intermediate':M,'final':F,'donor_words':('AB','B'),
      'middle_words':('A','BAA'),'final_words':('A','BAA'),
      'selected':((1,0,0),'B'),'first_old_map':OA,'first_new_map':NA,
      'second_old_map':OB,'second_new_map':NB}
    inputs.update(kwargs)
    return chain(**inputs)

class TwoHopFiniteTests(unittest.TestCase):
    def test_two_independent_squares(self):
        r=calc()
        self.assertEqual(r.status,'TWO_HOP_CHAIN_WITNESSED')
        self.assertEqual((len(r.links),len(r.state_pairs),len(r.admitted_edges)),(2,6,5))
        self.assertNotEqual(D[1].phi,M[1].phi)
        self.assertNotEqual(M[1].phi,F[1].phi)
    def test_wrong_second_map_rejected(self):
        bad=(((1,0,0),(1,0,0)),((1,2,0),(1,2,0)))
        self.assertEqual(calc(second_new_map=bad).status,'SECOND_INTERTWINING_CONFLICT')
        self.assertEqual(calc(second_new_map=bad).state_pairs,())
    def test_wrong_final_law_rejected(self):
        r=calc(final=(F[0],Law((0,2,1))))
        self.assertEqual(r.status,'SECOND_INTERTWINING_CONFLICT')
    def test_no_unwitnessed_donor_edge(self):
        r=calc(selected=((1,1,0),'A'))
        self.assertEqual(r.status,'FIRST_LINK_DONOR_EDGE_UNPROVED')
    def test_missing_maps_never_generalize(self):
        self.assertEqual(calc(second_old_map=OB[:1]).status,'SECOND_MAPPING_INCOMPLETE')
        self.assertEqual(calc(second_old_map=OB+(((2,2,2),(2,2,2)),)).status,
                         'SECOND_MAPPING_INCOMPLETE')
    def test_base_joins_unchanged(self):
        report=calc()
        before=join(*F,('A','BAA'))
        self.assertEqual((len(before.state_pairs),len(before.admitted_edges)),(5,4))
        self.assertNotIn(((1,0,0),'B',(1,2,2),(1,0,0),(1,2,2)),before.admitted_edges)
        self.assertIn(((1,0,0),'B',(1,2,2),(1,0,0),(1,2,2)),report.admitted_edges)
if __name__=='__main__':unittest.main()
