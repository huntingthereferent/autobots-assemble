"""Operators on complete eventually periodic A/B construction processes.

Exact scope:
- a coordinate gauge has an eventually periodic, nonzero F_3 scale law;
- its induced world-rule change is fixed by a commuting A/B square;
- period-two gauge schedules form a four-element group acting on ALL
  eventually periodic process blueprints, not necessarily preserving
  strict period-two syntax (a first-rule stem can appear);
- shift and additive coupling modification are genuine operators on
  descriptions but NOT automatically maps of diagonal-equivalence classes.

An operator being invertible on descriptions is not enough to descend
to the quotient. No universal A/B construction theorem is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import lcm

from .process_alignment import (
    IDENTITY, NEGATIVE, ZERO, PeriodicProcess, find_process_alignment,
    verify_lasso,
)

Rule = tuple[int, int, int]


@dataclass(frozen=True)
class GaugeSchedule:
    """A repeating scale sequence for coordinates x_2,x_3,..., over F_3."""
    period: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.period or any(type(s) is not int or s not in (1, 2)
                                  for s in self.period):
            raise ValueError("gauge schedule must have nonempty F_3-unit period")

    def scale(self, index: int) -> int:
        if type(index) is not int or index < 0:
            raise ValueError("scale coordinate must be nonnegative")
        return self.period[index % len(self.period)]

    def compose(self, other: "GaugeSchedule") -> "GaugeSchedule":
        """Apply other first, then self; multiplication of coordinate units."""
        n = lcm(len(self.period), len(other.period))
        return GaugeSchedule(tuple(self.scale(i) * other.scale(i) % 3
                                   for i in range(n)))

    def inverse(self) -> "GaugeSchedule":
        """Both units of F_3 are self-inverse."""
        return self

    def apply(self, process: PeriodicProcess) -> PeriodicProcess:
        """Construct rule stream Q with Q_i(s_(i-1)u) = s_i P_i(u).

        s_-1 = 1 preserves the first two state coordinates and rooted
        origin. For i>=1 the scale sequence is periodic; after a finite
        stem this constructs another eventually periodic process.

        The rule equation is an EXACT, all-depth A/B conjugacy; it also
        commutes with forgetting the newest state coordinate.
        """
        def transformed(index: int) -> Rule:
            prev = 1 if index == 0 else self.scale(index - 1)
            current = self.scale(index)
            before = process.rule(index)
            result = [0, 0, 0]
            for u in range(3):
                result[(prev * u) % 3] = (current * before[u]) % 3
            return tuple(result)  # type: ignore[return-value]

        prefix = max(1, len(process.stem))
        period = lcm(len(process.period), len(self.period))
        return PeriodicProcess(
            tuple(transformed(i) for i in range(prefix)),
            tuple(transformed(i) for i in range(prefix, prefix + period)),
        )


def same_rule_stream(left: PeriodicProcess, right: PeriodicProcess) -> bool:
    """Decide exact equality of eventually periodic infinite rule streams."""
    start = max(len(left.stem), len(right.stem))
    period = lcm(len(left.period), len(right.period))
    return all(left.rule(i) == right.rule(i)
               for i in range(start + period))


@dataclass(frozen=True)
class AddRule:
    """Syntactic reversible transformation r_i(u) -> r_i(u) + q(u)."""
    increment: Rule = IDENTITY

    def __post_init__(self) -> None:
        if (len(self.increment) != 3 or self.increment[0] != 0 or
                any(type(x) is not int or x not in range(3) for x in self.increment)):
            raise ValueError("F_3 coupling increment must fix zero")

    def apply(self, process: PeriodicProcess) -> PeriodicProcess:
        def add(rule: Rule) -> Rule:
            return tuple((a + b) % 3 for a, b in zip(rule, self.increment))  # type: ignore[return-value]
        return PeriodicProcess(
            tuple(add(r) for r in process.stem),
            tuple(add(r) for r in process.period),
        )

    def compose(self, other: "AddRule") -> "AddRule":
        return AddRule(tuple((a+b) % 3 for a, b
                             in zip(self.increment, other.increment)))  # type: ignore[arg-type]


@dataclass(frozen=True)
class QuotientBreak:
    operation: str
    left: PeriodicProcess
    right: PeriodicProcess
    before: str
    after: str
    first_impossible_depth: int | None


def find_operator_breaks() -> tuple[QuotientBreak, QuotientBreak]:
    """Concrete failure of shift and additive rule movement on the quotient.

    Shift is bijective on STRICT period-two templates (shift squared is
    identity), but loses the first-input gauge freedom of a zero rule.
    Adding identity is a reversible order-three rule-table operation;
    it can still map aligned worlds to misaligned worlds.
    """
    p = PeriodicProcess.repeat(ZERO, (0, 0, 1))
    q = PeriodicProcess.repeat(ZERO, (0, 1, 0))
    before_shift = find_process_alignment(p, q)
    after_shift = find_process_alignment(p.shift(1), q.shift(1))

    a = PeriodicProcess.repeat(IDENTITY)
    b = PeriodicProcess.repeat(NEGATIVE)
    before_add = find_process_alignment(a, b)
    operation = AddRule()
    after_add = find_process_alignment(operation.apply(a), operation.apply(b))
    if (before_shift.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT" or
            before_add.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT" or
            after_shift.status != "OPEN_DIAGONAL_ALIGNMENT" or
            after_add.status != "OPEN_DIAGONAL_ALIGNMENT"):
        raise AssertionError("operator-quotient counterexamples no longer valid")
    return (
        QuotientBreak("shift", p, q, before_shift.status,
                      after_shift.status, after_shift.first_impossible_depth),
        QuotientBreak("add-identity", a, b, before_add.status,
                      after_add.status, after_add.first_impossible_depth),
    )


@dataclass(frozen=True)
class OperatorAudit:
    status: str
    period_two_gauges: int
    examined_rule_templates: int
    all_depth_gauge_witnesses: int
    composition_checks: int
    shift_descends: bool
    additive_descends: bool
    shift_break_depth: int | None
    additive_break_depth: int | None


def audit_process_operators() -> OperatorAudit:
    """Exhaust the 4-element gauge group on all 81 period-two inputs.

    Also check the two counterexamples against transformations that
    are algebraically legitimate on raw process descriptions but fail
    to respect all-depth diagonal-equivalence classes.
    """
    gauges = tuple(GaugeSchedule(tuple(s))
                   for s in product((1, 2), repeat=2))
    processes = tuple(PeriodicProcess.repeat((0, a, b), (0, c, d))
                      for a, b, c, d in product(range(3), repeat=4))
    keys = {g.period for g in gauges}
    witnesses = 0
    for gauge in gauges:
        for process in processes:
            transformed = gauge.apply(process)
            certificate = find_process_alignment(process, transformed)
            if (certificate.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT" or
                    not verify_lasso(process, transformed, certificate)):
                return OperatorAudit("OPEN_GAUGE_ALIGNMENT", len(gauges),
                                     len(processes), witnesses, 0,
                                     False, False, None, None)
            witnesses += 1
    checks = 0
    identity = GaugeSchedule((1, 1))
    for left in gauges:
        if left.compose(left.inverse()).period not in keys:
            raise AssertionError("inverse escaped admitted gauge family")
        for right in gauges:
            composite = left.compose(right)
            if composite.period not in keys:
                raise AssertionError("gauge family failed composition closure")
            for process in processes:
                checks += 1
                if not same_rule_stream(left.apply(right.apply(process)),
                                        composite.apply(process)):
                    return OperatorAudit("OPEN_COMPOSITION", len(gauges),
                                         len(processes), witnesses, checks,
                                         False, False, None, None)
                if not same_rule_stream(identity.apply(process), process):
                    raise AssertionError("gauge identity failed")
    shift, addition = find_operator_breaks()
    return OperatorAudit(
        "CLOSED_GAUGE_GROUP_NOT_ALL_PROCESS_OPERATORS", len(gauges),
        len(processes), witnesses, checks, False, False,
        shift.first_impossible_depth, addition.first_impossible_depth,
    )
