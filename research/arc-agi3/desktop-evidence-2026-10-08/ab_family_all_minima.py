from dataclasses import dataclass
from itertools import combinations
from collections import defaultdict

@dataclass(frozen=True)
class Occurrence:
    referent: object
    relations: tuple
    future: object

@dataclass(frozen=True)
class ABFamilyState:
    referent: object
    minimal_separator_sets: tuple
    future_classes: tuple

def _minimal_sets(group):
    if len({o.future for o in group})<=1:
        return ((),)
    names=sorted(set.intersection(*(set(dict(o.relations)) for o in group)))
    good=[]
    for size in range(1,len(names)+1):
        for subset in combinations(names,size):
            buckets=defaultdict(set)
            for o in group:
                rel=dict(o.relations)
                key=tuple(rel[n] for n in subset)
                buckets[key].add(o.future)
            if all(len(v)==1 for v in buckets.values()):
                good.append(subset)
        if good:
            return tuple(good)
    raise ValueError("witness contract insufficient")

def ab_family_all(occurrences):
    groups=defaultdict(list)
    for o in occurrences:groups[o.referent].append(o)
    out={}
    for ref,g in groups.items():
        mins=_minimal_sets(g)
        futures=tuple(sorted({repr(o.future):o.future for o in g}.items(),key=lambda x:x[0]))
        out[ref]=ABFamilyState(ref,mins,tuple(v for k,v in futures))
    return out

def separator_values(o,subset):
    rel=dict(o.relations)
    return tuple((n,rel[n]) for n in subset)

def predictive_class_map(group,state):
    # Every minimal separator must induce the same future partition on the witness family.
    maps=[]
    for subset in state.minimal_separator_sets:
        m={}
        for o in group:
            key=separator_values(o,subset)
            prev=m.get(key,o.future)
            if prev!=o.future:raise ValueError(("separator not predictive",subset,key))
            m[key]=o.future
        maps.append((subset,m))
    return tuple(maps)
