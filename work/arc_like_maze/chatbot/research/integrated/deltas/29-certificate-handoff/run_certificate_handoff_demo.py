"""Reproducible CP-29 cross-invocation route-handoff demonstration."""
import json
from ab_chatbot_certificate_handoff import issue_handoff,accept_handoff
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
from test_ab_chatbot_multi_task_dependency import MultiRouteTaskDependencyTests


def make_fixture():
    x=RouteBoundTaskTests('runTest')
    refresh,_,left,right,_,registry,_,right_pin=x.fixture()
    a=x.task(refresh,'left',required_edges=[{'state':[1,0,0],'action':'B'}])
    b=x.task(refresh,'left',required_edges=[{'state':[1,1,2],'action':'A'}])
    unproved=x.task(refresh,'left',required_edges=[{'state':[0,1,2],'action':'B'}])
    return a,b,unproved,left,right


def main():
    a,b,unproved,left,right=make_fixture()
    scopes=(left.first.donor,left.first.recipient,left.final)
    counts=lambda:tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in scopes)
    before=counts()
    outbound=issue_handoff(a)
    assert outbound.status=='HANDOFF_REFERENCE_ISSUED'
    watch=MultiRouteTaskDependencyTests.spy(RouteBoundTaskTests('runTest'),left,right)
    carried=json.dumps(json.loads(outbound.receipt),sort_keys=True,separators=(',',':'))
    incoming=accept_handoff(carried,{'a':a,'unproved':unproved,'b':b})
    assert incoming.status=='HANDOFF_FRESHLY_REVALIDATED'
    assert incoming.usable==('a','b') and dict(incoming.task_status)['unproved']=='ROUTE_TASK_REQUIREMENTS_UNPROVED'
    assert watch=={'left':2,'right':0} and counts()==before
    next_call=accept_handoff(carried,{'new':b})
    assert next_call.proof_for_use and watch=={'left':4,'right':0}
    old_witness=carried
    left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
    withdrawn=accept_handoff(old_witness,{'a':a,'b':b})
    assert not withdrawn.proof_for_use
    out={
      'checkpoint':29,'experiment':'cross-invocation route-certificate reference',
      'sender_status':outbound.status,'sender_replay_calls':outbound.replay_calls,
      'receiver_status':incoming.status,'receiver_replay_calls':incoming.replay_calls,
      'receiver_tasks':dict(incoming.task_status),'receiver_usable':list(incoming.usable),
      'subsequent_invocation':next_call.status,'subsequent_replay_calls':next_call.replay_calls,
      'revocation_status':withdrawn.status,'revoked_receipt_not_usable':not withdrawn.proof_for_use,
      'source_observations_unchanged_before_revocation':True,
      'task_requirements_not_in_receipt':'required_edges' not in json.loads(carried),
      'independent_remote_authentication':False}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=='__main__':main()
