"""Cross-depth A/B projection and hidden loops in constructed finite worlds.

A world at depth d+1 is a lift of its depth-d projection, NOT an equal
world. This is mathematical construction evidence, not a native ARC run.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass

from .alignment import discover_alignment
from .math import World

State = tuple[int, ...]


def project(state: State) -> State:
    """Forget the newest coordinate. No claim of bijective alignment."""
    if len(state) < 3:
        raise ValueError("projection requires depth at least three")
    return state[:-1]


@dataclass(frozen=True)
class ExtensionWitness:
    status: str
    depth: int
    lower_states: int
    upper_states: int
    fiber_sizes: tuple[int, ...]
    commute_edges_checked: int
    failure: str | None = None


def verify_extension(lower: World, higher: World) -> ExtensionWitness:
    """Exhaust every reachable edge and fiber of a declared one-step lift."""
    if higher.depth != lower.depth + 1 or higher.phi != lower.phi:
        return ExtensionWitness("UNKNOWN", lower.depth, 0, 0, (), 0,
                                "not the declared coordinate extension")
    base = lower.reachable()
    lifted = higher.reachable()
    fibers: Counter[State] = Counter()
    edges = 0
    for state in lifted:
        image = project(state)
        if image not in base:
            return ExtensionWitness("OPEN", lower.depth, len(base), len(lifted), (), edges,
                                    "lift projected outside reachable base")
        fibers[image] += 1
        for action in "AB":
            edges += 1
            if project(higher.step(state, action)) != lower.step(image, action):
                return ExtensionWitness("OPEN", lower.depth, len(base), len(lifted), (), edges,
                                        f"noncommuting {action} edge at {state}")
    if set(fibers) != set(base):
        return ExtensionWitness("OPEN", lower.depth, len(base), len(lifted), (), edges,
                                "not every reachable base state has a lift")
    sizes = tuple(sorted(set(fibers.values())))
    return ExtensionWitness("PROJECTED_NOT_BIJECTIVE" if len(lifted) != len(base)
                            else "TRIVIAL_FIBER", lower.depth, len(base), len(lifted),
                            sizes, edges)


@dataclass(frozen=True)
class HiddenLoop:
    status: str
    base_depth: int
    action_word: str
    start: State
    after_one: State
    after_two: State
    after_three: State
    failure: str | None = None


def shortest_hidden_loop(higher: World) -> HiddenLoop:
    """Find a shortest word returning its projected origin but moving in the fiber.

    The action word is a concrete witness. Repetition is checked three times;
    no universal claim about arbitrary extensions is inferred from it.
    """
    if higher.depth < 4:
        raise ValueError("requires a world with a higher-dimensional fiber")
    start = higher.origin
    queue = deque([start])
    parent: dict[State, tuple[State | None, str]] = {start: (None, "")}
    destination = None
    while queue:
        state = queue.popleft()
        if project(state) == project(start) and state != start:
            destination = state
            break
        for action in "AB":
            nxt = higher.step(state, action)
            if nxt not in parent:
                parent[nxt] = (state, action)
                queue.append(nxt)
    if destination is None:
        return HiddenLoop("TRIVIAL_FIBER", higher.depth - 1, "", start, start, start, start)
    parts = []
    current = destination
    while current != start:
        previous, action = parent[current]
        parts.append(action)
        current = previous  # type: ignore[assignment]
    word = "".join(reversed(parts))

    def run(state: State) -> State:
        for action in word:
            state = higher.step(state, action)
        return state

    first = run(start)
    second = run(first)
    third = run(second)
    if (first != destination or first == start or second in (start, first)
            or third != start or project(first) != project(start)
            or project(second) != project(start)):
        return HiddenLoop("OPEN", higher.depth - 1, word, start, first, second, third,
                          "fiber translation failed the three-turn witness")
    return HiddenLoop("THREE_TURN_FIBER_LOOP", higher.depth - 1, word,
                      start, first, second, third)


@dataclass(frozen=True)
class AlignmentSquare:
    status: str
    higher_pairs: int
    lower_pairs: int
    failure: str | None = None


def verify_alignment_square(lower_a: World, lower_b: World) -> AlignmentSquare:
    """Do discovered same-depth A/B alignments commute with vertical projection?"""
    if lower_a.depth != lower_b.depth or lower_a.phi[0] != 0 or lower_b.phi[0] != 0:
        return AlignmentSquare("UNKNOWN", 0, 0, "incompatible lower worlds")
    upper_a = World(lower_a.depth + 1, lower_a.phi)
    upper_b = World(lower_b.depth + 1, lower_b.phi)
    bottom = discover_alignment(lower_a, lower_b)
    top = discover_alignment(upper_a, upper_b)
    if not bottom.aligned or not top.aligned:
        return AlignmentSquare("OPEN", len(top.pairs), len(bottom.pairs),
                               "a required same-depth alignment fails")
    lower_map = dict(bottom.pairs)
    for before, after in top.pairs:
        if project(after) != lower_map[project(before)]:
            return AlignmentSquare("OPEN", len(top.pairs), len(bottom.pairs),
                                   f"alignment-projection square fails at {before}")
    return AlignmentSquare("COMMUTING_SQUARE", len(top.pairs), len(bottom.pairs))
