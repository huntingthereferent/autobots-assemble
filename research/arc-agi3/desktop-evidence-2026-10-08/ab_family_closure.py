"""A/B closure over a witness family.

This is the family form of the same A/B operation:
- same referent;
- witnessed relations;
- witnessed continuation;
- retain only the smallest relation-set required for continuation closure.

Outputs remain admissible as referents in another A/B layer.
"""
from dataclasses import dataclass
from itertools import combinations
from collections import defaultdict

@dataclass(frozen=True)
class Occurrence:
    referent: object
    relations: tuple
    future: object

@dataclass(frozen=True)
class FamilyState:
    referent: object
    retained_names: tuple

def ab_family(occurrences):
    groups=defaultdict(list)
    for o in occurrences:
        groups[o.referent].append(o)

    out={}
    for referent,group in groups.items():
        futures={o.future for o in group}
        if len(futures)<=1:
            out[referent]=FamilyState(referent,())
            continue

        relation_names=sorted(set.intersection(*(set(dict(o.relations)) for o in group)))
        chosen=None
        for size in range(1,len(relation_names)+1):
            for subset in combinations(relation_names,size):
                buckets=defaultdict(set)
                for o in group:
                    rel=dict(o.relations)
                    key=tuple(rel[n] for n in subset)
                    buckets[key].add(o.future)
                if all(len(v)==1 for v in buckets.values()):
                    chosen=subset
                    break
            if chosen is not None:
                break

        if chosen is None:
            raise ValueError(("witness contract insufficient",referent))

        out[referent]=FamilyState(referent,chosen)
    return out

def project(o,state):
    rel=dict(o.relations)
    vals=tuple((n,rel[n]) for n in state.retained_names)
    return (state.referent,vals)
