"""Recursive A/B object for source-family structure."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AltFamily:
    alternatives: tuple

@dataclass(frozen=True)
class LayeredSource:
    core: tuple
    residual: AltFamily

def normalize_sources(sources):
    sets=[set(s) for s in sources]
    common=set.intersection(*sets) if sets else set()
    residuals=tuple(sorted(tuple(sorted(set(s)-common)) for s in sources))
    return LayeredSource(tuple(sorted(common)),AltFamily(residuals))

dc=normalize_sources((
 ("prev_action2",),("prev_obs1",),("prev_obs2",)
))
cd=normalize_sources((
 ("prev_action1","prev_action2"),
 ("prev_action1","prev_obs1"),
 ("prev_action1","prev_obs2"),
))
print("DC",dc)
print("CD",cd)

# Recursive reuse: the residual family is itself now the referent.
assert dc.residual==cd.residual
R=dc.residual
print("REUSED_REFERENT",R)

# Compare the two layered states at the next A/B layer.
# Shared referent R survives; only core differs.
pair=(("DC22",dc.core),("CD82",cd.core))
print("NEXT_LAYER",pair)
assert pair[0][1]==()
assert pair[1][1]==("prev_action1",)

print("PASS recursive source-family object")
