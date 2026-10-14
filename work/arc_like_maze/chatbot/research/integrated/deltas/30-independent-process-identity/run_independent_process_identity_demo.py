"""CP-30 reproducible, bounded independent-process identity demonstration."""
import json
import os
from dataclasses import replace
from ab_chatbot_independent_process_identity import (
    issue_owner_attestations, receive_owner_attestations, new_challenge)
from finite_process_attestation import generate_fixture_keys
from test_ab_chatbot_route_bound_task import RouteBoundTaskTests
from test_ab_chatbot_multi_task_dependency import MultiRouteTaskDependencyTests


def main():
    helper=RouteBoundTaskTests('runTest')
    refresh,_,left,right,_,registry,_,right_pin=helper.fixture()
    task=lambda s,a:helper.task(refresh,'left',required_edges=[{'state':list(s),'action':a}])
    a=task((1,0,0),'B');b=task((1,1,2),'A');bad=task((0,1,2),'B')
    secrets, trust=generate_fixture_keys()
    challenge=new_challenge()
    scopes=(left.first.donor,left.first.recipient,left.final)
    counts=lambda: tuple((len(x.old.snapshot.edges),len(x.new.snapshot.edges)) for x in scopes)
    before=counts()
    issued=issue_owner_attestations(a,secrets,challenge)
    assert issued.status=='ATTESTATIONS_ISSUED'
    watcher=MultiRouteTaskDependencyTests.spy(helper,left,right)
    verified=receive_owner_attestations(issued,{'a':a,'bad':bad,'b':b},trust,challenge)
    assert verified.status=='INDEPENDENT_PROCESS_FRESHLY_VERIFIED'
    assert verified.usable==('a','b') and dict(verified.tasks)['bad']=='ROUTE_TASK_REQUIREMENTS_UNPROVED'
    assert watcher=={'left':2,'right':0}
    assert issued.signer_pid!=verified.verifier_pid and os.getpid() not in (issued.signer_pid,verified.verifier_pid)
    source_unchanged=counts()==before
    wrong_nonce=receive_owner_attestations(issued,{'a':a},trust,new_challenge())
    wrong_trust=dict(trust);wrong_trust['donor']=wrong_trust['middle']
    swapped_key=receive_owner_attestations(issued,{'a':a},wrong_trust,challenge)
    repeated=receive_owner_attestations(issued,{'a':a},trust,challenge)
    assert watcher=={'left':4,'right':0}
    left.first.recipient.registry.revoke(left.first.recipient._base._tokens[0])
    revoked=receive_owner_attestations(issued,{'a':a},trust,challenge)
    assert not revoked.proof_for_use
    output={
      'checkpoint':30,'experiment':'independent-process synthetic owner-scope attestations',
      'signer_separate_process':True,'verifier_separate_process':True,
      'scope_count':3,'scopes':['donor','middle','final'],
      'valid_status':verified.status,'valid_tasks':dict(verified.tasks),
      'valid_usable':list(verified.usable),'valid_replay_calls':verified.replay_calls,
      'wrong_challenge':wrong_nonce.status,'wrong_pinned_key':swapped_key.status,
      'reused_signed_bundle_reaudited':repeated.status,'later_replay_calls':repeated.replay_calls,
      'source_revoked_status':revoked.status,
      'no_new_observations':source_unchanged,
      'real_world_owner_authenticated':False,'deployed_trust_bootstrap_verified':False}
    print(json.dumps(output, indent=2, sort_keys=True))

if __name__=='__main__':main()
