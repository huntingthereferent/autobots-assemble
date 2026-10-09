"""A new origin-moving CENTRAL symmetry over the declared 48 A/B worlds.

T_r(x)_2=x_2+r, with every other coordinate unchanged. This genuinely
changes the pointed object, though it commutes with the A/B dynamics.
It is NOT a new inequivalent world. It is independent of the previously
admitted H (shear) and R (fiber-shift) state-map witnesses.

This module extends the *witness language*, not the 48-world family:
old CombinedRelation factors and new TranslationFactor factors compose
without discarding intermediate pointed endpoints or former root conflicts.
Coordinates >=3 are preserved, and explicit marks have zero tails.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .window_combined import CombinedRelation, CombinedWorld, classify_pair, family
from .window_marked_arrows import (
    PointedWorld, StateArrow, MarkedArrow, MarkChange, ORIGIN,
    canonical_arrow, transport_target_mark,
)

State = tuple[int, ...]


def translate(state: State, amount: int) -> State:
    """Exact, coherent inverse-limit automorphism C_r of the third digit."""
    if (type(state) is not tuple or len(state) < 3 or
            any(type(d) is not int or d not in (0, 1, 2) for d in state)):
        raise ValueError("requires an F3 state of depth >=3")
    if type(amount) is not int or amount not in (0, 1, 2):
        raise ValueError("translation amount must be in F3")
    return state[:2] + ((state[2] + amount) % 3,) + state[3:]


@dataclass(frozen=True)
class TranslationFactor:
    """A nonzero or identity central shift; retains the world and amount."""
    world: CombinedWorld
    amount: int

    def __post_init__(self) -> None:
        if not isinstance(self.world, CombinedWorld):
            raise TypeError("expected constructed CombinedWorld")
        if type(self.amount) is not int or self.amount not in (0, 1, 2):
            raise ValueError("translation amount must be in F3")

    @property
    def source_world(self) -> CombinedWorld:
        return self.world

    @property
    def target_world(self) -> CombinedWorld:
        return self.world

    def map_state(self, state: State) -> State:
        return translate(state, self.amount)

    def inverse(self) -> "TranslationFactor":
        return TranslationFactor(self.world, (-self.amount) % 3)


@dataclass(frozen=True)
class ConjugacyFactor:
    """Retain BOTH directional A/B witness descriptions at admission time.

    Inversion swaps stored witnesses; it does not reclassify on every inverse.
    """
    forward: CombinedRelation
    backward: CombinedRelation

    def __post_init__(self) -> None:
        if (self.forward.kind not in ("SHEAR", "FIBER_SHIFT") or
                self.backward.kind not in ("SHEAR", "FIBER_SHIFT") or
                self.forward.source != self.backward.target or
                self.forward.target != self.backward.source):
            raise ValueError("conjugacy factors require compatible exact inverse arrows")

    @property
    def source_world(self) -> CombinedWorld:
        return self.forward.source

    @property
    def target_world(self) -> CombinedWorld:
        return self.forward.target

    def map_state(self, state: State) -> State:
        return self.forward.map_state(state)

    def inverse(self) -> "ConjugacyFactor":
        return ConjugacyFactor(self.backward, self.forward)


def from_relation(relation: CombinedRelation) -> ConjugacyFactor:
    if relation.kind not in ("SHEAR", "FIBER_SHIFT"):
        raise ValueError("cannot turn an invariant obstruction into an operator")
    return ConjugacyFactor(relation, classify_pair(relation.target, relation.source))


Factor = TranslationFactor | ConjugacyFactor


@dataclass(frozen=True)
class OperatorPath:
    """Composable exact state maps with full ordered factor provenance.

    The original pointed endpoints are retained. A path is marked iff it
    actually maps its source point onto the chosen target point.
    """
    source: PointedWorld
    target: PointedWorld
    factors: tuple[Factor, ...]

    def __post_init__(self) -> None:
        if not self.factors:
            raise ValueError("operator path must carry a literal witness")
        if self.factors[0].source_world != self.source.world:
            raise ValueError("first factor starts in another world")
        if self.factors[-1].target_world != self.target.world:
            raise ValueError("final factor ends in another world")
        for earlier, later in zip(self.factors, self.factors[1:]):
            if earlier.target_world != later.source_world:
                raise ValueError("operator witness worlds do not compose")

    def map_state(self, state: State) -> State:
        for factor in self.factors:
            state = factor.map_state(state)
        return state

    @property
    def image_of_mark(self) -> State:
        return self.map_state(self.source.mark)

    @property
    def mark_status(self) -> str:
        return ("MARK_PRESERVED" if self.image_of_mark == self.target.mark
                else "MARK_MISMATCH")

    def require_marked(self) -> "PointedOperator":
        if self.mark_status != "MARK_PRESERVED":
            raise ValueError("path moves chosen mark: change pointed object explicitly")
        return PointedOperator(self)

    def compose(self, after: "OperatorPath") -> "OperatorPath":
        if self.target != after.source:
            raise ValueError("middle pointed object differs; composition refused")
        return OperatorPath(self.source, after.target, self.factors + after.factors)

    def inverse(self) -> "OperatorPath":
        return OperatorPath(self.target, self.source,
                            tuple(f.inverse() for f in reversed(self.factors)))


@dataclass(frozen=True)
class PointedOperator:
    """An OperatorPath whose COMPLETE map preserves its endpoint marks."""
    path: OperatorPath

    def __post_init__(self) -> None:
        if self.path.mark_status != "MARK_PRESERVED":
            raise ValueError("pointed-arrow mark mismatch")

    @property
    def source(self) -> PointedWorld:
        return self.path.source

    @property
    def target(self) -> PointedWorld:
        return self.path.target

    def map_state(self, state: State) -> State:
        return self.path.map_state(state)

    def then(self, after: "PointedOperator") -> "PointedOperator":
        return self.path.compose(after.path).require_marked()

    def inverse(self) -> "PointedOperator":
        return self.path.inverse().require_marked()


def include_existing(arrow: StateArrow | MarkedArrow) -> OperatorPath:
    """Keep literal H/R factors and both pointed endpoints from prior layer."""
    if isinstance(arrow, MarkedArrow):
        arrow = arrow.state_arrow
    if not isinstance(arrow, StateArrow):
        raise TypeError("expected witnessed state/marked arrow")
    return OperatorPath(arrow.source, arrow.target,
                        tuple(from_relation(rel) for rel in arrow.factors))


def shift_point(pointed: PointedWorld, amount: int) -> PointedOperator:
    """A new pointed target, connected by an exact commuting A/B symmetry."""
    new_mark = translate(pointed.mark, amount)
    target = PointedWorld(pointed.world, new_mark)
    return OperatorPath(pointed, target,
                        (TranslationFactor(pointed.world, amount),)).require_marked()


@dataclass(frozen=True)
class ShiftedRootBridge:
    """Keep original canonical-root failure, plus the two new witness kinds."""
    old_change: MarkChange
    shift: PointedOperator
    route: PointedOperator

    def __post_init__(self) -> None:
        if self.shift.source != self.old_change.resulting_arrow.target:
            raise ValueError("shift does not start at the actual transported mark")
        if self.route.source != self.old_change.original.source:
            raise ValueError("original canonical source lost")
        if self.route.target != self.shift.target:
            raise ValueError("shifted target mark lost")
        if not isinstance(self.route.path.factors[-1], TranslationFactor):
            raise ValueError("shift witness must remain the final factor")
        if len(self.route.path.factors) != len(self.old_change.original.factors) + 1:
            raise ValueError("original full-state witness factors lost")
        if self.route.map_state(self.route.source.mark) != self.route.target.mark:
            raise ValueError("transported mark fails the operator composition")


def shift_nonroot_bridge(source: CombinedWorld, target: CombinedWorld,
                         amount: int) -> ShiftedRootBridge:
    """An actual R bridge followed by an INDEPENDENT central translation."""
    original = canonical_arrow(source, target)
    change = transport_target_mark(original)  # enforces original root collision
    initial = include_existing(change.resulting_arrow).require_marked()
    move = shift_point(initial.target, amount)
    return ShiftedRootBridge(change, move, initial.then(move))


@dataclass(frozen=True)
class TranslationCertificate:
    status: str
    worlds: int
    distinct_translated_marks: int
    canonical_rooted_relations: int
    nonrooted_relations: int
    translated_rooted_routes: int
    translated_nonroot_routes: int
    blocked_nonroot_promotions: int
    fixed_root_conflicts_retained: int
    failures: str | None = None


def certify_translation() -> TranslationCertificate:
    """All pairs, three literal shift witnesses per existing proved relation."""
    members = family()
    mark_count = rooted = nonroot = rooted_routes = nonroot_routes = guards = conflicts = 0
    for world in members:
        marks = {shift_point(PointedWorld(world), r).target.mark for r in range(3)}
        if len(marks) != 3:
            return TranslationCertificate("OPEN_MARK_COLLISION",48,0,0,0,0,0,0,0)
        mark_count += len(marks)
    for source in members:
        for target in members:
            relation = classify_pair(source, target)
            if relation.kind is None:
                continue
            base = canonical_arrow(source, target)
            if base.mark_status == "MARK_PRESERVED":
                rooted += 1
                initial = include_existing(base).require_marked()
                for r in range(3):
                    follow = shift_point(initial.target, r)
                    route = initial.then(follow)
                    if route.map_state(ORIGIN) != follow.target.mark:
                        return TranslationCertificate("OPEN_ROOT_TRANSLATION",48,mark_count,
                                                      rooted,nonroot,rooted_routes,nonroot_routes,guards,conflicts)
                    rooted_routes += 1
            else:
                nonroot += 1
                try:
                    include_existing(base).require_marked()
                except ValueError:
                    guards += 1
                else:
                    return TranslationCertificate("OPEN_UNSAFE_PROMOTION",48,mark_count,
                                                  rooted,nonroot,rooted_routes,nonroot_routes,guards,conflicts)
                for r in range(3):
                    route = shift_nonroot_bridge(source, target, r)
                    if route.old_change.original_root_conflict is None:
                        return TranslationCertificate("OPEN_LOST_ROOT_WITNESS",48,mark_count,
                                                      rooted,nonroot,rooted_routes,nonroot_routes,guards,conflicts)
                    if route.route.target.mark == ORIGIN:
                        return TranslationCertificate("OPEN_FALSE_CANONICAL_ROOT",48,mark_count,
                                                      rooted,nonroot,rooted_routes,nonroot_routes,guards,conflicts)
                    nonroot_routes += 1
                    conflicts += 1
    status = ("CLOSED_TRANSLATION_AND_EXPLICIT_MARK_TRANSPORT"
              if (mark_count, rooted, nonroot, rooted_routes, nonroot_routes,guards,conflicts)
              == (144,144,36,432,108,36,108) else "OPEN_COUNTS")
    return TranslationCertificate(status,48,mark_count,rooted,nonroot,
                                  rooted_routes,nonroot_routes,guards,conflicts)
