"""Small finite witnesses for inverse A/B construction and relational alignment.

A/B is not defined by this sample model. The finite F_3 constructions are
candidate worlds produced from declared relations, not observed ARC games.
"""
from collections import deque
from dataclasses import dataclass
from itertools import product
from typing import Callable

State = tuple[int, ...]
Alignment = Callable[[State], State]


@dataclass(frozen=True)
class World:
    depth: int
    phi: tuple[int, int, int] = (0, 1, 2)

    def __post_init__(self):
        if self.depth < 2:
            raise ValueError("depth must be at least two")
        if len(self.phi) != 3 or any(v not in range(3) for v in self.phi):
            raise ValueError("phi must be three values in F_3")

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def step(self, state: State, action: str) -> State:
        if len(state) != self.depth or any(v not in range(3) for v in state):
            raise ValueError("invalid state")
        out = list(state)
        if action == "A":
            out[0] = (state[0] + 1) % 3
        elif action == "B":
            out[1] = (state[1] + state[0] + 1) % 3
            if self.depth >= 3:
                out[2] = (state[2] + self.phi[state[1]]) % 3
            for index in range(3, self.depth):
                out[index] = (state[index] + state[index - 1]) % 3
        else:
            raise ValueError("only A and B are admitted")
        return tuple(out)

    def reachable(self) -> frozenset[State]:
        seen = {self.origin}
        frontier = deque([self.origin])
        while frontier:
            state = frontier.popleft()
            for action in "AB":
                new = self.step(state, action)
                if new not in seen:
                    seen.add(new)
                    frontier.append(new)
        return frozenset(seen)

    def apply(self, actions: str) -> State:
        state = self.origin
        for action in actions:
            state = self.step(state, action)
        return state


def inverse_candidates() -> tuple[World, ...]:
    """Construct, don't observe: nine candidate 3D relations with phi(0)=0."""
    return tuple(World(3, (0, a, b)) for a, b in product(range(3), repeat=2))


@dataclass(frozen=True)
class AlignmentResult:
    aligned: bool
    source_count: int
    target_count: int
    failure: str | None


def align_worlds(source: World, target: World, mapping: Alignment) -> AlignmentResult:
    """Check rooted, bijective A/B transition conjugacy on *all reachable* states.

    The states need not match literally. A mere projection/quotient is not
    accepted as full world alignment, even when every projected edge commutes.
    """
    src, dst = source.reachable(), target.reachable()
    failure = None
    try:
        images = {state: mapping(state) for state in src}
        if images[source.origin] != target.origin:
            failure = "origin does not align"
        elif len(src) != len(dst) or set(images.values()) != set(dst):
            failure = "not a bijection of reachable worlds"
        else:
            for state in sorted(src):
                for action in "AB":
                    if mapping(source.step(state, action)) != target.step(images[state], action):
                        failure = f"transition fails at {state} via {action}"
                        break
                if failure:
                    break
    except (TypeError, ValueError, KeyError, IndexError) as error:
        failure = f"invalid alignment: {type(error).__name__}"
    return AlignmentResult(failure is None, len(src), len(dst), failure)


def verify_recurrence(worlds: tuple[World, ...], maps: tuple[Alignment, ...]) -> str:
    """Finite prefix test only; never a proof that all future turns close.

    A one-pair return is preliminary; at least one further construction must
    preserve the alignment. A finite prefix can only produce a *candidate*.
    """
    if len(worlds) < 2 or len(maps) != len(worlds) - 1:
        return "UNKNOWN: missing worlds or alignment witnesses"
    results = [align_worlds(a, b, mapping) for a, b, mapping in zip(worlds, worlds[1:], maps)]
    if any(not result.aligned for result in results):
        return "OPEN: alignment breaks"
    if len(results) == 1:
        return "CANDIDATE: one aligned construction, next layer untested"
    return "CANDIDATE_NEXT_LAYER_VERIFIED: finite recurrence only, not terminal closure"


def rescale_last(state: State) -> State:
    """Explicit alignment between 3D phi=(0,1,2) and phi=(0,2,1)."""
    if len(state) != 3:
        raise ValueError("rescaling witness requires three dimensions")
    return (state[0], state[1], (2 * state[2]) % 3)
