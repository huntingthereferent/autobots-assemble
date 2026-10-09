from dataclasses import dataclass
from itertools import combinations

@dataclass(frozen=True)
class Witness:
    referent: object
    relations: tuple
    future: object

@dataclass(frozen=True)
class ABOutput:
    referent: object
    retained: tuple

def ab(a,b):
    if a.referent != b.referent:
        return ABOutput(a.referent,()),ABOutput(b.referent,())
    if a.future == b.future:
        s=ABOutput(a.referent,())
        return s,s
    ar=dict(a.relations); br=dict(b.relations)
    names=sorted(set(ar)&set(br))
    differing=[n for n in names if ar[n] != br[n]]
    for size in range(1,len(differing)+1):
        for subset in combinations(differing,size):
            ka=tuple((n,ar[n]) for n in subset)
            kb=tuple((n,br[n]) for n in subset)
            if ka != kb:
                return ABOutput(a.referent,ka),ABOutput(b.referent,kb)
    raise ValueError("witness contract insufficient")
