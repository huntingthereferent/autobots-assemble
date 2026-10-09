"""Audit shifts of entire periodic inverse-A/B construction processes.

A coinductive shift loop is an exact equivalence between the WHOLE
infinite generated action systems at each phase, with a consistent
diagonal coordinate alignment. It is not a finite state-loop, nor is
a shift of rule templates the projection between existing dimensions.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product

from .process_alignment import (
    CoinductiveAlignment, PeriodicProcess, compare_shift, find_process_alignment,
)


@dataclass(frozen=True)
class ShiftOrbitCertificate:
    status: str
    distinct_turns: int
    verified_edges: int
    failure_turn: int | None
    failure_coordinate_depth: int | None
    witnesses: tuple[CoinductiveAlignment, ...] = ()


def certify_shift_orbit(process: PeriodicProcess) -> ShiftOrbitCertificate:
    """Check every distinct phase, not merely the first P ~ shift(P) pair."""
    if process.stem:
        return ShiftOrbitCertificate("UNKNOWN_NONCYCLIC_STEM", 0, 0, None, None)
    period = len(process.period)
    fundamental = next(k for k in range(1, period + 1)
                       if period % k == 0 and
                       all(process.rule(i) == process.rule(i % k) for i in range(period)))
    witnesses = []
    for phase in range(fundamental):
        source = process.shift(phase)
        witness = compare_shift(source)
        if witness.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT":
            return ShiftOrbitCertificate(
                "OPEN_SHIFT_ORBIT", fundamental, phase,
                phase, witness.first_impossible_depth, tuple(witnesses),
            )
        witnesses.append(witness)
    return ShiftOrbitCertificate(
        "CLOSED_COINDUCTIVE_SHIFT_ORBIT", fundamental, fundamental,
        None, None, tuple(witnesses),
    )


@dataclass(frozen=True)
class TwoPhaseAudit:
    status: str
    templates: int
    process_classes: int
    class_size_distribution: tuple[tuple[int, int], ...]
    one_turn_closed: int
    changing_one_turn_closed: int
    first_counterexample: tuple[int, int] | None = None


def audit_two_phase_templates() -> TwoPhaseAudit:
    """Exhaust 9^2 period-2 streams under all-depth diagonal equivalence.

    Distinct parameter pairs are separate construction descriptions. Their
    equivalence is decided by finite-state coinduction, not by matching a
    few finite projected worlds. Counts are scoped to F_3 tables fixing 0.
    """
    rules = tuple((0, a, b) for a, b in product(range(3), repeat=2))
    processes = tuple(PeriodicProcess.repeat(a, b)
                      for a, b in product(rules, repeat=2))
    remaining = list(processes)
    groups = []
    while remaining:
        representative = remaining.pop(0)
        same = [representative]
        different = []
        for other in remaining:
            alignment = find_process_alignment(representative, other)
            if alignment.status == "COINDUCTIVE_DIAGONAL_ALIGNMENT":
                same.append(other)
            else:
                different.append(other)
        groups.append(tuple(same))
        remaining = different

    # Check every pair within each equivalence class and each pair
    # of class representatives. This guards against classification drift.
    for i, group in enumerate(groups):
        for j, source in enumerate(group):
            for target in group[j + 1:]:
                if find_process_alignment(source, target).status != "COINDUCTIVE_DIAGONAL_ALIGNMENT":
                    return TwoPhaseAudit("OPEN_INCONSISTENT_EQUIVALENCE",81,len(groups),(),0,0,(i,j))
        for other in groups[i + 1:]:
            if find_process_alignment(group[0],other[0]).status == "COINDUCTIVE_DIAGONAL_ALIGNMENT":
                return TwoPhaseAudit("OPEN_INCONSISTENT_PARTITION",81,len(groups),(),0,0,(i,i+1))

    rotations = tuple(certify_shift_orbit(process) for process in processes)
    if any(c.status not in ("CLOSED_COINDUCTIVE_SHIFT_ORBIT", "OPEN_SHIFT_ORBIT")
           for c in rotations):
        return TwoPhaseAudit("UNKNOWN_SHIFT_ORBIT",len(processes),len(groups),(),0,0)

    closed = [process for process, cert in zip(processes, rotations)
              if cert.status == "CLOSED_COINDUCTIVE_SHIFT_ORBIT"]
    return TwoPhaseAudit(
        "EXACT_PERIOD_TWO_DIAGONAL_CLASSIFICATION",
        len(processes),
        len(groups),
        tuple(sorted(Counter(len(g) for g in groups).items())),
        len(closed),
        sum(process.rule(0) != process.rule(1) for process in closed),
    )
