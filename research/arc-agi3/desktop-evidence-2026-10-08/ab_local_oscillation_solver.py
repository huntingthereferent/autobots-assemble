"""
Stay at THIS layer.
A created relation gets only its reciprocal oscillation.  If that oscillation
does not resolve locally, STOP: that is the drift witness and rebuild here.
No frontier, no breadth expansion, no search-space completion.
"""
from dataclasses import dataclass
@dataclass(frozen=True)
class Return:
    left: bytes
    right: bytes
    forward: tuple
    reverse: tuple
    invariant: tuple
    complete: bool
    drift: str|None=None

def local_oscillation(x, move, apply, witness):
    # x --move--> y
    y, wy = apply(x, move)
    f = witness(x,y,move,wy)
    # relation itself must supply its reciprocal; caller may not choose a new
    # exploratory action here.
    inv = f.get("reciprocal")
    if inv is None:
        return Return(x,y,f,(),(),False,"NO_WITNESSED_RECIPROCAL")
    # y --reciprocal--> z
    z, wz = apply(y, inv)
    r = witness(y,z,inv,wz)
    # Completion belongs to this oscillation only.
    shared=tuple(sorted(set(f.get("features",())) & set(r.get("features",()))))
    if not shared:
        return Return(x,y,f,r,(),False,"OSCILLATION_DID_NOT_RETURN_INVARIANT")
    return Return(x,y,f,r,shared,True)

# HARD BOUNDARY:
# A failed local oscillation is not permission to:
# - enumerate another action
# - add y/z to a frontier
# - broaden the representation
# - invent a semantic completion target
# It returns DRIFT at this same layer so the solver is rebuilt from the witness.
