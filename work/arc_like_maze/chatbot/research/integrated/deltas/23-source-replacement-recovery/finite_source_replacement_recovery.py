"""Independent finite-law recovery reference; NO owner authentication.

Caller supplies whether old and unaffected pins remain valid. The integrated
chatbot obtains those statuses by re-auditing live pinned observations. This
reference never treats a repeated source label as proof or merges two routes.
"""
from dataclasses import dataclass
from finite_two_route_comparison import compare

VALID=('ROUTES_AGREE_ON_SELECTED_EDGE','ROUTE_COMPOSED_MAP_CONFLICT')

@dataclass(frozen=True)
class FiniteReplacement:
    status: str
    historical: object
    replacement: object | None
    historical_middle_ref: str
    replacement_middle_ref: str


def reassess(baseline:dict, *, replacement_middle, replacement_maps,
             old_middle_ref:str, replacement_middle_ref:str,
             old_right_valid:bool, left_valid:bool):
    if (type(baseline) is not dict or type(replacement_maps) is not tuple or
        len(replacement_maps)!=4 or type(old_middle_ref) is not str or
        type(replacement_middle_ref) is not str or not old_middle_ref or
        not replacement_middle_ref or old_middle_ref==replacement_middle_ref or
        type(old_right_valid) is not bool or type(left_valid) is not bool):
        raise ValueError('independent replacement referent and explicit validity required')
    historical=compare(**baseline)
    if historical.status not in VALID:
        return FiniteReplacement('BASELINE_UNPROVED',historical,None,old_middle_ref,replacement_middle_ref)
    if not left_valid:
        return FiniteReplacement('UNAFFECTED_ROUTE_UNPROVED',historical,None,old_middle_ref,replacement_middle_ref)
    if old_right_valid:
        return FiniteReplacement('RECOVERY_NOT_NEEDED',historical,None,old_middle_ref,replacement_middle_ref)
    proposal={**baseline,'middle_right':replacement_middle,'maps_right':replacement_maps}
    current=compare(**proposal)
    status=('RECOVERY_AGREEMENT_WITNESSED' if current.status=='ROUTES_AGREE_ON_SELECTED_EDGE' else
            'RECOVERY_CONFLICT_WITNESSED' if current.status=='ROUTE_COMPOSED_MAP_CONFLICT' else
            'REPLACEMENT_UNPROVED')
    return FiniteReplacement(status,historical,current,old_middle_ref,replacement_middle_ref)

if __name__=='__main__':
    from test_finite_two_route_comparison import setup,M1,AL
    r=reassess(setup(),replacement_middle=M1,replacement_maps=AL,
               old_middle_ref='historical-owner-0',replacement_middle_ref='new-owner-1',
               old_right_valid=False,left_valid=True)
    print(r.status,r.historical.status,r.replacement.status)
