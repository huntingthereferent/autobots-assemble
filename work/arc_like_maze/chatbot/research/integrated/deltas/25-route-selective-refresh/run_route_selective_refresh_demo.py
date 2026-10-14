"""Reproduce route-level selectivity and the proof-for-use replay boundary."""
import json
from pathlib import Path
from ab_chatbot_route_selective_refresh import RouteSelectiveRefresh
from ab_chatbot_source_change_propagation import SourceChangePropagation
from test_ab_chatbot_two_route_comparison import TwoRouteTests
from ab_chatbot_discovered_correspondence import DOMAIN
from ab_chatbot_stability_witness import TransportedLaw


def fixture():
    test=TwoRouteTests('test_independent_valid_routes_can_disagree_without_one_being_false')
    cmp,left,right,middle,registry,pinold,pinnew=test.fixture()
    h=SourceChangePropagation(cmp)
    assert h.advance().status=='BASELINE_WITNESSED'
    return RouteSelectiveRefresh(h),left,right,middle,registry,pinnew


def report(r):
    return {'status':r.status,'audited':list(r.audited),'skipped':list(r.skipped),
            'routes':[{'name':v.name,'mode':v.mode,'outcome':v.outcome,
                      'fresh':v.proof_fresh} for v in r.routes],
            'changed':[{'scope':x.scope,'causes':list(x.causes)} for x in r.changed],
            'comparison_proof_for_use':r.proof_for_use,
            'historical_comparison':r.historical_comparison.status,
            'current_comparison':r.current_comparison.status if r.current_comparison else None,
            'additional_observations':sum(sum(after)-sum(before) for before,after in
                                         zip(r.observations_before,r.observations_after))}


def demo():
    a,left,right,middle,registry,pin=fixture()
    still=report(a.advance())
    registry.revoke(pin.token)
    changed=report(a.advance())
    blocked=report(a.verify_for_use())
    b,leftb,rightb,middleb,registryb,pinb=fixture()
    middleb.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
    movement=report(b.advance())
    repaired=report(b.verify_for_use())
    c,leftc,rightc,middlec,registryc,pinc=fixture()
    leftc.final.registry.revoke(leftc.final._base._tokens[0])
    shared=report(c.advance())
    result={'case':'selective route-level replay within existing two-route comparison',
            'stable':still,'right_middle_revoked':changed,
            'revoked_full_use':blocked,'new_head_historical_snapshot_survives':movement,
            'explicit_full_use':repaired,'shared_final_revoked':shared}
    target=Path(__file__).with_name('ROUTE_SELECTIVE_REFRESH_RESULTS.json')
    target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:{'status':v['status'],'audited':v['audited'],
                          'skipped':v['skipped'],'new_reads':v['additional_observations']}
                      for k,v in result.items() if isinstance(v,dict)},indent=2))
    print('evidence:',target)

if __name__=='__main__':demo()
