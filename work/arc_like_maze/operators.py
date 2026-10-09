"""A higher mathematical layer: construction operators on inverse A/B worlds.

Finite F_3 witness only. Construction moves are not ARC gameplay actions.
Proves finite closure only for explicit operator families; detects when
original A/B equivalence is NOT respected by an added construction rule.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .alignment import discover_alignment, equivalent_classes
from .math import World, inverse_candidates


@dataclass(frozen=True)
class Operator:
    name: str
    matrix: tuple[tuple[int, int], tuple[int, int]]
    offset: tuple[int, int] = (0, 0)

    def __post_init__(self) -> None:
        if not self.name or len(self.matrix) != 2 or any(len(row) != 2 for row in self.matrix):
            raise ValueError("an operator requires a name and 2x2 matrix")
        if len(self.offset) != 2:
            raise ValueError("operator needs a two-coordinate offset")
        if any(not isinstance(v, int) or not 0 <= v <= 2
               for row in self.matrix for v in row):
            raise ValueError("matrix entries must be in F_3")
        if any(not isinstance(v, int) or not 0 <= v <= 2 for v in self.offset):
            raise ValueError("offset entries must be in F_3")

    def __call__(self, world: World) -> World:
        if world.depth != 3 or world.phi[0] != 0:
            raise ValueError("this operator belongs only to the 3D phi(0)=0 construction family")
        a, b = world.phi[1:]
        (p, q), (r, s) = self.matrix
        c, d = self.offset
        return World(3, (0, (p*a + q*b + c) % 3, (r*a + s*b + d) % 3))


SCALE = Operator("scale", ((2, 0), (0, 2)))
SHEAR = Operator("shear", ((1, 0), (1, 1)))
SWAP = Operator("swap", ((0, 1), (1, 0)))
TRANSLATE = Operator("translate", ((1, 0), (0, 1)), (1, 0))
COLLAPSE = Operator("collapse", ((1, 0), (0, 0)))


@dataclass(frozen=True)
class BrokenAlignment:
    operator: str
    source: tuple[int, int, int]
    target: tuple[int, int, int]
    source_class: int
    target_class: int
    conflicting_words: tuple[str, str] | None


@dataclass(frozen=True)
class QuotientCounterexample:
    operator: str
    equivalent_sources: tuple[tuple[int, int, int], tuple[int, int, int]]
    distinct_target_classes: tuple[int, int]
    target_words: tuple[str, str] | None


@dataclass(frozen=True)
class ConstructionAudit:
    status: str
    states: int
    classes: tuple[tuple[tuple[int, int, int], ...], ...]
    operator_edges: int
    preserving_edges: int
    broken_edges: tuple[BrokenAlignment, ...]
    quotient_breaks: tuple[QuotientCounterexample, ...]
    quotient_edges: tuple[tuple[int, str, int], ...]
    refined_classes: tuple[tuple[tuple[int, int, int], ...], ...]
    refinement_rounds: int
    recurrent_components: tuple[tuple[int, ...], ...]
    failure: str | None = None


def _components(count: int, edges: Iterable[tuple[int, str, int]]) -> tuple[tuple[int, ...], ...]:
    """Closed strongly connected components of a finite total quotient graph."""
    graph = {i: set() for i in range(count)}
    for src, _, dst in edges:
        graph[src].add(dst)

    def reach(start: int) -> set[int]:
        visited = {start}
        queue = [start]
        while queue:
            for next_state in graph[queue.pop(0)]:
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append(next_state)
        return visited

    reachable = {i: reach(i) for i in range(count)}
    remaining = set(graph)
    groups = []
    while remaining:
        root = min(remaining)
        group = {node for node in remaining if node in reachable[root] and root in reachable[node]}
        remaining -= group
        if all(graph[node] <= group for node in group):
            groups.append(tuple(sorted(group)))
    return tuple(groups)


def _refine(
    initial: tuple[tuple[World, ...], ...],
    operators: tuple[Operator, ...],
) -> tuple[tuple[tuple[World, ...], ...], int]:
    """Coarsest stable refinement of A/B equivalence for declared operators."""
    blocks = initial
    rounds = 0
    while True:
        by_world = {world: index for index, block in enumerate(blocks) for world in block}
        changed = False
        updated = []
        for block in blocks:
            buckets: dict[tuple[int, ...], list[World]] = {}
            for world in block:
                signature = tuple(by_world[operator(world)] for operator in operators)
                buckets.setdefault(signature, []).append(world)
            if len(buckets) > 1:
                changed = True
            updated.extend(tuple(group) for group in buckets.values())
        if not changed:
            return blocks, rounds
        blocks = tuple(updated)
        rounds += 1


def audit_constructors(
    operators: tuple[Operator, ...],
    *,
    family: tuple[World, ...] | None = None,
    max_states: int = 10000,
) -> ConstructionAudit:
    """Check constructor closure, exact A/B alignments, and congruence.

    A finite family closed under operators is NOT automatically closed under
    relational equivalence. A quotient is valid only if C(W)~C(W') whenever
    W~W' for EVERY admitted constructor C. A different quotient target for
    aligned sources is an explicit higher-order boundary.
    """
    worlds = family if family is not None else inverse_candidates()
    if not worlds or len(set(worlds)) != len(worlds) or not operators:
        return ConstructionAudit("UNKNOWN", len(worlds), (), 0, 0, (), (), (), (), 0,
                                 "nonempty, distinct family and constructors required")
    if max_states < 1:
        raise ValueError("max_states must be positive")
    allowed = set(worlds)
    for world in worlds:
        for operation in operators:
            try:
                successor = operation(world)
            except ValueError as exc:
                return ConstructionAudit("UNKNOWN", len(worlds), (), 0, 0, (), (), (), (), 0,
                                         f"operator not defined here: {exc}")
            if successor not in allowed:
                return ConstructionAudit("OPEN_FAMILY", len(worlds), (), 0, 0, (), (), (), (), 0,
                                         f"{operation.name} escapes at {world.phi} -> {successor.phi}")
    try:
        groups = equivalent_classes(worlds, max_states=max_states)
    except ValueError as exc:
        return ConstructionAudit("UNKNOWN", len(worlds), (), 0, 0, (), (), (), (), 0, str(exc))
    classes = {world: i for i, block in enumerate(groups) for world in block}
    broken = []
    quotient_breaks = []
    edges = set()
    preserving = 0
    for operation in operators:
        for world in worlds:
            target = operation(world)
            edges.add((classes[world], operation.name, classes[target]))
            witness = discover_alignment(world, target, max_states=max_states)
            if witness.status == "UNKNOWN":
                return ConstructionAudit("UNKNOWN", len(worlds), (), 0, 0, (), (), (), (), 0,
                                         f"exhaustive transition witness unavailable for {world.phi}")
            if witness.aligned:
                preserving += 1
            else:
                broken.append(BrokenAlignment(operation.name, world.phi, target.phi,
                                              classes[world], classes[target], witness.conflicting_words))
        for group in groups:
            for index, world in enumerate(group):
                for other in group[index + 1:]:
                    target_a, target_b = operation(world), operation(other)
                    if classes[target_a] != classes[target_b]:
                        pair = discover_alignment(target_a, target_b, max_states=max_states)
                        if pair.status == "UNKNOWN":
                            return ConstructionAudit("UNKNOWN", len(worlds), (), 0, 0, (), (), (), (), 0,
                                                     "target class correspondence unverified")
                        quotient_breaks.append(QuotientCounterexample(
                            operation.name, (world.phi, other.phi),
                            (classes[target_a], classes[target_b]), pair.conflicting_words,
                        ))
    refined, rounds = _refine(groups, operators)
    valid_quotient = not quotient_breaks
    return ConstructionAudit(
        "CLOSED_ON_AB_QUOTIENT" if valid_quotient else "OPEN_AB_QUOTIENT",
        len(worlds), tuple(tuple(w.phi for w in group) for group in groups),
        len(worlds) * len(operators), preserving, tuple(broken),
        tuple(quotient_breaks), tuple(sorted(edges)),
        tuple(tuple(w.phi for w in group) for group in refined), rounds,
        _components(len(groups), edges) if valid_quotient else (),
    )


def shear_three_turn_witness(start: World = World(3, (0, 1, 0))) -> tuple[World, ...]:
    """A nontrivial exact C^3=identity orbit in *construction* (not game) space."""
    first, second = SHEAR(start), SHEAR(SHEAR(start))
    if SHEAR(second) != start:
        raise AssertionError("finite-field shear relation changed")
    return start, first, second, start
