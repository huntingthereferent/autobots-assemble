"""Exhaustive scoped classification; run from repo root: python -m research.continuity_fifth_couplings.verify"""
from itertools import product
from collections import Counter
from pathlib import Path
import json, time
from .core import R,S,orbit_RS,fingerprint,reach_count,positive_transport_checks,LAWS,SELECTED_FEATURES
HERE=Path(__file__).resolve().parent

def classify():
    start=time.perf_counter()
    remaining=set(product(range(3),repeat=9))
    families=[]
    while remaining:
        r=min(remaining);g=orbit_RS(r)
        assert g<=remaining
        remaining.difference_update(g)
        families.append((r,g))
    assert len(families)==1098
    census=Counter(len(g) for _,g in families)
    assert census==Counter({1:1,2:1,6:4,18:1092}),census
    labels={r:fingerprint(r) for r,g in families}
    assert len(set(labels.values()))==len(labels)==1098,'Four features did not distinguish all positive orbits'
    four_stage=[len(set(tuple(labels[r][:k]) for r in labels)) for k in range(1,5)]
    assert all(positive_transport_checks(r) for r,g in families)
    assert sum(reach_count(r)==243 for r,g in families)==1097
    positive=sum(len(g)**2 for _,g in families)
    answer={'declared_family':'All q: F3^2 -> F3 in the fixed F3^5 triangular A/B grammar',
            'laws':LAWS,'states':243,
            'positive_transport_orbits':len(families),
            'orbit_size_histogram':dict(sorted(census.items())),
            'four_linked_orbit_incidence_features':[
                {'from':p,'to':q,'shift':r} for p,q,r in SELECTED_FEATURES],
            'independent_signature_counts':four_stage,
            'exact_conjugacy_classes':1098,
            'ordered_positive_law_pairs':positive,
            'ordered_negative_law_pairs':LAWS*LAWS-positive,
            'transitive_orbit_representatives':1097,
            'nontransitive_zero_law_orbit_representatives':1,
            'representative_R_S_generator_intertwiners_verified':len(families)*2,
            'math_reason':'A/B transports provide positive conjugacies within each R,S orbit; four conjugacy-invariant fingerprints distinguish every orbit',
            'limits':'Only the declared finite family; no general action-group or arbitrary dimension claim',
            'runtime_seconds':round(time.perf_counter()-start,3),
            'representative_signatures':[
                {'law':list(r),'positive_orbit_size':len(g),
                 'features':[[list(k) for k in h] for h in labels[r]]} for r,g in families]}
    print(json.dumps({k:v for k,v in answer.items() if k!='representative_signatures'},indent=2))
    return answer
if __name__=='__main__':classify()
