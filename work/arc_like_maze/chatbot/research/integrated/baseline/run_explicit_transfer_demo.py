"""Demonstrate finite witnessed transfer without reading new owner edges."""
import json
from test_ab_chatbot_cross_pin_join import JoinCrossPinTests
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import current_digest
from ab_chatbot_explicit_evidence_transfer import ExplicitEvidenceTransfer,TransferredEvidenceTask

def settle(j):
    for _ in range(40):
        r=j.advance(max_new_edges=3)
        if r.status!='SEARCHING':
            return r
    raise RuntimeError('budget did not settle')

fixture=JoinCrossPinTests()
recipient,old,new,owner,reg,p,q=fixture.join(('A','BAA'))
assert settle(recipient).status=='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED'
donor=CrossPinJoin(old,new,{'required_owner_pins':{'old':p.token,'new':q.token},
                         'join_words':['B','ABB']},registry=reg)
assert settle(donor).status=='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED'
before=[len(old.snapshot.edges),len(new.snapshot.edges)]

def task(keys):
    contract={'recipient_fingerprint':current_digest(recipient),
              'donor_fingerprint':current_digest(donor),
              'transfer_edges':[{'state':list(s),'action':a} for s,a in keys]}
    transfer=ExplicitEvidenceTransfer(recipient,donor,contract)
    report=transfer.advance()
    return transfer,report

one,result=task((((1,0,0),'B'),))
requirements={'transfer_fingerprint':result.derived_digest,
              'required_edges':[{'state':[1,1,0],'action':'A'},
                                {'state':[1,0,0],'action':'B'}]}
completed=TransferredEvidenceTask(one,requirements).advance()
_,bad=task((((1,0,0),'B'),((1,2,0),'B')))
out={'transfer':{'status':result.status,'state_pairs':len(result.state_pairs),
                 'admitted_edges':len(result.admitted_edges),
                 'selected_edge':((1,0,0),'B'),'digest':result.derived_digest},
     'task':{'status':completed.status,'checks':completed.obligations},
     'conflicting_batch':{'status':bad.status,
             'obstruction':bad.obstruction.__dict__ if bad.obstruction else None},
     'owner_observations_before':before,
     'owner_observations_after':[len(old.snapshot.edges),len(new.snapshot.edges)]}
assert completed.status=='TASK_COMPLETED_ON_TRANSFER_WITNESS'
assert bad.status=='TRANSFER_STATE_CONFLICT'
assert out['owner_observations_before']==out['owner_observations_after']
with open('EXPLICIT_TRANSFER_RESULTS.json','w') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
