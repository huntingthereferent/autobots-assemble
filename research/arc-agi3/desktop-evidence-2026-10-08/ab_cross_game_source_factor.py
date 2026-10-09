"""A/B one layer above minimal witness sets: factor common relation core from alternative witness family."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SourceFamily:
    sources: tuple

@dataclass(frozen=True)
class FactoredFamily:
    common: tuple
    residuals: tuple

def factor_family(f):
    sets=[set(s) for s in f.sources]
    common=set.intersection(*sets) if sets else set()
    residuals=tuple(sorted(tuple(sorted(set(s)-common)) for s in f.sources))
    return FactoredFamily(tuple(sorted(common)),residuals)

DC22=SourceFamily((
    ("prev_action2",),
    ("prev_obs1",),
    ("prev_obs2",),
))
CD82=SourceFamily((
    ("prev_action1","prev_action2"),
    ("prev_action1","prev_obs1"),
    ("prev_action1","prev_obs2"),
))

d=factor_family(DC22)
c=factor_family(CD82)
print("DC22",d)
print("CD82",c)

# A/B across the source families:
# preserve the residual alternative family because it is exactly shared;
# retain prev_action1 only on CD82 because that is the witnessed difference.
assert d.residuals==c.residuals
assert d.common==()
assert c.common==("prev_action1",)

print("SHARED_RESIDUAL",d.residuals)
print("CD82_EXTRA_CORE",c.common)
print("PASS source-family A/B: CD82 = prev_action1 + DC22 residual family")
