"""Bounded law-level two-route reference; no owner-authentication claims."""
import unittest
from finite_goal_priority import Law
from finite_two_route_comparison import compare
from finite_cross_pin_join import join

D=(Law((0,0,1)),Law((1,0,1)))
M1=(Law((0,0,0)),Law((0,1,2)))
M2=(Law((1,1,0)),Law((1,1,1)))
F=(Law((2,0,0)),Law((2,2,1)))
AL=(
 (((1,0,0),(1,0,0)),((1,2,0),(1,2,0))),
 (((1,0,0),(1,0,0)),((1,2,1),(1,2,0))),
 (((1,0,0),(1,0,0)),((1,2,0),(1,2,2))),
 (((1,0,0),(1,0,0)),((1,2,0),(1,2,2))),
)
AR=(
 (((1,0,0),(0,1,1)),((1,2,0),(0,2,2))),
 (((1,0,0),(0,1,1)),((1,2,1),(0,2,2))),
 (((0,1,1),(0,1,2)),((0,2,2),(0,2,2))),
 (((0,1,1),(0,1,2)),((0,2,2),(0,2,1))),
)

def setup(**kwargs):
    req=dict(donor=D,middle_left=M1,middle_right=M2,final=F,
         donor_words=('AB','B'),middle_words_left=('A','BAA'),
         middle_words_right=('A','BAA'),final_words=('A','BAA'),
         selected=((1,0,0),'B'),maps_left=AL,maps_right=AR)
    req.update(kwargs)
    return req

class FiniteRouteTests(unittest.TestCase):
    def test_two_valid_chains_different_composed_images(self):
        r=compare(**setup())
        self.assertEqual(r.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual((r.left_status,r.right_status),('TWO_HOP_CHAIN_WITNESSED',)*2)
        self.assertEqual(len(r.disagreements),4)
        self.assertEqual(r.left_composed[3],((1,2,1),(1,2,2)))
        self.assertEqual(r.right_composed[3],((1,2,1),(0,2,1)))
    def test_independent_middle_with_identical_laws_may_agree(self):
        r=compare(**setup(middle_right=M1,maps_right=AL))
        self.assertEqual(r.status,'ROUTES_AGREE_ON_SELECTED_EDGE')
        self.assertFalse(r.disagreements)
    def test_wrong_last_mapping_fails_second_route_before_comparison(self):
        changed=list(AR);changed[3]=(
              ((0,1,1),(0,1,2)),((0,2,2),(0,2,2)))
        r=compare(**setup(maps_right=tuple(changed)))
        self.assertEqual(r.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertEqual(r.right_status,'SECOND_INTERTWINING_CONFLICT')
        self.assertFalse(r.disagreements)
    def test_missing_first_donor_witness_is_not_transported(self):
        r=compare(**setup(selected=((1,1,0),'A')))
        self.assertEqual(r.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertEqual(r.left_status,'FIRST_LINK_DONOR_EDGE_UNPROVED')
    def test_no_supplied_unobserved_edge_promoted(self):
        base=join(*F,('A','BAA'))
        r=compare(**setup())
        self.assertEqual((len(base.admitted_edges),len(r.left_final_edges),len(r.right_final_edges)),(4,5,5))
        self.assertNotIn(((1,0,0),'B',(1,2,2),(1,0,0),(1,2,2)),base.admitted_edges)
    def test_changed_final_law_breaks_at_least_one_route(self):
        r=compare(**setup(final=(F[0],Law((0,2,1)))))
        self.assertEqual(r.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertNotEqual((r.left_status,r.right_status),('TWO_HOP_CHAIN_WITNESSED',)*2)
    def test_requires_two_independently_declared_map_sets(self):
        with self.assertRaises(ValueError):compare(**setup(maps_right=AR[:2]))

if __name__=='__main__':unittest.main()
