"""Three separately pinned source pairs; two independent selected-edge squares."""
import unittest
from copy import deepcopy
from test_ab_chatbot_cross_scope_transport import CrossScopeTransportTests
from test_ab_chatbot_cross_pin_comparison import CrossPinTests
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer
from ab_chatbot_joint_witness_binding import current_digest
from ab_chatbot_two_hop_transport import TwoHopTransport, TwoHopTask

class TwoHopTransportTests(unittest.TestCase):
    def fixture(self,*,final_newlaw=(2,2,1),final_budget=54):
        middle,donor,*_=CrossScopeTransportTests.fixture(self)
        first=CrossScopeIntertwiningTransfer(middle,donor,
                        CrossScopeTransportTests.declaration(self,middle,donor))
        first_report=first.advance()
        self.assertEqual(first_report.status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        old,new,_,registry,po,pn=CrossPinTests.make(self,oldlaw=(2,0,0),
                      newlaw=final_newlaw,budget=final_budget)
        final=CrossPinJoin(old,new,{'required_owner_pins':{'old':po.token,'new':pn.token},
                       'join_words':['A','BAA']},registry=registry)
        report=final.advance(max_new_edges=108)
        self.assertEqual(report.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        self.assertEqual((len(report.state_pairs),len(report.admitted_edges)),(5,4))
        declaration={'first_link_fingerprint':first_report.derived_fingerprint,
             'final_join_fingerprint':current_digest(final),
             'old_state_transport':[
                {'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,2]}],
             'new_state_transport':[
                {'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,2]}]}
        return first,final,declaration,registry,po,pn

    def test_two_separate_links_and_three_independent_scopes(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        before=tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges))
            for p in (first.donor,first.recipient,final))
        report=chain.advance()
        self.assertEqual(report.status,'TWO_HOP_CHAIN_WITNESSED')
        self.assertEqual((len(report.state_pairs),len(report.admitted_edges)),(6,5))
        self.assertEqual(len(report.links),2)
        self.assertEqual(report.links[1][1],((1,0,0),'B',(1,2,2),(1,0,0),(1,2,2)))
        self.assertEqual(report.observed_by_scope,
                         (before[0],before[1],
                                      (before[2][0]+1,before[2][1]+1)))
        self.assertEqual(len(first.donor.advance(max_new_edges=0).admitted_edges),3)
        self.assertEqual(len(final.advance(max_new_edges=0).admitted_edges),4)
        self.assertEqual(chain.advance().fingerprint,report.fingerprint)
        self.assertEqual(chain.advance().observed_by_scope,report.observed_by_scope)

    def test_task_consumes_only_chain_witness(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        rep=chain.advance()
        task=TwoHopTask(chain,{'chain_fingerprint':rep.fingerprint,
             'required_edges':[{'state':[1,1,2],'action':'A'},
                               {'state':[1,0,0],'action':'B'}]})
        status,report,checks=task.advance()
        self.assertEqual(status,'TASK_COMPLETED_ON_TWO_HOP_WITNESS')
        self.assertEqual([c[2] for c in checks],[True,True])
        self.assertEqual(report.fingerprint,rep.fingerprint)
        # The complete law does not authorize an edge absent from chain.
        unproved=TwoHopTask(chain,{'chain_fingerprint':rep.fingerprint,
             'required_edges':[{'state':[1,2,2],'action':'B'}]})
        self.assertEqual(unproved.advance()[0],'TASK_REQUIREMENTS_UNPROVED')
        different=TwoHopTask(chain,{'chain_fingerprint':'0'*64,
             'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(different.advance()[0],'WITNESS_FINGERPRINT_MISMATCH')

    def test_incorrect_second_map_yields_replayable_conflict(self):
        first,final,decl,*_=self.fixture()
        decl['new_state_transport'][1]['recipient']=[1,2,0]
        rep=TwoHopTransport(first,final,decl).advance()
        self.assertEqual(rep.status,'CHAIN_INTERTWINING_CONFLICT')
        self.assertEqual(rep.obstruction,(((1,2,2),(1,2,2)),((1,2,0),(1,2,2))))
        self.assertIsNone(rep.fingerprint)
        self.assertEqual(len(rep.links),2)

    def test_wrong_final_law_changes_second_square_only(self):
        first,final,decl,*_=self.fixture(final_newlaw=(0,2,1))
        report=TwoHopTransport(first,final,decl).advance()
        self.assertEqual(report.status,'CHAIN_INTERTWINING_CONFLICT')
        self.assertIsNone(report.fingerprint)

    def test_budget_stops_link_two_without_final_relation(self):
        first,final,decl,*_=self.fixture(final_budget=4)
        rep=TwoHopTransport(first,final,decl).advance()
        self.assertEqual(rep.status,'UNKNOWN_BUDGET')
        self.assertFalse(rep.state_pairs)
        self.assertIsNone(rep.fingerprint)

    def test_revoking_first_owner_pin_revokes_whole_chain(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        self.assertEqual(chain.advance().status,'TWO_HOP_CHAIN_WITNESSED')
        donor=first.donor
        donor.registry.revoke(donor._base._tokens[0])
        self.assertEqual(chain.advance().status,'OWNER_PIN_UNPROVED')

    def test_revoking_final_pin_revokes_whole_chain(self):
        first,final,decl,registry,po,pn=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        task=TwoHopTask(chain,{'chain_fingerprint':chain.advance().fingerprint,
                 'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(task.advance()[0],'TASK_COMPLETED_ON_TWO_HOP_WITNESS')
        registry.revoke(pn.token)
        self.assertEqual(task.advance()[0],'OWNER_PIN_UNPROVED')

    def test_tampered_final_observation_forces_wall(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        self.assertEqual(chain.advance().status,'TWO_HOP_CHAIN_WITNESSED')
        final.new.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        self.assertEqual(chain.advance().status,'WALL_OBSERVATION')

    def test_revision_change_withholds_certificate(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        self.assertEqual(chain.advance().status,'TWO_HOP_CHAIN_WITNESSED')
        final.old.snapshot.revision+=1
        self.assertEqual(chain.advance().status,'UNKNOWN_VERSION')

    def test_intermediate_pin_revocation_withholds_second_link(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        self.assertEqual(chain.advance().status,'TWO_HOP_CHAIN_WITNESSED')
        first.recipient.registry.revoke(first.recipient._base._tokens[1])
        self.assertEqual(chain.advance().status,'OWNER_PIN_UNPROVED')

    def test_intermediate_selected_edge_tampering_withholds_chain(self):
        first,final,decl,*_=self.fixture()
        chain=TwoHopTransport(first,final,decl)
        self.assertEqual(chain.advance().status,'TWO_HOP_CHAIN_WITNESSED')
        first.recipient.new.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        self.assertEqual(chain.advance().status,'WALL_OBSERVATION')

    def test_wrong_first_fingerprint_no_completion(self):
        first,final,decl,*_=self.fixture()
        decl['first_link_fingerprint']='0'*64
        r=TwoHopTransport(first,final,decl).advance()
        self.assertEqual(r.status,'CHAIN_FINGERPRINT_MISMATCH')

    def test_maps_cannot_claim_extra_states(self):
        first,final,decl,*_=self.fixture()
        decl['old_state_transport'].append({'donor':[2,2,2],'recipient':[2,2,2]})
        r=TwoHopTransport(first,final,decl).advance()
        self.assertEqual(r.status,'INVALID_CHAIN')

    def test_scope_reuse_prohibited(self):
        first,final,decl,*_=self.fixture()
        self.assertEqual(TwoHopTransport(first,first.recipient,decl).advance().status,'INVALID_CHAIN')

if __name__=='__main__':unittest.main()
