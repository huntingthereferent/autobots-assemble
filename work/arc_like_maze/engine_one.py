"""Engine 1: bounded inverse construction of changing finite-field engines.

This module selects *mathematical laws from witnessed relation requirements*.
It is not A/B's universal definition, an autonomous research agent, ARC
gameplay, a commerce system, or a proof of universal self-modification.

Two distinct construction grammars are deliberately kept separate:
- the 48 two-predecessor windows with *full-state* classifiers;
- triangular coupling towers of 1..4 rules with *root-reachable* classifiers.
A projection, a pointed conjugacy, and an unpointed conjugacy are not aliases.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

from .third_coupling import (
    CouplingTower, construct_family, count_fixed_B_formula,
    projective_scaling, rooted_graph, classify_rooted,
)
from .window_combined import (
    CombinedWorld, classify_pair, family as window_family,
    fixed_word_formula, rooted_conflict,
)
from .window_two import WindowProcess

Family = Literal["window48", "coupling_tower"]
Relation = Literal[
    "ANY", "ROOTED_FULL", "FULL_UNROOTED", "FULL_OBSTRUCTED",
    "ROOTED_REACHABLE", "ROOTED_OBSTRUCTED", "PROJECTION",
]
WORDS = ("B", "BBB", "AABAB", "ABABAB")
RELATIONS = (
    "ANY", "ROOTED_FULL", "FULL_UNROOTED", "FULL_OBSTRUCTED",
    "ROOTED_REACHABLE", "ROOTED_OBSTRUCTED", "PROJECTION",
)


@dataclass(frozen=True)
class Requirements:
    """Inverse-construction constraints, not a target parameter description.

    Fixed-word counts in window48 are complete-state counts at depth three.
    Fixed-B counts in coupling_tower are complete-state counts at minimal depth.
    For a follow-on construction, the relation is compared to the actual
    previous law. ANY permits only *witnessed* changes, not silent guesses.
    """
    family: Family
    couplings: int = 1
    fixed_words: tuple[tuple[str, int], ...] = ()
    fixed_B: int | None = None
    relation: Relation = "ANY"

    def __post_init__(self) -> None:
        if self.family not in ("window48", "coupling_tower"):
            raise ValueError("unknown declared mathematical construction family")
        if type(self.couplings) is not int or not 1 <= self.couplings <= 4:
            raise ValueError("admitted coupling counts are 1..4")
        if self.relation not in RELATIONS:
            raise ValueError("unknown relation requirement")
        if len({w for w, _ in self.fixed_words}) != len(self.fixed_words):
            raise ValueError("duplicate fixed-word constraint")
        for word, value in self.fixed_words:
            if word not in WORDS or type(value) is not int or value < 0:
                raise ValueError("unsupported fixed-word equation")
        if self.fixed_B is not None and (type(self.fixed_B) is not int or self.fixed_B < 0):
            raise ValueError("fixed-B count must be a nonnegative integer")
        if self.family == "window48" and self.fixed_B is not None:
            raise ValueError("use fixed_words=(('B', count),) for window48")
        if self.family == "coupling_tower" and self.fixed_words:
            raise ValueError("coupling_tower exposes a proved fixed-B formula only")


@dataclass(frozen=True)
class RelationWitness:
    kind: str
    source: str
    target: str
    evidence: tuple[str, ...]
    source_mark: tuple[int, ...] | None = None
    target_mark: tuple[int, ...] | None = None

    @property
    def is_alignment(self) -> bool:
        return self.kind in ("ROOTED_FULL", "FULL_UNROOTED", "ROOTED_REACHABLE")


Law = CombinedWorld | CouplingTower | WindowProcess


@dataclass(frozen=True)
class ConstructionCycle:
    """Independently executable, witnessed mathematical recurrence."""
    laws: tuple[Law, ...]
    arrows: tuple[RelationWitness, ...]
    scope: str

    def __post_init__(self) -> None:
        if len(self.laws) < 2 or len(self.laws) != len(self.arrows):
            raise ValueError("a witnessed cycle needs two or more laws and one arrow per turn")
        if len(set(self.laws)) != len(self.laws):
            raise ValueError("cycle laws must differ until the witnessed return")
        for i, arrow in enumerate(self.arrows):
            if arrow.source != repr(self.laws[i]):
                raise ValueError("cycle witness source is not the selected law")
            if arrow.target != repr(self.laws[(i + 1) % len(self.laws)]):
                raise ValueError("cycle witness target is not the next law")


@dataclass(frozen=True)
class ConstructedEngine:
    """A constructed changing-law object. Law changes require certified turns."""
    law: Law
    version: int
    history: tuple[RelationWitness, ...] = ()
    cycle: ConstructionCycle | None = None
    phase: int = 0

    def tick(self) -> "ConstructedEngine":
        """Run the admitted update without consulting the inverse constructor again."""
        if self.cycle is None:
            raise ValueError("no constructed recurrence; Engine 1 must witness one")
        if self.phase not in range(len(self.cycle.laws)) or self.cycle.laws[self.phase] != self.law:
            raise ValueError("engine version does not match its witnessed recurrence phase")
        next_phase = (self.phase + 1) % len(self.cycle.laws)
        return ConstructedEngine(
            self.cycle.laws[next_phase], self.version + 1,
            self.history + (self.cycle.arrows[self.phase],),
            self.cycle, next_phase,
        )

    def step(self, state: tuple[int, ...], generator: str) -> tuple[int, ...]:
        return self.law.step(state, generator)

    def inverse(self, state: tuple[int, ...], generator: str) -> tuple[int, ...]:
        return self.law.inverse(state, generator)

    def evolve(self, engine_one: "InverseConstructionEngine", requirement: Requirements) -> "ConstructionResult":
        return engine_one.construct(requirement, previous=self)

    def watch_B_against(self, other: "ConstructedEngine"):
        """Enter the Cyclic Action Engine's B-only continuation on two explicit window laws.

        The inverse-construction grammar is unchanged. This cannot claim
        A/B conjugacy or promote a five-coordinate window into Engine 1's
        previously declared 48-law or coupling-tower search.
        """
        from .cyclic_action_continuation import CyclicActionContinuation
        return CyclicActionContinuation.enter(self, other)


@dataclass(frozen=True)
class ConstructionResult:
    status: str   # CONSTRUCTED / WALL
    engine: ConstructedEngine | None
    candidates_examined: int
    admissible_candidates: int
    selection_rule: str
    wall: str | None = None


def _window_neighbors(world: CombinedWorld) -> tuple[tuple[str, CombinedWorld], ...]:
    moves = (
        ("shear", world.shear_next()),
        ("support", world.support_next()),
        ("pulse", world.pulse_next()),
        ("balanced", world.balanced_next()),
    )
    return tuple((name, target) for name, target in moves if target is not None)


def _window_paths(start: CombinedWorld) -> dict[CombinedWorld, tuple[str, ...]]:
    """Breadth-first shortest paths through the actual admitted constructors.

    No inverse pulse/support/balanced operation is invented. Shear is cyclic.
    """
    paths = {start: ()}
    queue = [start]
    for law in queue:
        for operation, target in _window_neighbors(law):
            if target not in paths:
                paths[target] = paths[law] + (operation,)
                queue.append(target)
    return paths


def _window_witness(source: CombinedWorld, target: CombinedWorld) -> RelationWitness:
    rel = classify_pair(source, target)
    before, after = repr(source), repr(target)
    if rel.kind is not None:
        image = rel.map_state((0, 0, 0))
        # Finite independent check of the declared all-depth formula.
        for state in product(range(3), repeat=3):
            mapped = rel.map_state(state)
            for action in "AB":
                if rel.map_state(source.step(state, action)) != target.step(mapped, action):
                    raise AssertionError("declared conjugacy fails a generator square")
        if rel.root_preserving:
            if image != (0, 0, 0):
                raise AssertionError("rooted witness moved the canonical origin")
            return RelationWitness(
                "ROOTED_FULL", before, after,
                ("exact labeled generator squares", "origin mapped to origin"),
                (0, 0, 0), image,
            )
        collision = rooted_conflict(source, target)
        if collision is None:
            raise AssertionError("unrooted conjugacy lacks the rooted collision")
        first, second, same, first_dst, second_dst = collision
        if first_dst == second_dst or source.apply((0, 0, 0), first) != same:
            raise AssertionError("invalid root collision witness")
        return RelationWitness(
            "FULL_UNROOTED", before, after,
            ("exact labeled generator squares",
             "canonical origins are NOT conjugate",
             "word collision: " + repr((first, second, same, first_dst, second_dst))),
            (0, 0, 0), image,
        )
    if not rel.obstruction_word or rel.source_count == rel.target_count:
        raise AssertionError("claimed full-state obstruction has no separating invariant")
    return RelationWitness(
        "FULL_OBSTRUCTED", before, after,
        ("fixed word " + rel.obstruction_word,
         "source=" + str(rel.source_count),
         "target=" + str(rel.target_count)),
    )


def _tower_witness(source: CouplingTower, target: CouplingTower) -> RelationWitness | None:
    before, after = repr(source), repr(target)
    n, m = len(source.rules), len(target.rules)
    if m == n + 1 and target.rules[:n] == source.rules and target.depth == source.depth + 1:
        # Complete finite-state projection check, *not* a bijective conjugacy.
        for state in product(range(3), repeat=target.depth):
            for action in "AB":
                if (target.step(state, action)[:-1]
                        != source.step(state[:-1], action)):
                    raise AssertionError("triangular extension broke projection")
        return RelationWitness("PROJECTION", before, after, (
            "new rule appended without changing the old rule prefix",
            "all complete-state A/B projection squares checked",
            "not a full-state conjugacy",
        ))
    if n != m or source.depth != target.depth:
        return None
    if sum(a != b for a, b in zip(source.rules, target.rules)) != 1:
        return None  # Only one-table edits are admitted per turn.
    same_root = rooted_graph(source) == rooted_graph(target)
    if same_root:
        scale = projective_scaling(source, target)
        if scale is not None:
            return RelationWitness(
                "ROOTED_FULL", before, after,
                ("explicit all-depth projective diagonal scaling " + repr(scale),
                 "exact origin-reachable graph agreement"),
                source.origin, target.origin,
            )
        return RelationWitness(
            "ROOTED_REACHABLE", before, after,
            ("identical complete origin-reachable transition graph",
             "full-state alignment remains UNKNOWN"),
            source.origin, target.origin,
        )
    source_fixed = count_fixed_B_formula(source)
    target_fixed = count_fixed_B_formula(target)
    if source_fixed != target_fixed:
        return RelationWitness(
            "FULL_OBSTRUCTED", before, after,
            ("fixed B on complete state space",
             "source=" + str(source_fixed), "target=" + str(target_fixed),
             "origin-rooted graphs also differ"),
        )
    return RelationWitness(
        "ROOTED_OBSTRUCTED", before, after,
        ("distinct complete rooted transition graphs",
         "full-state conjugacy UNKNOWN; fixed-B counts coincide"),
    )


class InverseConstructionEngine:
    """Inverse search followed by witnessed changing-law construction.

    Search is exhaustive in the *declared finite family*, not across all A/B.
    Default selection: fewest admitted construction operations, then stable
    family enumeration. This is a documented deterministic choice, not a
    unique solution implied by mathematics.
    """

    def construct(self, required: Requirements, *,
                  previous: ConstructedEngine | None = None) -> ConstructionResult:
        if not isinstance(required, Requirements):
            raise TypeError("construct expects mathematical Requirements")
        if previous is not None and not isinstance(previous, ConstructedEngine):
            raise TypeError("previous must be a ConstructedEngine")
        if previous is not None and isinstance(previous.law, WindowProcess):
            return ConstructionResult(
                "WALL", None, 0, 0, "unchanged inverse-construction grammar",
                "the two-input WindowProcess is admitted for B-only research, "
                "not for Engine 1 inverse construction without a new witnessed grammar",
            )

        laws: tuple[Law, ...]
        if required.family == "window48":
            laws = window_family()
            laws = tuple(w for w in laws if all(
                fixed_word_formula(word, 3, w.support, w.pulse, w.balanced) == count
                for word, count in required.fixed_words
            ))
        else:
            laws = construct_family(required.couplings)
            if required.fixed_B is not None:
                laws = tuple(w for w in laws
                             if count_fixed_B_formula(w) == required.fixed_B)

        considered = len(laws)
        if previous is None:
            if required.relation != "ANY":
                return ConstructionResult("WALL", None, considered, 0,
                                          "declared-family enumeration",
                                          "a relational comparison needs an existing engine")
            if not laws:
                return ConstructionResult("WALL", None, 0, 0,
                                          "declared-family enumeration",
                                          "no system satisfies all required equations")
            return ConstructionResult(
                "CONSTRUCTED", ConstructedEngine(laws[0], 0), considered, len(laws),
                "first matching law in declared family order; not a unique inverse",
            )

        old = previous.law
        if isinstance(old, CombinedWorld) and required.family != "window48":
            return ConstructionResult("WALL", None, considered, 0, "no cross-grammar adapter",
                                      "no admitted construction connecting these grammars")
        if isinstance(old, CouplingTower) and required.family != "coupling_tower":
            return ConstructionResult("WALL", None, considered, 0, "no cross-grammar adapter",
                                      "no admitted construction connecting these grammars")

        paths = _window_paths(old) if isinstance(old, CombinedWorld) else {}
        options: list[tuple[int, int, Law, RelationWitness]] = []
        for i, target in enumerate(laws):
            if old == target:
                continue  # A new engine version must change its concrete law.
            if isinstance(old, CombinedWorld):
                if target not in paths:
                    continue
                witness = _window_witness(old, target)
                distance = len(paths[target])
            else:
                witness = _tower_witness(old, target)
                if witness is None:
                    continue
                distance = 1
            if required.relation != "ANY" and required.relation != witness.kind:
                continue
            options.append((distance, i, target, witness))

        if not options:
            return ConstructionResult(
                "WALL", None, considered, 0, "shortest witnessed constructor path",
                "no permitted change satisfies the requested witnessed relation",
            )
        distance, _, target, witness = min(options, key=lambda item: (item[0], item[1]))
        if isinstance(old, CombinedWorld):
            path = paths[target]
            # Preserve every intermediate relation: a composite route is not
            # silently upgraded to an equivalence of its endpoints.
            trail = []
            current = old
            for operation in path:
                neighbors = dict(_window_neighbors(current))
                next_law = neighbors[operation]
                edge = _window_witness(current, next_law)
                trail.append(RelationWitness(
                    edge.kind, edge.source, edge.target,
                    ("constructor=" + operation,) + edge.evidence,
                    edge.source_mark, edge.target_mark,
                ))
                current = next_law
            if current != target:
                raise AssertionError("construction route does not reach its target")
            # Endpoints are compared independently of the intermediate arrows.
            route = tuple(trail) + (witness,)
        else:
            route = (witness,)
        return ConstructionResult(
            "CONSTRUCTED",
            ConstructedEngine(target, previous.version + 1,
                              previous.history + route),
            considered, len(options),
            "fewest admitted operations (" + str(distance) +
            "); stable family order; all intermediate witnesses retained",
        )


    def construct_cycle(self, seed: ConstructedEngine) -> ConstructionResult:
        """Construct an executable changing-law recurrence with its witnesses.

        Window family: exact three-turn shear (full-state pointed conjugacy).
        Coupling towers: the existing rooted-class permutation; it can have
        dormant, origin-reachable-only alignments. Neither is universal closure.
        """
        if not isinstance(seed, ConstructedEngine):
            raise TypeError("construct_cycle needs a constructed mathematical engine")
        law = seed.law
        if isinstance(law, CombinedWorld):
            members = (law, law.shear_next(), law.shear_next().shear_next())
            if members[2].shear_next() != law:
                raise AssertionError("shear cycle failed its closure identity")
            arrows = tuple(_window_witness(a, b) for a, b in zip(
                members, members[1:] + members[:1]
            ))
            if any(w.kind != "ROOTED_FULL" for w in arrows):
                raise AssertionError("proposed shear recurrence lacks pointed conjugacy")
            scope = "48-law window: exact three-turn origin-preserving shear cycle"
            examined = 48
        else:
            # Existing classification supplies a CHOSEN class-rotation
            # constructor. It may not be full-state conjugacy when an
            # origin-dormant coupling masks higher state behavior.
            groups = classify_rooted(construct_family(len(law.rules), depth=law.depth))
            group = next((g for g in groups if law in g), None)
            if group is None:
                raise AssertionError("source tower missing from native classification")
            if len(group) == 1:
                return ConstructionResult(
                    "WALL", None, len(groups), 0, "witnessed rooted-class rotation",
                    "this constructed law is a singleton rooted class; no changing cycle",
                )
            start = group.index(law)
            members = group[start:] + group[:start]
            arrows_list = []
            for a, b in zip(members, members[1:] + members[:1]):
                if rooted_graph(a) != rooted_graph(b):
                    raise AssertionError("class rotation crossed a rooted-graph boundary")
                scaling = projective_scaling(a, b)
                kind = "ROOTED_FULL" if scaling is not None else "ROOTED_REACHABLE"
                evidence = (
                    ("projectively coherent full-state diagonal scaling " + repr(scaling))
                    if scaling is not None else
                    "same complete rooted orbit; full-space conjugacy UNKNOWN"
                )
                arrows_list.append(RelationWitness(
                    kind, repr(a), repr(b), (evidence, "declared rooted-class rotation"),
                    a.origin, b.origin,
                ))
            arrows = tuple(arrows_list)
            scope = "coupling-tower: chosen finite rooted-class rotation"
            examined = len(groups)
        cycle = ConstructionCycle(tuple(members), arrows, scope)
        return ConstructionResult(
            "CONSTRUCTED",
            ConstructedEngine(law, seed.version, seed.history, cycle, 0),
            examined, len(members),
            "witnessed finite construction cycle; no universal stopping claim",
        )
