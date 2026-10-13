"""Independent pure finite reference for multi-task source incidence.

A dependency graph can select required replay; it cannot certify owner pins,
validate finite transitions, or promote cached task outcomes to proof.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskImpactPlan:
    changed: tuple[str,...]
    replay: tuple[str,...]
    cached: tuple[str,...]
    impact: tuple[tuple[str,tuple[str,...]],...]
    outcomes: tuple[tuple[str,str],...]


def plan(tasks: dict[str,tuple[str,...]], changed: tuple[str,...], *, force=()):
    if (type(tasks) is not dict or not 2<=len(tasks)<=16 or
        any(type(name) is not str or not name or type(deps) is not tuple or
            not deps or len(set(deps))!=len(deps) or
            not all(type(s) is str and s for s in deps) for name,deps in tasks.items()) or
        type(changed) is not tuple or len(set(changed))!=len(changed) or
        any(type(s) is not str for s in changed) or
        type(force) is not tuple or len(set(force))!=len(force) or
        any(type(t) is not str or t not in tasks for t in force)):
        raise ValueError('invalid finite dependencies or replay selection')
    sources=set.union(*(set(v) for v in tasks.values()))
    if any(s not in sources for s in changed):
        raise ValueError('unknown source')
    impact=tuple((n,tuple(s for s in changed if s in dep))
                 for n,dep in tasks.items())
    replay=tuple(n for n,delta in impact if delta or n in force)
    cached=tuple(n for n in tasks if n not in replay)
    return TaskImpactPlan(changed,replay,cached,impact,
        tuple((n,'REPLAY_REQUIRED' if n in replay else 'CACHED_NOT_REPLAYED')
              for n in tasks))
