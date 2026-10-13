"""Reproduce two independently valid owner-backed routes with clashing maps."""
import json
from test_ab_chatbot_two_route_comparison import TwoRouteTests
from finite_two_route_comparison import compare
from test_finite_two_route_comparison import setup


def pack(r):
    return {
      'status':r.status, 'donor_edge':r.donor_edge,
      'left_status':r.left.status,'right_status':r.right.status,
      'left_fingerprint':r.left.fingerprint,'right_fingerprint':r.right.fingerprint,
      'left_composed':r.left_composed,'right_composed':r.right_composed,
      'disagreements':r.disagreement,
      'owner_observations_before':r.observations_before,
      'owner_observations_after':r.observations_after,
      'left_final_pairs':len(r.left.state_pairs),
      'right_final_pairs':len(r.right.state_pairs),
      'left_final_edges':len(r.left.admitted_edges),
      'right_final_edges':len(r.right.admitted_edges),
    }


def run():
    obj=TwoRouteTests()
    distinct,*_=obj.fixture()
    initial=distinct.advance()
    repeated=distinct.advance()
    agreement,*_=TwoRouteTests().fixture(same_middle=True)
    equivalent=agreement.advance()
    finite=compare(**setup())
    return {
      'finite_model':{'status':finite.status,'disagreements':finite.disagreements},
      'different_composed_routes':pack(initial),
      'zero_read_revisit':{'status':repeated.status,
                           'observation_totals_unchanged':
                               repeated.observations_before==repeated.observations_after},
      'independent_routes_agreeing':pack(equivalent),
      'claim_scope':'selected donor edge and four declared endpoints only; not global source equivalence',
    }

if __name__=='__main__':print(json.dumps(run(),indent=2))
