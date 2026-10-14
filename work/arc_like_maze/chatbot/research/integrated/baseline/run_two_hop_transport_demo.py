"""Executed locally: three independently pinned scope pairs and two certified links."""
import json
import unittest
from test_ab_chatbot_cross_scope_transport import CrossScopeTransportTests
from test_ab_chatbot_cross_pin_comparison import CrossPinTests
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer
from ab_chatbot_joint_witness_binding import current_digest
from ab_chatbot_two_hop_transport import TwoHopTransport,TwoHopTask


def run():
    fixture=unittest.TestCase()
    try:
        mid,donor,*_=CrossScopeTransportTests.fixture(fixture)
        final_old,final_new,_,registry,old_pin,new_pin=CrossPinTests.make(
            fixture,oldlaw=(2,0,0),newlaw=(2,2,1))
        final=CrossPinJoin(final_old,final_new,
              {'required_owner_pins':{'old':old_pin.token,'new':new_pin.token},
               'join_words':['A','BAA']},registry=registry)
        assert final.advance(max_new_edges=108).status=='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED'
        pairs=(donor,mid,final)
        count=lambda:tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in pairs)
        base=count()
        decl=CrossScopeTransportTests.declaration(fixture,mid,donor)
        first=CrossScopeIntertwiningTransfer(mid,donor,decl)
        first_rep=first.advance()
        assert first_rep.status=='CROSS_SCOPE_INTERTWINING_WITNESSED'
        after_first=count()
        chain_decl={
            'first_link_fingerprint':first_rep.derived_fingerprint,
            'final_join_fingerprint':current_digest(final),
            'old_state_transport':[
                {'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,2]}],
            'new_state_transport':[
                {'donor':[1,0,0],'recipient':[1,0,0]},
                {'donor':[1,2,0],'recipient':[1,2,2]}]}
        chain=TwoHopTransport(first,final,chain_decl)
        report=chain.advance()
        assert report.status=='TWO_HOP_CHAIN_WITNESSED'
        after_second=count()
        task=TwoHopTask(chain,{'chain_fingerprint':report.fingerprint,
            'required_edges':[{'state':[1,1,2],'action':'A'},
                              {'state':[1,0,0],'action':'B'}]})
        status,_,obligations=task.advance()
        after_task=count()
        assert status=='TASK_COMPLETED_ON_TWO_HOP_WITNESS'
        bad=json.loads(json.dumps(chain_decl))
        bad['new_state_transport'][1]['recipient']=[1,2,0]
        conflict=TwoHopTransport(first,final,bad).advance()
        assert conflict.status=='CHAIN_INTERTWINING_CONFLICT'
        return {'laws':[{'old':[0,0,1],'new':[1,0,1]},
                        {'old':[0,0,0],'new':[0,1,2]},
                        {'old':[2,0,0],'new':[2,2,1]}],
          'baseline_observations':base,
          'after_first_link':after_first,'after_second_link':after_second,
          'after_task':after_task,'link_one':first_rep.selected_square,
          'link_two':report.links[1],'status':report.status,
          'paired_states':len(report.state_pairs),'admitted_edges':len(report.admitted_edges),
          'chain_fingerprint':report.fingerprint,
          'task_status':status,'task_obligations':obligations,
          'negative_status':conflict.status,'negative_obstruction':conflict.obstruction,
          'original_join_edges':[len(p.advance(max_new_edges=0).admitted_edges) for p in pairs]}
    finally:fixture.doCleanups()

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
