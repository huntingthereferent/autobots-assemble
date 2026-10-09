"""Partition-aware A/B provenance.

Minimal source sets that induce exactly the same partition of witnessed
occurrences are aliases for that referent.

Different partitions that predict the same continuation remain alternative
proof classes, not aliases.
"""
from dataclasses import dataclass
from collections import defaultdict
from ab_family_all_minima import separator_values

@dataclass(frozen=True)
class AliasClass:
    sources: tuple
    occurrence_partition: tuple

@dataclass(frozen=True)
class ProvenanceQuotient:
    referent: object
    alias_classes: tuple

def _partition(group,subset):
    buckets=defaultdict(list)
    for i,o in enumerate(group):
        key=separator_values(o,subset)
        buckets[key].append(i)
    return tuple(sorted(tuple(v) for v in buckets.values()))

def source_alias_classes(group,family_state):
    by_partition=defaultdict(list)
    for subset in family_state.minimal_separator_sets:
        p=_partition(group,subset)
        by_partition[p].append(subset)

    classes=[]
    for p,sources in by_partition.items():
        classes.append(AliasClass(tuple(sorted(sources)),p))
    classes.sort(key=lambda c:(len(c.occurrence_partition),c.occurrence_partition,c.sources))
    return ProvenanceQuotient(family_state.referent,tuple(classes))
