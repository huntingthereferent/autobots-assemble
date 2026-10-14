"""Pure finite dependency projection for bounded selective certificate auditing.

This is an orchestration/reference model, not an owner-pinned or edge-observing
implementation. A skipped certificate is NOT a freshly witnessed mathematical result.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshPlan:
    dirty_sources: tuple[str,...]
    audited: tuple[str,...]
    skipped: tuple[str,...]
    dependent_on: tuple[tuple[str,tuple[str,...]],...]
    candidate_status: tuple[tuple[str,str],...]


def plan(dependencies: dict[str,tuple[str,...]], changes: tuple[str,...],
         cached: dict[str,str], *, force=()):
    if (type(dependencies) is not dict or not 2<=len(dependencies)<=16 or
        set(dependencies)!=set(cached) or
        any(type(k) is not str or type(d) is not tuple or not d or
            len(set(d))!=len(d) or not all(type(s) is str and s for s in d)
            for k,d in dependencies.items()) or
        type(changes) is not tuple or len(set(changes))!=len(changes) or
        not all(type(s) is str for s in changes) or
        any(s not in set.union(*[set(x) for x in dependencies.values()]) for s in changes) or
        any(n not in dependencies for n in force)):
        raise ValueError('explicit finite certificate dependencies and valid dirty sources required')
    impact=tuple((name,tuple(s for s in changes if s in deps))
                  for name,deps in dependencies.items())
    audited=tuple(n for n,dirty in impact if dirty or n in force)
    skipped=tuple(n for n in dependencies if n not in audited)
    # Unknown until the caller replays; do not infer validity from graph alone.
    status=tuple((n,'REPLAY_REQUIRED' if n in audited else
                  'CACHED_NOT_REPLAYED') for n in dependencies)
    return RefreshPlan(changes,audited,skipped,impact,status)


if __name__=='__main__':
    deps={'left_and_right':('donor','left_mid','right_mid','final'),
          'other':('separate_old','separate_new')}
    print(plan(deps,('right_mid',),{'left_and_right':'CONFLICT','other':'AGREEMENT'}))
