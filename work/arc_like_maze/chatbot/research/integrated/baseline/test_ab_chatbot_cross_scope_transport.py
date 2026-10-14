"""Different owner pin scopes require independently observed commuting squares."""
import unittest
from copy import deepcopy
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer, CrossScopeTransportTask
from ab_chatbot_joint_witness_binding import current_digest
from test_ab_chatbot_cross_pin_comparison import CrossPinTests

EDGE=((1,0,0),'B')

class CrossScopeTransportTests(unittest.TestCase):
    def fixture(self,*,recipient_newlaw=(0,1,2),donor_newlaw=(1,0,1),recipient_budget=54):
        old,new,_,rreg,rp,rq=CrossPinTests.make(self,oldlaw=(0,0,0),
                     newlaw=recipient_newlaw,budget=recipient_budget)
        do,dn,_,dreg,dp,dq=CrossPinTests.make(self,oldlaw=(0,0,1),newlaw=donor_newlaw)
        r=CrossPinJoin(old,new,{'required_owner_pins':{'old':rp.token,'new':rq.token},
                                'join_words':['A','BAA']},registry=rreg)
        d=CrossPinJoin(do,dn,{'required_owner_pins':{'old':dp.token,'new':dq.token},
                              'join_words':['AB','B']},registry=dreg)
        for agent in (r,d):
            for _ in range(10):
                output=agent.advance(max_new_edges=108)
                if output.status!='SEARCHING':break
            self.assertEqual(output.status,'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED')
        return r,d,rreg,rp,rq,dreg,dp,dq

    def declaration(self,r,d):
        return {'recipient_fingerprint':current_digest(r),'donor_fingerprint':current_digest(d),
            'selected_donor_edge':{'state':[1,0,0],'action':'B'},
            'old_state_transport':[
                {'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,0]}],
            'new_state_transport':[
                {'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,1],'recipient':[1,2,0]}]}

    def test_different_owner_scopes_witness_selected_square(self):
        r,d,*_=self.fixture()
        self.assertIsNot(r.registry,d.registry)
        t=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        before=(len(r.old.snapshot.edges),len(r.new.snapshot.edges),
                len(d.old.snapshot.edges),len(d.new.snapshot.edges))
        rep=t.advance()
        self.assertEqual(rep.status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        self.assertEqual((len(rep.state_pairs),len(rep.admitted_edges)),(6,5))
        self.assertEqual(rep.selected_square[0],((1,0,0),'B',(1,2,0),(1,0,0),(1,2,1)))
        self.assertEqual(rep.selected_square[1],((1,0,0),'B',(1,2,0),(1,0,0),(1,2,0)))
        self.assertEqual(tuple(map(len,(r.old.snapshot.edges,r.new.snapshot.edges,
                d.old.snapshot.edges,d.new.snapshot.edges))),
                (before[0]+1,before[1]+1,before[2],before[3]))
        self.assertEqual(rep.derived_fingerprint,t.advance().derived_fingerprint)
        self.assertEqual(tuple(map(len,(r.old.snapshot.edges,r.new.snapshot.edges,
                d.old.snapshot.edges,d.new.snapshot.edges))),
                (before[0]+1,before[1]+1,before[2],before[3]))

    def test_task_two_edges_can_use_derived_witness_without_claiming_original_join(self):
        r,d,*_=self.fixture()
        self.assertNotIn(EDGE,{(s,a) for s,a,*_ in r.advance(max_new_edges=0).admitted_edges})
        rep=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d)).advance()
        edges={(s,a) for s,a,*_ in rep.admitted_edges}
        self.assertIn(EDGE,edges)
        self.assertIn(((1,1,0),'A'),edges)
        self.assertNotIn(EDGE,{(s,a) for s,a,*_ in r.advance(max_new_edges=0).admitted_edges})

    def test_wrong_explicit_new_state_map_replays_noncommuting_square(self):
        r,d,*_=self.fixture()
        req=self.declaration(r,d)
        req['new_state_transport'][1]['recipient']=[1,2,1]
        report=CrossScopeIntertwiningTransfer(r,d,req).advance()
        self.assertEqual(report.status,'TRANSPORT_INTERTWINING_CONFLICT')
        self.assertIsNone(report.derived_fingerprint)
        self.assertEqual(report.obstruction,(((1,2,0),(1,2,0)),((1,2,1),(1,2,0))))

    def test_matching_labels_alone_never_trigger_mapping(self):
        r,d,*_=self.fixture()
        req=self.declaration(r,d);req['old_state_transport']=[]
        self.assertEqual(CrossScopeIntertwiningTransfer(r,d,req).advance().status,'INVALID_TRANSPORT')
        req=self.declaration(r,d);req['old_state_transport']=req['old_state_transport'][:1]
        self.assertEqual(CrossScopeIntertwiningTransfer(r,d,req).advance().status,'INVALID_TRANSPORT')

    def test_corrupted_or_revoked_base_withholds_previous_success(self):
        r,d,rreg,rp,rq,dreg,dp,dq=self.fixture()
        t=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        self.assertEqual(t.advance().status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        dreg.revoke(dp.token)
        self.assertEqual(t.advance().status,'OWNER_PIN_UNPROVED')
        self.assertIsNone(t.advance().derived_fingerprint)

    def test_changed_recipient_revision_or_tampered_new_edge_withholds(self):
        r,d,*_=self.fixture()
        t=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        self.assertEqual(t.advance().status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        r.new.snapshot.edges[((1,0,0),'B')]=(2,2,2)
        self.assertEqual(t.advance().status,'WALL_OBSERVATION')
        x,y,*_=self.fixture()
        t2=CrossScopeIntertwiningTransfer(x,y,self.declaration(x,y))
        self.assertEqual(t2.advance().status,'CROSS_SCOPE_INTERTWINING_WITNESSED')
        x.new.snapshot.revision+=1
        self.assertEqual(t2.advance().status,'UNKNOWN_VERSION')

    def test_missing_donor_witness_is_not_completed_from_the_laws(self):
        r,d,*_=self.fixture()
        req=self.declaration(r,d);req['selected_donor_edge']={'state':[2,2,2],'action':'A'}
        self.assertEqual(CrossScopeIntertwiningTransfer(r,d,req).advance().status,
                         'TRANSPORT_DONOR_EDGE_UNPROVED')

    def test_observation_budget_withholds_square(self):
        r,d,*_=self.fixture(recipient_budget=4)
        before=len(r.old.snapshot.edges)
        t=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        self.assertEqual(t.advance().status,'UNKNOWN_BUDGET')
        self.assertIsNone(t.advance().derived_fingerprint)
        self.assertEqual(len(r.old.snapshot.edges),before)

    def test_changed_recipient_target_transition_yields_counterexample(self):
        r,d,*_=self.fixture(recipient_newlaw=(1,0,1))
        # The changed recipient law yields a different endpoint from the
        # explicitly declared transport image of donor's new endpoint.
        t=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        result=t.advance()
        self.assertEqual(result.status,'TRANSPORT_INTERTWINING_CONFLICT')

    def test_duplicate_mapping_or_bad_fingerprint_rejected(self):
        r,d,*_=self.fixture()
        req=self.declaration(r,d);req['old_state_transport'][1]['donor']=[1,0,0]
        self.assertEqual(CrossScopeIntertwiningTransfer(r,d,req).advance().status,'INVALID_TRANSPORT')
        req=self.declaration(r,d);req['donor_fingerprint']='0'*64
        self.assertEqual(CrossScopeIntertwiningTransfer(r,d,req).advance().status,
                         'WITNESS_FINGERPRINT_MISMATCH')


    def test_two_edge_task_completed_only_from_derived_square(self):
        r,d,*_=self.fixture()
        tx=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        digest=tx.advance().derived_fingerprint
        task=CrossScopeTransportTask(tx,{'cross_scope_fingerprint':digest,
            'required_edges':[{'state':[1,1,0],'action':'A'},
                              {'state':[1,0,0],'action':'B'}]})
        res=task.advance()
        self.assertEqual(res.status,'TASK_COMPLETED_ON_CROSS_SCOPE_WITNESS')
        self.assertEqual([row[2] for row in res.obligations],[True,True])
        missing=CrossScopeTransportTask(tx,{'cross_scope_fingerprint':digest,
            'required_edges':[{'state':[1,2,0],'action':'B'}]})
        self.assertEqual(missing.advance().status,'TASK_REQUIREMENTS_UNPROVED')
        altered=CrossScopeTransportTask(tx,{'cross_scope_fingerprint':'0'*64,
            'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(altered.advance().status,'WITNESS_FINGERPRINT_MISMATCH')

    def test_task_rechecks_pin_after_prior_completion(self):
        r,d,rr,rp,rq,dr,dp,dq=self.fixture()
        tx=CrossScopeIntertwiningTransfer(r,d,self.declaration(r,d))
        task=CrossScopeTransportTask(tx,{'cross_scope_fingerprint':tx.advance().derived_fingerprint,
            'required_edges':[{'state':[1,0,0],'action':'B'}]})
        self.assertEqual(task.advance().status,'TASK_COMPLETED_ON_CROSS_SCOPE_WITNESS')
        rr.revoke(rp.token)
        self.assertEqual(task.advance().status,'OWNER_PIN_UNPROVED')
        self.assertFalse(task.advance().obligations)

if __name__=='__main__':unittest.main()
