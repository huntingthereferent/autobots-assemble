"""An independent negative census using four INCOMPLETE original invariants
followed by exhaustive transitive labeled-graph correspondence on remaining pairs.
Unlike verify.py, it does not rely on the four new COMPLETE fingerprints.
"""
from .core import old_four, orbit_RS, find_conjugacy, reach_count
from itertools import product, combinations
from collections import Counter,defaultdict
from pathlib import Path
import json,time
HERE=Path(__file__).resolve().parent

def main():
    start=time.perf_counter()
    remaining=set(product(range(3),repeat=9)); reps=[]
    while remaining:
        rep=min(remaining);members=orbit_RS(rep)
        remaining.difference_update(members);reps.append(rep)
    assert len(reps)==1098
    groups=defaultdict(list)
    for q in reps:groups[old_four(q)].append(q)
    assert len(groups)==738
    collisions=[g for g in groups.values() if len(g)>1]
    assert len(collisions)==222
    pairs=[p for group in collisions for p in combinations(group,2)]
    assert len(pairs)==621,len(pairs)
    checks=0
    for a,b in pairs:
        if reach_count(a)!=243 or reach_count(b)!=243:
            raise AssertionError('cannot exhaust using one root on nontransitive graph')
        conj,trials=find_conjugacy(a,b)
        assert conj is None and trials==243,(a,b)
        checks+=trials
    assert checks==150903
    report={'declared_laws':19683,'R_S_positive_orbits':1098,
            'incomplete_four_fingerprint_groups':len(groups),
            'ambiguous_fingerprint_groups':len(collisions),
            'fully_checked_between_orbit_pairs':len(pairs),
            'candidate_origin_images_exhausted':checks,
            'extra_conjugacies_between_R_S_orbits':0,
            'verified_full_conjugacy_classes':1098,
            'independent_of_new_complete_four_feature_catalog':True,
            'runtime_seconds':round(time.perf_counter()-start,3)}
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
