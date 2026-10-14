"""Pure finite dependency selection for two route certificates.

This model has no owner authentication or live transition replay. It selects
which certificates REQUIRE the integrated owner-backed audit; a skipped
certificate is always historical cache, never currently proved.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class DependencyDecision:
    affected: tuple[str, ...]
    skipped: tuple[str, ...]
    comparison_usable: bool
    modes: tuple[tuple[str,str], ...]


def select_routes(before, after, *, changed_declaration=False, force=()):
    """Stamps map donor/left_middle/right_middle/final to opaque evidence values.

    The values are supplied by the caller, NOT verified by this model.
    """
    names=('donor','left_middle','right_middle','final')
    if (type(before) is not dict or type(after) is not dict or
        set(before)!=set(names) or set(after)!=set(names) or
        type(changed_declaration) is not bool or type(force) is not tuple or
        len(set(force))!=len(force) or any(x not in ('left','right') for x in force)):
        raise ValueError('exact four-node dependency graph and valid route selection required')
    changed={name for name in names if before[name]!=after[name]}
    selected=set(force)
    if changed_declaration or changed.intersection(('donor','final')):
        selected.update(('left','right'))
    if 'left_middle' in changed:selected.add('left')
    if 'right_middle' in changed:selected.add('right')
    affected=tuple(name for name in ('left','right') if name in selected)
    skipped=tuple(name for name in ('left','right') if name not in selected)
    return DependencyDecision(affected,skipped,False,
        tuple((name,'REQUIRES_REPLAY' if name in selected else 'CACHED_NOT_REPLAYED')
              for name in ('left','right')))

if __name__=='__main__':
    b=dict(donor=1,left_middle=1,right_middle=1,final=1)
    a=dict(b,right_middle=2)
    print(select_routes(b,a))
