"""Independent complete-law reference for scope-specific relation re-evaluation.

Input laws are fully declared. This models no HTTP observation, pin registry or
source owner. In particular an externally announced revision without replacing
the selected historical law is not a change to that law's evidence.
"""
from dataclasses import dataclass
from finite_two_route_comparison import compare

SCOPES=('donor','middle_left','middle_right','final')
VALID=('ROUTES_AGREE_ON_SELECTED_EDGE','ROUTE_COMPOSED_MAP_CONFLICT')

@dataclass(frozen=True)
class FiniteChangeAssessment:
    status: str
    changed_scopes: tuple
    affected_routes: tuple
    left_status: str
    right_status: str
    comparison_status: str
    baseline: object
    current: object


def reassess(declared_before:dict, declared_now:dict):
    if (type(declared_before) is not dict or type(declared_now) is not dict or
            set(declared_before)!=set(declared_now)):
        raise ValueError('same declared problem schema required')
    before=compare(**declared_before)
    now=compare(**declared_now)
    changes=tuple(k for k in SCOPES if declared_before[k]!=declared_now[k])
    affected=tuple(x for x in ('left','right') if any(
        k in ('donor','final',('middle_'+x)) for k in changes))
    if before.status not in VALID:
        return FiniteChangeAssessment('BASELINE_UNPROVED',changes,affected,
                         now.left_status,now.right_status,now.status,before,now)
    status=('RELATION_WITHDRAWN' if now.status not in VALID else
            'RELATION_PRESERVED' if before.status==now.status and
            before.left_composed==now.left_composed and
            before.right_composed==now.right_composed else 'RELATION_CHANGED')
    return FiniteChangeAssessment(status,changes,affected,
                         now.left_status,now.right_status,now.status,before,now)
