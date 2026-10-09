"""Coherent gauge + root-transport algebra for eventually periodic A/B processes.

A construction morphism includes its VERIFIED scalar witness and marked
incoming boundary. Shifting that morphism keeps the literal tail of its
witness, rather than selecting another possible alignment. The resulting
interchange square commutes exactly, including both marked endpoints.

Scope: diagonal units of F_3, ultimately periodic rule streams, and
witness-aware simultaneous shifts. Not a shift action on an unmarked,
fixed-root quotient, nor a universal A/B closure certificate.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import lcm

from .root_transport import (
    Process, Witness, verify, MarkedWorld, marked_map,
    verify_marked_pair,
)

Rule = tuple[int, int, int]


def identical_streams(a: Process, b: Process) -> bool:
    """Decidable equality for the two complete eventually periodic streams."""
    start = max(len(a.stem), len(b.stem))
    period = lcm(len(a.period), len(b.period))
    return all(a.rule(i) == b.rule(i) for i in range(start + period))


@dataclass(frozen=True)
class BoundaryGauge:
    """The incoming x1 scale and periodic scales for x2, x3, ... ."""
    incoming: int
    period: tuple[int, ...]

    def __post_init__(self) -> None:
        if (type(self.incoming) is not int or self.incoming not in (1, 2)
                or not self.period or any(type(s) is not int or s not in (1, 2)
                                          for s in self.period)):
            raise ValueError("F_3 gauge requires invertible marked scales")

    def scale(self, i: int) -> int:
        if type(i) is not int or i < 0:
            raise ValueError("invalid coordinate index")
        return self.period[i % len(self.period)]

    def apply(self, p: Process) -> Process:
        """Construct Q_i(t_(i-1)*u)=t_i*P_i(u) at every index."""
        def rule(i: int) -> Rule:
            prev = self.incoming if i == 0 else self.scale(i - 1)
            scale = self.scale(i)
            old = p.rule(i)
            q = [0, 0, 0]
            for u in range(3):
                q[(prev * u) % 3] = (scale * old[u]) % 3
            return tuple(q)  # type: ignore[return-value]

        stem = max(1, len(p.stem))
        period = lcm(len(p.period), len(self.period))
        return Process(tuple(rule(i) for i in range(stem)),
                       tuple(rule(i) for i in range(stem, stem + period)))

    def compose(self, other: BoundaryGauge) -> BoundaryGauge:
        n = lcm(len(self.period), len(other.period))
        return BoundaryGauge(self.incoming * other.incoming % 3,
                             tuple(self.scale(i) * other.scale(i) % 3
                                   for i in range(n)))

    def inverse(self) -> BoundaryGauge:
        # Every nonzero F_3 digit is its own multiplicative inverse.
        return self

    def shifted(self, turns: int) -> BoundaryGauge:
        """Incoming scale is carried from the last removed coordinate."""
        if type(turns) is not int or turns < 0:
            raise ValueError("negative or noninteger shifts are inadmissible")
        return BoundaryGauge(self.incoming if turns == 0 else self.scale(turns - 1),
                             tuple(self.scale(turns + i)
                                   for i in range(len(self.period))))


@dataclass(frozen=True)
class MarkedObject:
    process: Process
    gain: int

    def __post_init__(self) -> None:
        if type(self.gain) is not int or self.gain not in (1, 2):
            raise ValueError("marked world must carry a nonzero root gain")

    def world(self) -> MarkedWorld:
        return MarkedWorld(self.process, self.gain)


@dataclass(frozen=True)
class MarkedArrow:
    source: MarkedObject
    target: MarkedObject
    witness: Witness

    def __post_init__(self) -> None:
        if self.target.gain != (self.source.gain * self.witness.incoming) % 3:
            raise ValueError("witness incoming scale disagrees with marked roots")
        if not verify(self.source.process, self.target.process, self.witness):
            raise ValueError("full coinductive process alignment not certified")


def witness_tail(w: Witness, turns: int) -> Witness:
    """Retain the EXACT known witness, including its choices at zero rules.

    Re-solving after shift could pick another valid scalar sequence, losing
    continuity/provenance of the original alignment. This moves the SAME map.
    """
    if (w.status != "ALIGNED" or not w.period
            or type(turns) is not int or turns < 0):
        raise ValueError("need certified witness and nonnegative shift")
    if turns < len(w.head):
        head = w.head[turns:]
        period = w.period
    else:
        head = ()
        phase = (turns - len(w.head)) % len(w.period)
        period = w.period[phase:] + w.period[:phase]
    incoming = w.incoming if turns == 0 else w.scale(turns - 1)
    return Witness("ALIGNED", incoming, tuple(head), tuple(period))


def shift_arrow(arrow: MarkedArrow, turns: int,
                *, new_source_gain: int = 1) -> MarkedArrow:
    """Witness-aware transport, not an object-only shift functor.

    A source gain is explicit because a relative witness alone determines
    only the ratio of the two new root marks.
    """
    if type(new_source_gain) is not int or new_source_gain not in (1, 2):
        raise ValueError("new source gain must be a unit")
    w = witness_tail(arrow.witness, turns)
    return MarkedArrow(
        MarkedObject(arrow.source.process.shift(turns), new_source_gain),
        MarkedObject(arrow.target.process.shift(turns),
                     (new_source_gain * w.incoming) % 3),
        w,
    )


def transform_arrow(arrow: MarkedArrow,
                    source_gauge: BoundaryGauge,
                    target_gauge: BoundaryGauge) -> MarkedArrow:
    """Independent source/target gauge changes, with exact witness transport.

    New witness scales are v_i*s_i*u_i^-1, including the incoming
    boundary scales. Composition is pointwise, not a rediscovery.
    """
    w = arrow.witness
    head_n = len(w.head)
    period_n = lcm(len(w.period), len(source_gauge.period),
                   len(target_gauge.period))

    def ratio(i: int) -> int:
        return (target_gauge.scale(i) * w.scale(i) * source_gauge.scale(i)) % 3

    changed = Witness(
        "ALIGNED",
        (target_gauge.incoming * w.incoming * source_gauge.incoming) % 3,
        tuple(ratio(i) for i in range(head_n)),
        tuple(ratio(i) for i in range(head_n, head_n + period_n)),
    )
    return MarkedArrow(
        MarkedObject(source_gauge.apply(arrow.source.process),
                     (source_gauge.incoming * arrow.source.gain) % 3),
        MarkedObject(target_gauge.apply(arrow.target.process),
                     (target_gauge.incoming * arrow.target.gain) % 3),
        changed,
    )


def same_arrow(left: MarkedArrow, right: MarkedArrow) -> bool:
    """Compare full process streams, both gains, and EVERY witness scale."""
    if (left.source.gain != right.source.gain
            or left.target.gain != right.target.gain
            or left.witness.incoming != right.witness.incoming
            or not identical_streams(left.source.process, right.source.process)
            or not identical_streams(left.target.process, right.target.process)):
        return False
    h = max(len(left.witness.head), len(right.witness.head))
    n = lcm(len(left.witness.period), len(right.witness.period))
    return all(left.witness.scale(i) == right.witness.scale(i)
               for i in range(h + n))


def interchange(arrow: MarkedArrow, source_gauge: BoundaryGauge,
                target_gauge: BoundaryGauge, turns: int) -> bool:
    """The gauge/shift square commutes when the boundary gains travel.

       shift, then shifted gauges == gauges, then shifted witness.

    The right path uses source gain u_(k-1) rather than erroneously 1.
    """
    shifted = shift_arrow(arrow, turns)
    left = transform_arrow(shifted, source_gauge.shifted(turns),
                           target_gauge.shifted(turns))
    gauged = transform_arrow(arrow, source_gauge, target_gauge)
    right = shift_arrow(
        gauged, turns,
        new_source_gain=source_gauge.shifted(turns).incoming,
    )
    return same_arrow(left, right)


def compose_arrows(first: MarkedArrow, second: MarkedArrow) -> MarkedArrow:
    """Compose verified marked morphisms only across an identical middle object."""
    if (first.target.gain != second.source.gain
            or not identical_streams(first.target.process, second.source.process)):
        raise ValueError("marked middle object does not agree")
    from .root_transport import compose_witness
    witness = compose_witness(
        first.source.process, first.target.process, second.target.process,
        first.witness, second.witness,
    )
    return MarkedArrow(first.source, second.target, witness)


def invert_arrow(arrow: MarkedArrow) -> MarkedArrow:
    """Inverse conjugacy with reciprocal coordinate scalars."""
    from .root_transport import invert_witness
    return MarkedArrow(
        arrow.target, arrow.source,
        invert_witness(arrow.source.process, arrow.target.process, arrow.witness),
    )


@dataclass(frozen=True)
class OperatorCertificate:
    status: str
    gauges: int
    raw_templates: int
    exact_compositions: int
    interchange_squares: int
    boundary_mismatch: bool


def audit_period_two() -> OperatorCertificate:
    """Exhaust gauge composition and a nontrivial witness-aware square.

    Finite audit is for period-two schedules/templates. The algebraic
    coinduction arguments apply to all admitted periodic/stemmed inputs.
    """
    rules = tuple((0, a, b) for a, b in product(range(3), repeat=2))
    processes = tuple(Process.repeat(a, b) for a, b in product(rules, repeat=2))
    gauges = tuple(BoundaryGauge(incoming, (s0, s1))
                   for incoming, s0, s1 in product((1, 2), repeat=3))
    keys = {(g.incoming, g.period) for g in gauges}
    comps = 0
    for g in gauges:
        for h in gauges:
            gh = g.compose(h)
            if (gh.incoming, gh.period) not in keys:
                return OperatorCertificate("OPEN_GROUP", 8, 81, comps, 0, False)
            for p in processes:
                comps += 1
                if not identical_streams(g.apply(h.apply(p)), gh.apply(p)):
                    return OperatorCertificate("OPEN_COMPOSITION", 8, 81, comps, 0, False)
    # An actual nonidentity arrow; other arrows are covered by focused tests.
    from .root_transport import ZERO, find
    p = Process.repeat(ZERO, (0, 0, 1))
    q = Process.repeat(ZERO, (0, 1, 0))
    base = MarkedArrow(MarkedObject(p, 1), MarkedObject(q, 1), find(p, q))
    squares = 0
    for g in gauges:
        for h in gauges:
            for turns in (1, 2, 3, 4):
                squares += 1
                if not interchange(base, g, h, turns):
                    return OperatorCertificate("OPEN_INTERCHANGE", 8, 81, comps,
                                               squares, False)
    # Resetting the incoming boundary after shift would lose valid alignment.
    shifted = shift_arrow(base, 1)
    # An incorrectly reset witness is rejected instead.
    try:
        MarkedArrow(shifted.source, MarkedObject(shifted.target.process, 1),
                    shifted.witness)
    except ValueError:
        reset_is_bad = True
    else:
        reset_is_bad = False
    return OperatorCertificate("CLOSED_MARKED_GAUGE_SHIFT_SYSTEM", 8, 81,
                               comps, squares, reset_is_bad)
