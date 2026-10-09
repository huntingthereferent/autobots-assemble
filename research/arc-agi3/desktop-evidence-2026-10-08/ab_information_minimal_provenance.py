"""Information-minimal A/B provenance.

After grouping source aliases by identical occurrence partition, remove any
proof partition that is strictly finer than another sufficient proof partition.

The survivors are the minimal sufficient partitions under refinement.
"""
from dataclasses import dataclass
from ab_partition_provenance import source_alias_classes

def refines(fine,coarse):
    # Every fine block is contained in some coarse block.
    C=[set(b) for b in coarse]
    return all(any(set(b).issubset(c) for c in C) for b in fine)

def strictly_refines(fine,coarse):
    return fine!=coarse and refines(fine,coarse)

def information_minimal_provenance(group,family_state):
    q=source_alias_classes(group,family_state)
    keep=[]
    for c in q.alias_classes:
        # c is redundant if some other sufficient partition is strictly coarser.
        if any(strictly_refines(c.occurrence_partition,d.occurrence_partition)
               for d in q.alias_classes if d is not c):
            continue
        keep.append(c)
    return q.referent,tuple(keep)
