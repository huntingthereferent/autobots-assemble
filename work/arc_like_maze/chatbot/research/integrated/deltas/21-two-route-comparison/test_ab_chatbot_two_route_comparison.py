"""Two distinct middle owner scope pairs, shared donor and final source pair."""
import unittest
from ab_chatbot_two_route_comparison import TwoRouteComparison
from ab_chatbot_two_hop_transport import TwoHopTransport
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import current_digest
from test_ab_chatbot_cross_pin_comparison import CrossPinTests
from test_ab_chatbot_two_hop_transport import TwoHopTransportTests

class TwoRouteTests(unittest.TestCase):
    def fixture(self, same_middle=False):
        first,final,first_decl,*_=TwoHopTransportTests.fixture(self)
        route1=TwoHopTransport(first,final,first_decl)
        a=route1.advance()
        self.assertEqual(a.status,'TWO_HOP_CHAIN_WITNESSED')
        law=(0,0,0) if same_middle else (1,1,0)
        law_new=(0,1,2) if same_middle else (1,1,1)
        old,new,_,reg,pold,pnew=CrossPinTests.make(self,oldlaw=law,newlaw=law_new)
        middle2=CrossPinJoin(old,new,{'required_owner_pins':{'old':pold.token,'new':pnew.token},
                     'join_words':['A','BAA']},registry=reg)
        report=middle2.advance(max_new_edges=108)
        self.assertEqual(report.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        donor=first.donor
        if same_middle:
            mapold=[{'donor':[1,0,0],'recipient':[1,0,0]},
                    {'donor':[1,2,0],'recipient':[1,2,0]}]
            mapnew=[{'donor':[1,0,0],'recipient':[1,0,0]},
                    {'donor':[1,2,1],'recipient':[1,2,0]}]
            finalold=[{'donor':[1,0,0],'recipient':[1,0,0]},
                      {'donor':[1,2,0],'recipient':[1,2,2]}]
            finalnew=finalold.copy()
        else:
            mapold=[{'donor':[1,0,0],'recipient':[0,1,1]},
                    {'donor':[1,2,0],'recipient':[0,2,2]}]
            mapnew=[{'donor':[1,0,0],'recipient':[0,1,1]},
                    {'donor':[1,2,1],'recipient':[0,2,2]}]
            finalold=[{'donor':[0,1,1],'recipient':[0,1,2]},
                      {'donor':[0,2,2],'recipient':[0,2,2]}]
            finalnew=[{'donor':[0,1,1],'recipient':[0,1,2]},
                      {'donor':[0,2,2],'recipient':[0,2,1]}]
        declaration={'recipient_fingerprint':current_digest(middle2),
             'donor_fingerprint':current_digest(donor),
             'selected_donor_edge':{'state':[1,0,0],'action':'B'},
             'old_state_transport':mapold, 'new_state_transport':mapnew}
        second_first=CrossScopeIntertwiningTransfer(middle2,donor,declaration)
        second_first_report=second_first.advance()
        self.assertEqual(second_first_report.status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        route2=TwoHopTransport(second_first,final,{
             'first_link_fingerprint':second_first_report.derived_fingerprint,
             'final_join_fingerprint':current_digest(final),
             'old_state_transport':finalold,'new_state_transport':finalnew})
        b=route2.advance()
        self.assertEqual(b.status,'TWO_HOP_CHAIN_WITNESSED')
        compare=TwoRouteComparison(route1,route2,{
             'left_chain_fingerprint':a.fingerprint,
             'right_chain_fingerprint':b.fingerprint})
        return compare,route1,route2,middle2,reg,pold,pnew

    def test_independent_valid_routes_can_disagree_without_one_being_false(self):
        cmp,a,b,*_=self.fixture()
        report=cmp.advance()
        self.assertEqual(report.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual(len(report.left.links),2)
        self.assertEqual(len(report.right.links),2)
        self.assertEqual(report.donor_edge,((1,0,0),'B',(1,2,0),(1,0,0),(1,2,1)))
        self.assertEqual(report.left_composed[1],((1,2,0),(1,2,2)))
        self.assertEqual(report.right_composed[1],((1,2,0),(0,2,2)))
        self.assertEqual(report.left_composed[3],((1,2,1),(1,2,2)))
        self.assertEqual(report.right_composed[3],((1,2,1),(0,2,1)))
        self.assertEqual(len(report.disagreement),4)
        self.assertIsNotNone(report.left.fingerprint)
        self.assertIsNotNone(report.right.fingerprint)

    def test_two_distinct_middle_owners_may_agree_on_selected_edge(self):
        cmp,*_=self.fixture(same_middle=True)
        r=cmp.advance()
        self.assertEqual(r.status,'ROUTES_AGREE_ON_SELECTED_EDGE')
        self.assertEqual(r.disagreement,())
        self.assertNotEqual(r.left.fingerprint,r.right.fingerprint)

    def test_repeated_comparison_adds_no_new_observations(self):
        cmp,*_=self.fixture()
        first=cmp.advance();second=cmp.advance()
        self.assertEqual(first.observations_after,second.observations_after)
        self.assertEqual(second.observations_before,second.observations_after)

    def test_one_middle_pin_revoked_prevents_comparison(self):
        cmp,a,b,m,reg,po,pn=self.fixture()
        self.assertEqual(cmp.advance().status,'ROUTE_COMPOSED_MAP_CONFLICT')
        reg.revoke(pn.token)
        report=cmp.advance()
        self.assertEqual(report.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertNotEqual(report.right.status,'TWO_HOP_CHAIN_WITNESSED')
        self.assertEqual(report.left.status,'TWO_HOP_CHAIN_WITNESSED')

    def test_final_owner_tamper_stops_both_routes(self):
        cmp,a,b,*_=self.fixture()
        self.assertEqual(cmp.advance().status,'ROUTE_COMPOSED_MAP_CONFLICT')
        a.final.new.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        r=cmp.advance()
        self.assertEqual(r.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertEqual(r.left.status,'WALL_OBSERVATION')

    def test_wrong_declared_fingerprint_disallowed(self):
        cmp,a,b,*_=self.fixture()
        incorrect=TwoRouteComparison(a,b,{'left_chain_fingerprint':'0'*64,
                                         'right_chain_fingerprint':cmp.expected[1]})
        self.assertEqual(incorrect.advance().status,'ROUTE_FINGERPRINT_MISMATCH')

    def test_changing_second_middle_revision_withholds_route_agreement(self):
        cmp,a,b,m,*_=self.fixture(same_middle=True)
        self.assertEqual(cmp.advance().status,'ROUTES_AGREE_ON_SELECTED_EDGE')
        m.old.snapshot.revision+=1
        r=cmp.advance()
        self.assertEqual(r.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertEqual(r.right.status,'UNKNOWN_VERSION')

    def test_tampered_first_middle_witness_withholds_comparison(self):
        cmp,a,b,*_=self.fixture()
        self.assertEqual(cmp.advance().status,'ROUTE_COMPOSED_MAP_CONFLICT')
        a.first.recipient.old.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        r=cmp.advance()
        self.assertEqual(r.status,'ROUTE_EVIDENCE_UNPROVED')
        self.assertEqual(r.left.status,'WALL_OBSERVATION')

    def test_both_base_joins_remain_unchanged(self):
        cmp,a,b,m,*_=self.fixture()
        r=cmp.advance()
        self.assertEqual(r.status,'ROUTE_COMPOSED_MAP_CONFLICT')
        self.assertEqual(len(a.final.advance(max_new_edges=0).admitted_edges),4)
        self.assertEqual(len(a.first.donor.advance(max_new_edges=0).admitted_edges),3)
        self.assertEqual(len(m.advance(max_new_edges=0).admitted_edges),4)
        self.assertEqual(r.observations_before,r.observations_after)
        self.assertEqual(r.observations_after,((3,3),(5,5),(5,5),(6,6)))

    def test_invalid_intake_cannot_read_owner_edges(self):
        cmp,a,b,*_=self.fixture()
        bad=TwoRouteComparison(a,b,{'left_chain_fingerprint':'invalid',
                                  'right_chain_fingerprint':cmp.expected[1]})
        before=cmp._counts()
        self.assertEqual(bad.advance().status,'INVALID_ROUTE_COMPARISON')
        self.assertEqual(before,cmp._counts())

    def test_post_declaration_scope_swap_not_admitted(self):
        cmp,a,b,*_=self.fixture()
        self.assertEqual(cmp.advance().status,'ROUTE_COMPOSED_MAP_CONFLICT')
        b.first=a.first
        self.assertEqual(cmp.advance().status,'ROUTE_SCOPE_CHANGED')

    def test_same_middle_scope_not_two_independent_routes(self):
        cmp,a,b,*_=self.fixture()
        bad=TwoHopTransport(b.first,a.final,{'first_link_fingerprint':cmp.expected[1],
            'final_join_fingerprint':'0'*64,'old_state_transport':[], 'new_state_transport':[]})
        invalid=TwoRouteComparison(a,a,{'left_chain_fingerprint':cmp.expected[0],
                                       'right_chain_fingerprint':cmp.expected[0]})
        self.assertEqual(invalid.advance().status,'INVALID_ROUTE_COMPARISON')
        invalid2=TwoRouteComparison(a,TwoHopTransport(a.first,a.final,{
            'first_link_fingerprint':a.expected[0], 'final_join_fingerprint':a.expected[1],
            'old_state_transport':[{'donor':list(k),'recipient':list(v)} for k,v in a.old_map.items()],
            'new_state_transport':[{'donor':list(k),'recipient':list(v)} for k,v in a.new_map.items()] }),
            {'left_chain_fingerprint':cmp.expected[0], 'right_chain_fingerprint':cmp.expected[0]})
        self.assertEqual(invalid2.advance().status,'INVALID_ROUTE_COMPARISON')

if __name__=='__main__':unittest.main()
