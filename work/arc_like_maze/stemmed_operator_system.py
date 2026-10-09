"""Eventually-periodic, boundary-marked coordinate gauges and shift composition.

An operation on a *verified marked arrow* carries its original lasso witness.
The admitted gauge has finitely many initial unit scales and a periodic tail.
This module extends periodic gauges without altering the established solver.
All conclusions concern diagonal F_3 A/B conjugacies, not native ARC.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import lcm

from .marked_operator_system import (
    MarkedArrow, MarkedObject, identical_streams, same_arrow, shift_arrow,
    compose_arrows, transform_arrow, BoundaryGauge,
)
from .root_transport import Process, Witness, verify, verify_marked_pair


@dataclass(frozen=True)
class StemGauge:
    """Incoming unit, finite unit-scale stem, nonempty periodically repeated tail."""
    incoming: int
    stem: tuple[int, ...]
    period: tuple[int, ...]

    def __post_init__(self) -> None:
        if (type(self.incoming) is not int or self.incoming not in (1, 2)
            or not self.period or any(type(s) is not int or s not in (1, 2)
                                      for s in self.stem + self.period)):
            raise ValueError('incoming and all scale values must be F3 units')

    @classmethod
    def periodic(cls, incoming: int, *scales: int) -> 'StemGauge':
        return cls(incoming, (), tuple(scales))

    def scale(self, i: int) -> int:
        if type(i) is not int or i < 0:
            raise ValueError('nonnegative coordinate index required')
        if i < len(self.stem):
            return self.stem[i]
        return self.period[(i - len(self.stem)) % len(self.period)]

    def apply(self, p: Process) -> Process:
        """Change rules via q_i(t_(i-1)u)=t_i p_i(u), with t_-1=incoming.

        The first transformed rule must be stored as a stem because its
        incoming unit may differ from the periodic predecessor scale.
        For all i >= max(1, |p.stem|, |g.stem|+1) both the original
        table phase and the predecessor scale are periodic.
        """
        def rule(i: int):
            prev = self.incoming if i == 0 else self.scale(i - 1)
            new = self.scale(i)
            old = p.rule(i)
            out = [0, 0, 0]
            for u in range(3):
                out[prev*u % 3] = new*old[u] % 3
            return tuple(out)

        transient = max(1, len(p.stem), len(self.stem) + 1)
        period = lcm(len(p.period), len(self.period))
        return Process(tuple(rule(i) for i in range(transient)),
                       tuple(rule(i) for i in range(transient, transient+period)))

    def compose(self, other: 'StemGauge') -> 'StemGauge':
        """Self after other; all scales are pointwise products."""
        h = max(len(self.stem), len(other.stem))
        p = lcm(len(self.period), len(other.period))
        return StemGauge(self.incoming*other.incoming % 3,
                         tuple(self.scale(i)*other.scale(i)%3 for i in range(h)),
                         tuple(self.scale(i)*other.scale(i)%3 for i in range(h,h+p)))

    def inverse(self) -> 'StemGauge':
        """Every nonzero unit of F3 is its own multiplicative inverse."""
        return self

    def shifted(self, turns: int) -> 'StemGauge':
        if type(turns) is not int or turns < 0:
            raise ValueError('shift must be nonnegative')
        incoming = self.incoming if turns == 0 else self.scale(turns-1)
        if turns < len(self.stem):
            return StemGauge(incoming, self.stem[turns:], self.period)
        phase = (turns-len(self.stem)) % len(self.period)
        return StemGauge(incoming, (), self.period[phase:] + self.period[:phase])


def same_gauge(a: StemGauge, b: StemGauge) -> bool:
    """Complete gauge-stream equality, not syntactic tuple equality."""
    if a.incoming != b.incoming:
        return False
    h = max(len(a.stem), len(b.stem))
    p = lcm(len(a.period), len(b.period))
    return all(a.scale(i) == b.scale(i) for i in range(h+p))


def gauge_arrow(arrow: MarkedArrow, source: StemGauge,
                target: StemGauge) -> MarkedArrow:
    """Transport BOTH endpoint gains and the exact full lasso witness."""
    w = arrow.witness
    h = max(len(w.head), len(source.stem), len(target.stem))
    p = lcm(len(w.period), len(source.period), len(target.period))

    def s(i: int) -> int:
        # A/B conjugacy: v_i*s_i/u_i, inverse==itself in F3.
        return target.scale(i)*w.scale(i)*source.scale(i) % 3

    new = Witness('ALIGNED', target.incoming*w.incoming*source.incoming % 3,
                  tuple(s(i) for i in range(h)),
                  tuple(s(i) for i in range(h,h+p)))
    return MarkedArrow(
        MarkedObject(source.apply(arrow.source.process),
                     arrow.source.gain*source.incoming % 3),
        MarkedObject(target.apply(arrow.target.process),
                     arrow.target.gain*target.incoming % 3),
        new)


def interchange_stem(arrow: MarkedArrow, source: StemGauge,
                      target: StemGauge, turns: int) -> bool:
    """All-depth square: shift then shifted gauge = gauge then shift.

    For both paths the source gain after the shift must be u_(k-1).
    The original witness is transported without re-solving its zero rules.
    """
    u = source.shifted(turns)
    v = target.shifted(turns)
    left = gauge_arrow(shift_arrow(arrow, turns), u, v)
    right = shift_arrow(gauge_arrow(arrow, source, target), turns,
                        new_source_gain=u.incoming)
    return same_arrow(left, right)


@dataclass(frozen=True)
class StemOperatorAudit:
    status: str
    gauges: int
    process_templates: int
    compositions_checked: int
    gauge_shift_squares: int
    counterexamples: int


def audit_stemmed() -> StemOperatorAudit:
    """Finite stress audit; the coordinate identities establish all-depth laws."""
    gauges = tuple(StemGauge(b, stem, period)
                   for b in (1, 2)
                   for stem in ((1,), (2, 1))
                   for period in ((1,), (1, 2), (2, 1)))
    templates = tuple(Process.repeat((0,a,b),(0,c,d))
                      for a,b,c,d in product(range(3), repeat=4))
    checks = 0
    for u in gauges:
        for v in gauges:
            uv = u.compose(v)
            for p in templates:
                checks += 1
                if not identical_streams(u.apply(v.apply(p)), uv.apply(p)):
                    return StemOperatorAudit('OPEN_COMPOSITION',len(gauges),len(templates),checks,0,0)
    from .root_transport import ZERO, find
    p = Process((ZERO, (0,0,1)), ((0,0,1), ZERO))
    q = StemGauge(2,(2,),(1,2)).apply(p)
    # Incoming root marks must match the coordinate map.
    arrow = MarkedArrow(MarkedObject(p,1),MarkedObject(q,2),
                        Witness('ALIGNED',2,(2,),(1,2)))
    squares = 0
    for u in gauges:
        for v in gauges:
            for shift in (0, 1, 2, 3, 5, 8):
                squares += 1
                if not interchange_stem(arrow,u,v,shift):
                    return StemOperatorAudit('OPEN_INTERCHANGE',len(gauges),len(templates),checks,squares,0)
    # A deliberately incorrect root reset must be detected.
    k = 1
    shifted = shift_arrow(arrow,k)
    failure = 0
    try:
        MarkedArrow(shifted.source,
                    MarkedObject(shifted.target.process,1),shifted.witness)
    except ValueError:
        failure += 1
    return StemOperatorAudit('CLOSED_STEM_GAUGE_INTERCHANGE',len(gauges),len(templates),checks,squares,failure)


@dataclass(frozen=True)
class GaugeStep:
    source: StemGauge
    target: StemGauge


@dataclass(frozen=True)
class ShiftStep:
    turns: int

    def __post_init__(self) -> None:
        if type(self.turns) is not int or self.turns < 0:
            raise ValueError('shift must be nonnegative')


Step = GaugeStep | ShiftStep


@dataclass(frozen=True)
class WordNormalForm:
    """One shift, then two endpoint gauges; it is not an inverse shift.

    The form is a symbolic certificate of the mixed operator word, not an
    assertion that an erased process stem can be reconstructed from its tail.
    """
    removed_rules: int
    source: StemGauge
    target: StemGauge

    def act(self, arrow: MarkedArrow) -> MarkedArrow:
        return gauge_arrow(shift_arrow(arrow, self.removed_rules),
                           self.source, self.target)


def normalize_word(steps: tuple[Step, ...]) -> WordNormalForm:
    """Rewrite G;S_k -> S_k;shift_k(G), preserving transported incoming marks.

    Operator order is as written (first item acts first).
    Every output remains an admitted finite-stem gauge plus a forward shift.
    """
    identity = StemGauge.periodic(1, 1)
    shift = 0
    u, v = identity, identity
    for operation in steps:
        if isinstance(operation, GaugeStep):
            u = operation.source.compose(u)
            v = operation.target.compose(v)
        elif isinstance(operation, ShiftStep):
            shift += operation.turns
            u = u.shifted(operation.turns)
            v = v.shifted(operation.turns)
        else:
            raise TypeError('unadmitted operator step')
    return WordNormalForm(shift, u, v)


def execute_word(arrow: MarkedArrow, steps: tuple[Step, ...]) -> MarkedArrow:
    """Apply actions in order while retaining the gauge frame at every shift.

    The frame determines the source gain carried across a shifted root.
    Resetting it to one would make the desired normal form false.
    """
    u = StemGauge.periodic(1, 1)
    v = u
    state = arrow
    for operation in steps:
        if isinstance(operation, GaugeStep):
            state = gauge_arrow(state, operation.source, operation.target)
            u = operation.source.compose(u)
            v = operation.target.compose(v)
        elif isinstance(operation, ShiftStep):
            new_u, new_v = u.shifted(operation.turns), v.shifted(operation.turns)
            state = shift_arrow(state, operation.turns,
                                new_source_gain=new_u.incoming)
            u, v = new_u, new_v
        else:
            raise TypeError('unadmitted operator step')
    return state


def certify_word(arrow: MarkedArrow, steps: tuple[Step, ...]) -> bool:
    return same_arrow(execute_word(arrow, steps), normalize_word(steps).act(arrow))
