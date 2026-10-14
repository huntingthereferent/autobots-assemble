"""Executed independently under live owner-backed finite HTTP observations."""
import json
from ab_chatbot_source_change_propagation import SourceChangePropagation
from ab_chatbot_stability_witness import TransportedLaw
from ab_chatbot_discovered_correspondence import DOMAIN
from test_ab_chatbot_two_route_comparison import TwoRouteTests


def run_case(change):
    test=TwoRouteTests()
    try:
        comparison,left,right,middle,registry,pold,pnew=test.fixture()
        harness=SourceChangePropagation(comparison)
        initial=harness.advance()
        if change=='right_pin_revoked':
            registry.revoke(pnew.token)
        elif change=='owner_head_advanced':
            middle.old.owner.replace(TransportedLaw((2,2,2),tuple(DOMAIN)))
        elif change=='shared_final_revoked':
            left.final.registry.revoke(left.final._base._tokens[1])
        elif change!='unchanged':
            raise ValueError(change)
        current=harness.advance()
        return {
          'initial_comparison':initial.comparison,
          'propagation_status':current.status,
          'left_route':current.left_route,
          'right_route':current.right_route,
          'comparison':current.comparison,
          'changed_scopes':[
              {'scope':item.scope,'causes':item.causes} for item in current.changed_scopes],
          'affected_routes':current.affected_routes,
          'observations_before':current.observations_before,
          'observations_after':current.observations_after,
          'new_observations_from_refresh':sum(sum(a)-sum(b) for b,a in
                                              zip(current.observations_before,current.observations_after)),
          'historical_comparison_kept':current.historical is not None and
                                        current.historical.status==initial.comparison,
          'current_disagreements':current.current.disagreement,
        }
    finally:
        test.doCleanups()


def run():
    return {'unchanged':run_case('unchanged'),
      'right_pin_revoked':run_case('right_pin_revoked'),
      'owner_head_advanced':run_case('owner_head_advanced'),
      'shared_final_revoked':run_case('shared_final_revoked'),
      'scope':'four live in-process owner-pinned pairs; explicit on-demand replay, no autonomous watching',
      'historical_evidence':'preserved separately from live result; no re-pin or transport inferred'}

if __name__=='__main__':print(json.dumps(run(),indent=2))
