"""A/B predictive refinement.

A/B compares two witnessed state occurrences under one action/evidence contract.
If their current observations are equal but their continuations differ, the
smallest witnessed relation that separates the continuations is retained.

The returned state is reusable as an input to the same operation.
"""

from dataclasses import dataclass
from typing import Hashable, Mapping

@dataclass(frozen=True)
class WitnessedState:
    current: Hashable
    predecessor: Hashable | None
    futures: tuple

@dataclass(frozen=True)
class ABState:
    current: Hashable
    retained: tuple[tuple[str, Hashable | None], ...]

def ab(a: WitnessedState, b: WitnessedState) -> tuple[ABState, ABState]:
    if a.current != b.current:
        # The visible referent already separates them.
        return (
            ABState(a.current, ()),
            ABState(b.current, ()),
        )

    if a.futures == b.futures:
        # No witnessed continuation distinction: collapse to the shared referent.
        s=ABState(a.current, ())
        return s,s

    # Same current referent, different futures.
    # Retain predecessor iff it is a witnessed separating relation.
    if a.predecessor != b.predecessor:
        return (
            ABState(a.current, (("predecessor",a.predecessor),)),
            ABState(b.current, (("predecessor",b.predecessor),)),
        )

    raise ValueError("current + predecessor still insufficient; lift one relation higher")

def equivalent(a: ABState,b: ABState)->bool:
    return a==b
