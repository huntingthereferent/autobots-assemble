"""Recursive A/B relation closure.

A/B is not a classifier over whether refinement is possible.
It is the recursively reusable operation.

Given witnessed occurrences:
1. preserve the referent actually shared;
2. compare available relations under the same continuation contract;
3. retain the smallest relation-set that preserves the witnessed distinction;
4. feed that output back as the next valid input;
5. repeat until no continuation distinction remains.

Older layers remain evidence only.
"""

from dataclasses import dataclass
from itertools import combinations

@dataclass(frozen=True)
class Witness:
    referent: object
    relations: tuple
    future: object

@dataclass(frozen=True)
class ABState:
    referent: object
    retained: tuple

def _minimal_separator(a_rel,b_rel):
    ar=dict(a_rel); br=dict(b_rel)
    names=sorted(set(ar)&set(br))
    differing=[n for n in names if ar[n]!=br[n]]
    for size in range(1,len(differing)+1):
        for subset in combinations(differing,size):
            ka=tuple((n,ar[n]) for n in subset)
            kb=tuple((n,br[n]) for n in subset)
            if ka!=kb:
                return ka,kb
    return (),()

def ab(a,b):
    # Different current referents already carry the distinction.
    if a.referent != b.referent:
        return ABState(a.referent,()),ABState(b.referent,())

    # Same continuation: shared referent closes this comparison.
    if a.future == b.future:
        s=ABState(a.referent,())
        return s,s

    # Same referent, different continuation:
    # retain the minimum witnessed relation-set that preserves the difference.
    ra,rb=_minimal_separator(a.relations,b.relations)

    # If the current relation layer contains no separator, lift the whole
    # witnessed relation tuple as the next referent and continue recursively.
    if not ra and not rb:
        na=Witness(a.relations,(),a.future)
        nb=Witness(b.relations,(),b.future)
        return ab(na,nb)

    return ABState(a.referent,ra),ABState(b.referent,rb)

def recurse(a,b,next_relations_a=(),next_relations_b=(),next_future_a=None,next_future_b=None):
    xa,xb=ab(a,b)
    if next_future_a is None or next_future_b is None:
        return xa,xb
    return ab(
        Witness(xa,next_relations_a,next_future_a),
        Witness(xb,next_relations_b,next_future_b),
    )
