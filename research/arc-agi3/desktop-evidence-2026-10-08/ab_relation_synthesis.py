"""A/B relation synthesis when the available relation vocabulary cannot realize
the continuation-equivalence quotient.

The synthesized relation is not chosen from old field names. It is the witnessed
merge from the best available proof partition to the continuation partition.
"""
from dataclasses import dataclass
from collections import defaultdict

@dataclass(frozen=True)
class SynthesizedRelation:
    referent: object
    proof_partition: tuple
    continuation_partition: tuple
    proof_to_class: tuple

def future_partition(group):
    buckets=defaultdict(list)
    for i,o in enumerate(group):
        buckets[repr(o.future)].append(i)
    return tuple(sorted(tuple(v) for v in buckets.values()))

def synthesize_relation(referent,proof_partition,group):
    target=future_partition(group)

    # Every proof block is future-pure, so it must lie wholly inside one target block.
    target_sets=[set(b) for b in target]
    mapping=[]
    for j,pb in enumerate(proof_partition):
        P=set(pb)
        hits=[k for k,T in enumerate(target_sets) if P.issubset(T)]
        if len(hits)!=1:
            raise ValueError(("proof block not continuation-pure",pb,hits))
        mapping.append((j,hits[0]))

    return SynthesizedRelation(
        referent,
        proof_partition,
        target,
        tuple(mapping),
    )

def apply_synthesized(rel,occurrence_index):
    proof_idx=next(i for i,b in enumerate(rel.proof_partition) if occurrence_index in b)
    return dict(rel.proof_to_class)[proof_idx]
