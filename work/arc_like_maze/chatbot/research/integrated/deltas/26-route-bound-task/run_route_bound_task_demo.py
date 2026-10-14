"""Reproduce a route-specific task using the existing owner-backed fixtures."""
import json
from pathlib import Path
from ab_chatbot_route_bound_task import RouteBoundTask
from test_ab_chatbot_route_selective_refresh import RouteSelectiveTests


def counts(chain):
    return tuple((len(p.old.snapshot.edges), len(p.new.snapshot.edges))
                 for p in (chain.first.donor,chain.first.recipient,chain.final))


def task(refresh,side,edges):
    return RouteBoundTask(refresh,{
        'route':side,
        'route_fingerprint':refresh.comparison.expected[0 if side=='left' else 1],
        'required_edges':[{'state':list(s),'action':a} for s,a in edges]})


def run():
    helper=RouteSelectiveTests()
    refresh,compare,left,right,middle,registry,_,right_pin=helper.fixture()
    left_task=task(refresh,'left',(((1,0,0),'B'),((1,1,2),'A')))
    borrowed=task(refresh,'left',(((0,1,2),'B'),))
    baseline=left_task.advance()
    registry.revoke(right_pin.token)
    before=counts(left)
    after_right_change=left_task.advance()
    unproved=borrowed.advance()
    after=counts(left)
    comparison=refresh.verify_for_use()
    left.first.donor.registry.revoke(left.first.donor._base._tokens[0])
    withdrawn=left_task.advance()
    return {'case':'selected left route with right middle source revoked',
        'historical_comparison':baseline.historical_comparison.status,
        'before_source_change':baseline.status,
        'after_neighbor_revocation':after_right_change.status,
        'proof_from_other_route':unproved.status,
        'full_comparison_after_right_revocation':comparison.status,
        'selected_route_after_own_revocation':withdrawn.status,
        'selected_edge_checks':[
            {'kind':x.kind,'required':str(x.requirement),'admitted':x.admitted}
            for x in after_right_change.obligations],
        'selected_route_edge_counts_before':before,
        'selected_route_edge_counts_after':after,
        'new_owner_edge_observations':sum(sum(pair) for pair in after)-sum(sum(pair) for pair in before),
        'task_fingerprint':left_task.task_fingerprint,
        'selected_fingerprint':left_task.expected}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
