import unittest
from finite_goal_priority import Law
from finite_explicit_join_transfer import transfer

A,B=Law((0,0,0)),Law((0,1,2))
P=('A','BAA');D=('B','ABB')
FIRST=((1,0,0),'B')
SECOND=((1,2,0),'B')

class FiniteTransferOracleTests(unittest.TestCase):
    def test_valid_labeled_edge_from_independently_witnessed_path(self):
        r=transfer(A,B,P,D,(FIRST,))
        self.assertEqual(r.status,'EXPLICIT_TRANSFER_WITNESSED')
        self.assertEqual((len(r.pairs),len(r.edges)),(6,5))
        self.assertIn(((1,0,0),'B',(1,2,0),(1,0,0),(1,2,0)),r.edges)
    def test_incompatible_extra_edge_not_admitted(self):
        r=transfer(A,B,P,D,(FIRST,SECOND))
        self.assertEqual(r.status,'INCOMPATIBLE_EDGE')
        self.assertEqual((r.pairs,r.edges),((),()))
        self.assertEqual(r.cause[1:4],((1,1,0),(1,1,2),(1,1,0)))
    def test_selected_edge_must_have_rooted_prefix(self):
        r=transfer(A,B,P,D,(SECOND,))
        self.assertEqual(r.status,'PREFIX_UNWITNESSED')
    def test_unwitnessed_edge_not_transferred_from_known_law(self):
        r=transfer(A,B,P,D,((((1,1,0),'B')),))
        self.assertEqual(r.status,'EDGE_NOT_WITNESSED')
    def test_unchanged_recipient_and_donor_can_be_replayed_again(self):
        x=transfer(A,B,P,D,(FIRST,))
        y=transfer(A,B,P,D,(FIRST,))
        self.assertEqual(x,y)
        self.assertNotIn(((1,2,0),'B',(1,1,0),(1,2,0),(1,1,2)),x.edges)
if __name__=='__main__':unittest.main()
