"""Independent law-level assessment of TWO explicitly composed two-hop routes.

Complete laws are supplied, so this does NOT prove observation or owner
identity. An image conflict refutes a proposed route-INDEPENDENT map on the
selected endpoints, not the validity of either separately declared route.
"""
from dataclasses import dataclass
from finite_goal_priority import Law
from finite_two_hop_transport import chain
from finite_cross_pin_join import join

@dataclass(frozen=True)
class FiniteRouteAssessment:
    status: str
    left_status: str
    right_status: str
    left_composed: tuple
    right_composed: tuple
    disagreements: tuple
    left_final_edges: tuple
    right_final_edges: tuple


def _compose(selected_edge, first_old_map, first_new_map,
             second_old_map, second_new_map):
    ds,a,dt,dns,dnt=selected_edge
    fo,fn,so,sn=map(dict,(first_old_map,first_new_map,
                           second_old_map,second_new_map))
    if (set(fo)!={ds,dt} or set(fn)!={dns,dnt} or
        set(so)!={fo[ds],fo[dt]} or set(sn)!={fn[dns],fn[dnt]}):
        return ()
    return ((ds,so[fo[ds]]),(dt,so[fo[dt]]),
            (dns,sn[fn[dns]]),(dnt,sn[fn[dnt]]))


def compare(donor, middle_left, middle_right, final, donor_words,
            middle_words_left, middle_words_right, final_words, selected,
            maps_left, maps_right):
    """Each maps tuple contains first-old, first-new, second-old, second-new."""
    if (type(maps_left) is not tuple or type(maps_right) is not tuple or
        len(maps_left)!=4 or len(maps_right)!=4):
        raise ValueError('two explicit four-map routes are required')
    l=chain(donor,middle_left,final,donor_words,middle_words_left,final_words,
            selected,*maps_left)
    r=chain(donor,middle_right,final,donor_words,middle_words_right,final_words,
            selected,*maps_right)
    if (l.status,r.status)!=('TWO_HOP_CHAIN_WITNESSED',)*2:
        return FiniteRouteAssessment('ROUTE_EVIDENCE_UNPROVED',l.status,r.status,
                                     (),(),(),(),())
    # Both independently checked chains begin with the exact same donor edge.
    original=join(*donor,donor_words)
    selected_edge=next((e for e in original.admitted_edges if e[:2]==selected),None)
    if selected_edge is None or l.links[0][0]!=selected or r.links[0][0]!=selected:
        return FiniteRouteAssessment('DONOR_EDGE_MISMATCH',l.status,r.status,
                                     (),(),(),(),())
    lm=_compose(selected_edge,*maps_left)
    rm=_compose(selected_edge,*maps_right)
    if not lm or not rm:
        return FiniteRouteAssessment('ROUTE_MAPPING_INCOMPLETE',l.status,r.status,
                                     lm,rm,(),(),())
    differences=tuple((i,lm[i],rm[i]) for i in range(4) if lm[i]!=rm[i])
    return FiniteRouteAssessment('ROUTE_COMPOSED_MAP_CONFLICT' if differences else
                                 'ROUTES_AGREE_ON_SELECTED_EDGE',l.status,r.status,
                                 lm,rm,differences,l.admitted_edges,r.admitted_edges)

if __name__=='__main__':
    from test_finite_two_route_comparison import setup
    print(compare(**setup()).status)
