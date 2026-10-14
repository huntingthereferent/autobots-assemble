"""Independent, complete-law four-source checks for selected intertwining square."""
import unittest
from finite_goal_priority import Law
from finite_cross_scope_transport import transport

R_OLD,R_NEW=Law((0,0,0)),Law((0,1,2))
D_OLD,D_NEW=Law((0,0,1)),Law((1,0,1))
OW=(((1,0,0),(1,0,0)),((1,2,0),(1,2,0)))
NW=(((1,0,0),(1,0,0)),((1,2,1),(1,2,0)))
RECIPIENT=('A','BAA')
DONOR=('AB','B')
KEY=((1,0,0),'B')

def run(old_map=OW,new_map=NW,r_old=R_OLD,r_new=R_NEW,selected=KEY):
    return transport(r_old,r_new,D_OLD,D_NEW,RECIPIENT,DONOR,
                     selected,old_map,new_map)

class IndependentSquareTests(unittest.TestCase):
    def test_four_distinct_laws_commuting_selected_edge(self):
        r=run()
        self.assertEqual(r.status,'CROSS_SCOPE_SQUARE_WITNESSED')
        self.assertEqual((len(r.state_pairs),len(r.admitted_edges)),(6,5))
        self.assertEqual(r.square[0],KEY)
        self.assertEqual(r.square[2][1],((1,0,0),(1,2,0)))
        self.assertNotEqual(D_NEW.phi,R_NEW.phi)
    def test_nontrivial_new_side_map_is_required(self):
        # Donor new endpoint (1,2,1) differs from recipient new endpoint (1,2,0).
        self.assertEqual(NW[-1],((1,2,1),(1,2,0)))
        bad=(((1,0,0),(1,0,0)),((1,2,1),(1,2,1)))
        out=run(new_map=bad)
        self.assertEqual(out.status,'INTERTWINING_CONFLICT')
        self.assertIsNotNone(out.obstruction)
        self.assertEqual((out.state_pairs,out.admitted_edges),((),()))
    def test_witness_donor_edge_not_computed_from_law_alone(self):
        x=run(selected=((1,1,0),'A'))
        self.assertEqual(x.status,'DONOR_EDGE_UNPROVED')
    def test_map_cannot_sneak_unrelated_state_claims(self):
        extra=OW+(((0,2,2),(0,2,2)),)
        self.assertEqual(run(old_map=extra).status,'MAPPING_INCOMPLETE')
        self.assertEqual(run(old_map=OW[:1]).status,'MAPPING_INCOMPLETE')
    def test_recipient_law_change_detected_independently(self):
        r=run(r_new=Law((1,0,1)))
        self.assertEqual(r.status,'INTERTWINING_CONFLICT')
    def test_original_recipient_partial_witness_not_mutated(self):
        from finite_cross_pin_join import join
        orig=join(R_OLD,R_NEW,RECIPIENT)
        out=run()
        self.assertEqual((len(orig.state_pairs),len(orig.admitted_edges)),(5,4))
        self.assertNotIn(((1,0,0),'B',(1,2,0),(1,0,0),(1,2,0)),orig.admitted_edges)
        self.assertIn(((1,0,0),'B',(1,2,0),(1,0,0),(1,2,0)),out.admitted_edges)

if __name__=='__main__':unittest.main()
