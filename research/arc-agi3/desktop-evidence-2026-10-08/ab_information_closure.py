"""Direct information-minimal A/B closure.

Search all witnessed relation subsets.
A candidate is sufficient iff its induced occurrence partition is future-pure.
Among sufficient candidates, retain only partitions that are not strict
refinements of another sufficient partition.

All source subsets inducing the same surviving partition are provenance aliases.
"""
from dataclasses import dataclass
from itertools import combinations
from collections import defaultdict

@dataclass(frozen=True)
class InfoProof:
    partition: tuple
    sources: tuple

@dataclass(frozen=True)
class InfoABState:
    referent: object
    proofs: tuple

def partition_for(group,subset):
    buckets=defaultdict(list)
    for i,o in enumerate(group):
        rel=dict(o.relations)
        key=tuple((n,rel[n]) for n in subset)
        buckets[key].append(i)
    return tuple(sorted(tuple(v) for v in buckets.values()))

def sufficient(group,partition):
    for block in partition:
        fut={group[i].future for i in block}
        if len(fut)>1:return False
    return True

def refines(fine,coarse):
    C=[set(b) for b in coarse]
    return all(any(set(b).issubset(c) for c in C) for b in fine)

def info_ab_group(group):
    ref=group[0].referent
    futures={o.future for o in group}
    if len(futures)<=1:
        p=(tuple(range(len(group))),)
        return InfoABState(ref,(InfoProof(p,((),)),))

    names=sorted(set.intersection(*(set(dict(o.relations)) for o in group)))
    by_partition=defaultdict(list)

    # Enumerate all non-empty source subsets. Relation count has no priority.
    for size in range(1,len(names)+1):
        for subset in combinations(names,size):
            p=partition_for(group,subset)
            if sufficient(group,p):
                by_partition[p].append(subset)

    if not by_partition:
        raise ValueError(("witness contract insufficient",ref))

    parts=list(by_partition)
    survivors=[]
    for p in parts:
        # Drop p if it is strictly finer than another sufficient partition q.
        if any(p!=q and refines(p,q) for q in parts):
            continue
        survivors.append(p)

    proofs=[]
    for p in survivors:
        raw=sorted(by_partition[p],key=lambda s:(len(s),s))
        minimal=[]
        for s in raw:
            ss=set(s)
            if any(set(m).issubset(ss) for m in minimal):
                continue
            minimal.append(s)
        proofs.append(InfoProof(p,tuple(minimal)))
    proofs.sort(key=lambda x:(len(x.partition),x.partition,x.sources))
    return InfoABState(ref,tuple(proofs))
