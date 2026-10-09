"""Discover rooted A/B alignments and certify a declared finite construction loop.

These are mathematical model witnesses, not ARC gameplay or live observations.
A closed family means only closed under the explicitly supplied constructor.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable

from .math import State, World, inverse_candidates


@dataclass(frozen=True)
class DiscoveredAlignment:
    status: str  # ALIGNED / OPEN / UNKNOWN
    pairs: tuple[tuple[State, State], ...]
    failure: str | None = None
    conflicting_words: tuple[str, str] | None = None

    @property
    def aligned(self) -> bool:
        return self.status == "ALIGNED"


def discover_alignment(source: World, target: World, *, max_states: int = 10000) -> DiscoveredAlignment:
    """Discover the unique origin-preserving, action-label-preserving alignment.

    Determinism and reachability force the image of every state via its action
    word. Conflicting words give a concrete counterexample to equivalence.
    Exhausting reachable states checks every A and B transition, not a sample.
    """
    if max_states < 1:
        raise ValueError("max_states must be positive")
    forward = {source.origin: target.origin}
    reverse = {target.origin: source.origin}
    words = {source.origin: ""}
    queue = deque([source.origin])

    def result(status: str, failure: str | None = None,
               conflict: tuple[str, str] | None = None) -> DiscoveredAlignment:
        return DiscoveredAlignment(status, tuple(forward.items()), failure, conflict)

    while queue:
        state = queue.popleft()
        image = forward[state]
        for action in "AB":
            src_next = source.step(state, action)
            dst_next = target.step(image, action)
            word = words[state] + action
            if src_next in forward:
                if forward[src_next] != dst_next:
                    return result("OPEN", "same source state, different target state",
                                  (words[src_next], word))
            elif dst_next in reverse:
                return result("OPEN", "different source states, same target state",
                              (words[reverse[dst_next]], word))
            else:
                if len(forward) >= max_states:
                    return result("UNKNOWN", "state exploration limit reached")
                forward[src_next] = dst_next
                reverse[dst_next] = src_next
                words[src_next] = word
                queue.append(src_next)
    return result("ALIGNED")


def equivalent_classes(worlds: tuple[World, ...], *, max_states: int = 10000) -> tuple[tuple[World, ...], ...]:
    """Partition a finite candidate set by discovered exact A/B alignment.

    Raises if a configured exploration budget prevents definite classification.
    """
    remaining = list(worlds)
    groups = []
    while remaining:
        representative = remaining.pop(0)
        group = [representative]
        rest = []
        for other in remaining:
            alignment = discover_alignment(representative, other, max_states=max_states)
            if alignment.status == "UNKNOWN":
                raise ValueError("candidate classification requires more exploration budget")
            (group if alignment.aligned else rest).append(other)
        groups.append(tuple(group))
        remaining = rest
    return tuple(groups)


def scale_construction(world: World) -> World:
    """Invert by composing third-and-higher coordinate units with scalar 2.

    Finite-field witness: 2*2 == 1 (mod 3). No existing-world
    observation drives this next construction; the relation operator does.
    """
    return World(world.depth, tuple((2 * value) % 3 for value in world.phi))


@dataclass(frozen=True)
class ClosureCertificate:
    status: str
    family_size: int
    aligned_edges: int
    cycles: tuple[tuple[World, ...], ...] = ()
    failure: str | None = None
    conflicting_words: tuple[str, str] | None = None


def certify_finite_family(
    worlds: tuple[World, ...],
    constructor: Callable[[World], World],
    *,
    max_states: int = 10000,
) -> ClosureCertificate:
    """Prove a finite closed *declared family*, never global inverse A/B closure.

    Requires every successor to be in the family, all rooted transition graphs
    aligned, and a permutation of the finite family (all members on cycles).
    Induction on the finite successor map proves indefinite recurrence *within
    the named family and constructor*, not under arbitrary other constructions.
    """
    if not worlds or len(set(worlds)) != len(worlds):
        return ClosureCertificate("UNKNOWN", len(worlds), 0,
                                  failure="family must be nonempty and duplicate-free")
    allowed = set(worlds)
    successors = {}
    checked = 0
    for world in worlds:
        successor = constructor(world)
        if successor not in allowed:
            return ClosureCertificate("OPEN", len(worlds), checked,
                                      failure=f"constructor leaves declared family at {world}")
        witness = discover_alignment(world, successor, max_states=max_states)
        if not witness.aligned:
            return ClosureCertificate(witness.status, len(worlds), checked,
                                      failure=f"{world} -> {successor}: {witness.failure}",
                                      conflicting_words=witness.conflicting_words)
        successors[world] = successor
        checked += 1
    if set(successors.values()) != allowed:
        return ClosureCertificate("OPEN", len(worlds), checked,
                                  failure="constructor is not a permutation; some members are transient")
    cycles = []
    visited = set()
    for world in worlds:
        if world in visited:
            continue
        cycle = []
        current = world
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = successors[current]
        if current != world:
            return ClosureCertificate("OPEN", len(worlds), checked,
                                      failure="successor orbit merged into another orbit")
        cycles.append(tuple(cycle))
    return ClosureCertificate("CLOSED_FOR_DECLARED_FAMILY", len(worlds), checked, tuple(cycles))


def certify_inverse_candidates() -> ClosureCertificate:
    """Exhaust the nine candidate 3D relations under the declared scale rule."""
    return certify_finite_family(inverse_candidates(), scale_construction)
