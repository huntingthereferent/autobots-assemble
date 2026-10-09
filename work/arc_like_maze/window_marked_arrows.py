"""Witness-carrying full-state arrows with explicitly retained F3 origin marks.

The previously verified CombinedRelation supplies labeled A/B state conjugacies.
An arrow between two *unpointed* worlds need not preserve their chosen marks.
Mark compatibility is a separate, mechanically checked assertion, NEVER inferred
from full-state conjugacy or the fact that two construction rules commute.

All marked points represented here have a given three-digit prefix and ZERO tail.
This is enough for this declared 48-world construction: its A/B transitions,
H shears and R fiber shifts leave all coordinates i>=3 unchanged. It is not a
representation of arbitrary infinite marks or arbitrary window processes.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .window_combined import CombinedWorld, CombinedRelation, classify_pair, rooted_conflict, family

State = tuple[int, ...]
ORIGIN = (0, 0, 0)


def _mark(mark: State) -> None:
    if (type(mark) is not tuple or len(mark) != 3 or
            any(type(v) is not int or v not in (0, 1, 2) for v in mark)):
        raise ValueError("marks must be explicit three-digit F3 tuples")


@dataclass(frozen=True)
class PointedWorld:
    world: CombinedWorld
    mark: State = ORIGIN

    def __post_init__(self) -> None:
        if not isinstance(self.world, CombinedWorld):
            raise TypeError("expected a constructed CombinedWorld")
        _mark(self.mark)

    def at_depth(self, depth: int) -> State:
        if type(depth) is not int or depth < 3:
            raise ValueError("depth must be >=3")
        return self.mark + (0,) * (depth - 3)

    @property
    def canonical(self) -> bool:
        return self.mark == ORIGIN


@dataclass(frozen=True)
class StateArrow:
    """An exact complete-state arrow, not necessarily a marked arrow.

    The chain of literal mathematical witnesses is preserved even if
    the end-to-end map happens to preserve the chosen marks after a
    pair of origin-moving steps cancel.
    """
    source: PointedWorld
    target: PointedWorld
    factors: tuple[CombinedRelation, ...]

    def __post_init__(self) -> None:
        if not self.factors:
            raise ValueError("every arrow must retain at least one state witness")
        if self.factors[0].source != self.source.world:
            raise ValueError("first relation does not start at source world")
        if self.factors[-1].target != self.target.world:
            raise ValueError("last relation does not terminate at target world")
        for index, relation in enumerate(self.factors):
            if relation.kind not in ("SHEAR", "FIBER_SHIFT"):
                raise ValueError("obstructed pair is not a state arrow")
            if index and self.factors[index - 1].target != relation.source:
                raise ValueError("relation witnesses do not compose")

    def map_state(self, state: State) -> State:
        for relation in self.factors:
            state = relation.map_state(state)
        return state

    @property
    def image_of_mark(self) -> State:
        return self.map_state(self.source.mark)

    @property
    def mark_status(self) -> str:
        return ("MARK_PRESERVED" if self.image_of_mark == self.target.mark
                else "MARK_MISMATCH")

    def require_marked(self) -> "MarkedArrow":
        """Never promote an origin-moving arrow without an exact mark match."""
        if self.mark_status != "MARK_PRESERVED":
            raise ValueError("full-state alignment moves the chosen mark; explicit re-marking required")
        return MarkedArrow(self)

    def inverse(self) -> "StateArrow":
        inverse_factors = tuple(
            classify_pair(relation.target, relation.source)
            for relation in reversed(self.factors)
        )
        # In this declared family the chosen reverse shear/R is the
        # inverse of the original chosen witness; tested on all states.
        return StateArrow(self.target, self.source, inverse_factors)

    def compose(self, after: "StateArrow") -> "StateArrow":
        """Compose source -> middle -> target, requiring the SAME POINTED middle."""
        if self.target != after.source:
            raise ValueError("different middle worlds or marks; composition refused")
        return StateArrow(self.source, after.target, self.factors + after.factors)


@dataclass(frozen=True)
class MarkedArrow:
    """A state arrow proved to transport its *explicit* source mark."""
    state_arrow: StateArrow

    def __post_init__(self) -> None:
        if self.state_arrow.mark_status != "MARK_PRESERVED":
            raise ValueError("cannot use origin-moving state map as a marked arrow")

    @property
    def source(self) -> PointedWorld:
        return self.state_arrow.source

    @property
    def target(self) -> PointedWorld:
        return self.state_arrow.target

    def map_state(self, state: State) -> State:
        return self.state_arrow.map_state(state)

    def inverse(self) -> "MarkedArrow":
        return self.state_arrow.inverse().require_marked()

    def compose(self, after: "MarkedArrow") -> "MarkedArrow":
        return self.state_arrow.compose(after.state_arrow).require_marked()


@dataclass(frozen=True)
class MarkChange:
    """An explicit change of target point, not an equivalence of old points.

    The ORIGINAL target world/mark remains recoverable. For canonical-root
    bridges, witness is two A/B words colliding at the original source
    origin and splitting at the original target origin.
    """
    original: StateArrow
    transported_target: PointedWorld
    resulting_arrow: MarkedArrow
    original_root_conflict: tuple[str, str, State, State, State]

    def __post_init__(self) -> None:
        if self.original.source.mark != ORIGIN or self.original.target.mark != ORIGIN:
            raise ValueError("root-collision evidence requires canonical old marks")
        if self.original.mark_status != "MARK_MISMATCH":
            raise ValueError("no change required: marks already align")
        if self.transported_target.world != self.original.target.world:
            raise ValueError("cannot silently replace target world")
        if self.transported_target.mark != self.original.image_of_mark:
            raise ValueError("mark-change target must be the exact mapped source mark")
        if self.resulting_arrow.source != self.original.source or (
                self.resulting_arrow.target != self.transported_target):
            raise ValueError("mark-change arrow endpoints do not agree")
        one, two, same_source, first_target, second_target = self.original_root_conflict
        a, b = self.original.source.world, self.original.target.world
        if (a.apply(ORIGIN, one) != same_source or
                a.apply(ORIGIN, two) != same_source or
                b.apply(ORIGIN, one) != first_target or
                b.apply(ORIGIN, two) != second_target or
                first_target == second_target):
            raise ValueError("root-collision witness is not valid")


def canonical_arrow(source: CombinedWorld, target: CombinedWorld) -> StateArrow:
    """Return exact full-state witness; throw on genuinely inequivalent worlds."""
    return StateArrow(PointedWorld(source), PointedWorld(target),
                      (classify_pair(source, target),))


def transport_target_mark(arrow: StateArrow) -> MarkChange:
    """Repoint the *target* explicitly while retaining original root conflict.

    This changes the pointed target object, NOT its dynamics. It may be
    used as a marked arrow only relative to the NEW target mark.
    """
    if not arrow.source.canonical or not arrow.target.canonical:
        raise ValueError("only canonical-root differences are handled here")
    if arrow.mark_status == "MARK_PRESERVED":
        raise ValueError("source mark already maps to target mark")
    conflict = rooted_conflict(arrow.source.world, arrow.target.world)
    if conflict is None:
        raise ValueError("no concrete rooted word-collision witness exists")
    repointed = PointedWorld(arrow.target.world, arrow.image_of_mark)
    admitted = StateArrow(arrow.source, repointed, arrow.factors).require_marked()
    return MarkChange(arrow, repointed, admitted, conflict)


@dataclass(frozen=True)
class MarkedCertificate:
    status: str
    total_pairs: int
    obstructed: int
    canonical_marked_arrows: int
    nonrooted_state_arrows: int
    guarded_nonrooted_arrows: int
    explicit_remarkings: int
    marked_inverse_checks: int
    marked_composition_checks: int
    failure: str | None = None


def certify_marked_operator() -> MarkedCertificate:
    """Exhaust all 2,304 world pairs in this deliberately finite universe."""
    tally = dict(obstructed=0, marked=0, nonroot=0,
                 guards=0, repointed=0, inverse=0, composition=0)
    worlds = family()
    for src in worlds:
        for dst in worlds:
            rel = classify_pair(src, dst)
            if rel.kind is None:
                tally["obstructed"] += 1
                try:
                    canonical_arrow(src, dst)
                except ValueError:
                    continue
                return MarkedCertificate("OPEN_OBSTRUCTION",2304,0,0,0,0,0,0,0,
                                         "obstructed pair admitted")
            arrow = canonical_arrow(src, dst)
            for state in product(range(3), repeat=3):
                image = arrow.map_state(state)
                for action in "AB":
                    if arrow.map_state(src.step(state, action)) != dst.step(image, action):
                        return MarkedCertificate("OPEN_CONJUGACY",2304,0,0,0,0,0,0,0,
                                                 "witness did not commute")
            if arrow.mark_status == "MARK_PRESERVED":
                tally["marked"] += 1
                marked = arrow.require_marked()
                reverse = marked.inverse()
                identity = marked.compose(reverse)
                if identity.source != identity.target or identity.map_state(ORIGIN) != ORIGIN:
                    return MarkedCertificate("OPEN_MARKED_INVERSE",2304,0,0,0,0,0,0,0,
                                             "mark identity lost")
                tally["inverse"] += 1
                tally["composition"] += 1
            else:
                tally["nonroot"] += 1
                try:
                    arrow.require_marked()
                except ValueError:
                    tally["guards"] += 1
                else:
                    return MarkedCertificate("OPEN_UNSAFE_PROMOTION",2304,0,0,0,0,0,0,0,
                                             "nonroot arrow promoted")
                witness = transport_target_mark(arrow)
                marked = witness.resulting_arrow
                if marked.map_state(ORIGIN) != witness.transported_target.mark:
                    return MarkedCertificate("OPEN_REMARKING",2304,0,0,0,0,0,0,0,
                                             "explicit transported mark lost")
                inverse = marked.inverse()
                result = marked.compose(inverse)
                if result.source != result.target or result.map_state(ORIGIN) != ORIGIN:
                    return MarkedCertificate("OPEN_REMARKING_INVERSE",2304,0,0,0,0,0,0,0,
                                             "nonroot witness failed after re-mark")
                tally["repointed"] += 1
                tally["inverse"] += 1
                tally["composition"] += 1
    success = (tally["obstructed"], tally["marked"], tally["nonroot"],
               tally["guards"], tally["repointed"], tally["inverse"],
               tally["composition"]) == (2124,144,36,36,36,180,180)
    return MarkedCertificate(
        "CLOSED_POINTED_ARROW_CONTRACT_IN_DECLARED_FAMILY" if success
        else "OPEN_COUNTS", len(worlds)**2,
        tally["obstructed"], tally["marked"], tally["nonroot"],
        tally["guards"], tally["repointed"], tally["inverse"],
        tally["composition"], None if success else str(tally))
