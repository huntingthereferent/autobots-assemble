"""Minimal-witness antichains as reusable A/B objects.

Each minimal separator set is one hyperedge.
A source family is the antichain of all minimal hyperedges.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class WitnessAntichain:
    edges: tuple

    @staticmethod
    def make(edges):
        canon=sorted({tuple(sorted(e)) for e in edges},key=lambda x:(len(x),x))
        # remove any nonminimal supersets
        out=[]
        for e in canon:
            se=set(e)
            if any(set(k).issubset(se) for k in out):
                continue
            out.append(e)
        return WitnessAntichain(tuple(out))

@dataclass(frozen=True)
class ABComparison:
    shared_edges: WitnessAntichain
    left_only: WitnessAntichain
    right_only: WitnessAntichain

def ab_compare(left,right):
    L=set(left.edges);R=set(right.edges)
    return ABComparison(
        WitnessAntichain.make(L&R),
        WitnessAntichain.make(L-R),
        WitnessAntichain.make(R-L),
    )

def common_core(family):
    if not family.edges:return ()
    c=set(family.edges[0])
    for e in family.edges[1:]:c &= set(e)
    return tuple(sorted(c))

def factor_core(family):
    core=set(common_core(family))
    residual=[tuple(sorted(set(e)-core)) for e in family.edges]
    return tuple(sorted(core)),WitnessAntichain.make(residual)
