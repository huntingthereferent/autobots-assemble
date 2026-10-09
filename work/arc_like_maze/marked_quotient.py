"""Finite, witness-complete marked-process quotient for a declared gauge family.

Starting family: all 81 strictly two-periodic F_3 coupling streams, at
both root gains. Close under the eight boundary-aware period-two gauges.
All resulting streams admit the canonical (one-rule stem, two-rule tail)
representation. The resulting 270 objects carry FULL marked-root dynamics,
not just the origin-reachable quotient of earlier finite coupling worlds.

There are two DISTINCT quotients: gauge-orbits under the eight admitted
period-two operators, and coinductively verified *diagonal* alignment.
The latter permits finite-head, eventually-periodic scalar witnesses.

No unrestricted A/B conjugacy, arbitrary process oracle, or native ARC
claim is implied.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product

from .marked_operator_system import (
    BoundaryGauge, MarkedArrow, MarkedObject, compose_arrows,
    invert_arrow, transform_arrow,
)
from .root_transport import Process, Rule, Witness, find, verify

ObjectKey = tuple[int, Rule, Rule, Rule]


def object_key(obj: MarkedObject) -> ObjectKey:
    """Exact full-stream key *only* for streams with <=1 stem and period <=2."""
    p = obj.process
    if len(p.stem) > 1 or len(p.period) not in (1, 2):
        raise ValueError("object is outside the canonical one-stem/two-tail family")
    return (obj.gain, p.rule(0), p.rule(1), p.rule(2))


def canonical(obj: MarkedObject) -> MarkedObject:
    """Preserve complete stream semantics while normalizing representation."""
    _, a, b, c = object_key(obj)
    return MarkedObject(Process((a,), (b, c)), obj.gain)


def gauge_eight() -> tuple[BoundaryGauge, ...]:
    return tuple(BoundaryGauge(incoming, (first, second))
                 for incoming, first, second in product((1, 2), repeat=3))


def seeds() -> tuple[MarkedObject, ...]:
    rules = tuple((0, a, b) for a, b in product(range(3), repeat=2))
    return tuple(MarkedObject(Process.repeat(first, second), gain)
                 for gain in (1, 2) for first in rules for second in rules)


def apply_gauge(obj: MarkedObject, gauge: BoundaryGauge) -> MarkedObject:
    """Source object changed by a full boundary-aware periodic gauge."""
    if len(gauge.period) != 2:
        raise ValueError("the declared finite operator family is period two")
    return canonical(MarkedObject(gauge.apply(obj.process),
                                  obj.gain * gauge.incoming % 3))


def objects() -> tuple[MarkedObject, ...]:
    """Complete orbit-closure of 162 seeds under the exact eight-gauge group."""
    members = {}
    for source in seeds():
        for gauge in gauge_eight():
            image = apply_gauge(source, gauge)
            members[object_key(image)] = image
    return tuple(members[key] for key in sorted(members))


def gauge_orbits() -> tuple[tuple[MarkedObject, ...], ...]:
    """Exact finite partition into eight-gauge orbits of *marked* objects."""
    universe = {object_key(obj): obj for obj in objects()}
    unassigned = set(universe)
    groups = []
    gauges = gauge_eight()
    for key in sorted(universe):
        if key not in unassigned:
            continue
        rep = universe[key]
        images = {object_key(apply_gauge(rep, gauge)) for gauge in gauges}
        if not images.issubset(universe):
            raise AssertionError("the finite gauge family left the closed universe")
        if not images.issubset(unassigned):
            raise AssertionError("computed gauge orbit overlaps a previous orbit")
        groups.append(tuple(universe[k] for k in sorted(images)))
        unassigned.difference_update(images)
    if unassigned:
        raise AssertionError("gauge orbit partition left an object unassigned")
    return tuple(groups)


def marked_alignment(source: MarkedObject, target: MarkedObject) -> Witness | None:
    """Require the EXACT incoming root gain ratio and a full coinductive proof."""
    incoming = target.gain * source.gain % 3  # inverse of unit = itself in F_3
    witness = find(source.process, target.process, incoming)
    if witness.status != "ALIGNED":
        return None
    if not verify(source.process, target.process, witness):
        raise AssertionError("solver issued an unverified infinite witness")
    # The constructor checks both marked endpoints and the full lasso again.
    MarkedArrow(source, target, witness)
    return witness


def alignment_classes() -> tuple[tuple[MarkedObject, ...], ...]:
    """The complete diagonal-alignment quotient of this 270-object universe.

    Exhaust only 36 gauge-orbit representatives with the complete coinductive
    decision algorithm. Gauge orbits lie within exact alignment classes and
    diagonal alignment is transitive, so the quotient of orbits is exact.
    """
    orbits = gauge_orbits()
    remaining = set(range(len(orbits)))
    groups = []
    for i in range(len(orbits)):
        if i not in remaining:
            continue
        hit = []
        rep = orbits[i][0]
        for j in sorted(remaining):
            if marked_alignment(rep, orbits[j][0]) is not None:
                hit.append(j)
        if not hit or i not in hit:
            raise AssertionError("marked diagonal alignment lost identity")
        groups.append(tuple(obj for j in hit for obj in orbits[j]))
        remaining.difference_update(hit)
    return tuple(groups)


@dataclass(frozen=True)
class MissingGaugeBridge:
    source: MarkedObject
    target: MarkedObject
    witness: Witness
    source_periodic_orbit_size: int
    target_periodic_orbit_size: int

    def arrow(self) -> MarkedArrow:
        return MarkedArrow(self.source, self.target, self.witness)


def missing_bridges() -> tuple[MissingGaugeBridge, ...]:
    """Produce exact arrows that a STRICT period-two gauge cannot realize."""
    orbits = gauge_orbits()
    universe = {object_key(obj): i
                for i, orbit in enumerate(orbits) for obj in orbit}
    bridges = []
    for cls in alignment_classes():
        members = {}
        for obj in cls:
            i = universe[object_key(obj)]
            members.setdefault(i, obj)
        if len(members) <= 1:
            continue
        head = min(members)
        for tail in sorted(members):
            if tail == head:
                continue
            source, target = members[head], members[tail]
            witness = marked_alignment(source, target)
            if witness is None:
                raise AssertionError("class merge lacks complete marked witness")
            if any(object_key(apply_gauge(source, gauge)) == object_key(target)
                   for gauge in gauge_eight()):
                raise AssertionError("bridge was already periodic-gauge equivalent")
            bridges.append(MissingGaugeBridge(
                source, target, witness, len(orbits[head]), len(orbits[tail])
            ))
    return tuple(bridges)


@dataclass(frozen=True)
class MarkedQuotientCertificate:
    status: str
    seed_objects: int
    closed_objects: int
    period_two_gauges: int
    gauge_orbits: int
    coinductive_classes: int
    gauge_orbit_sizes: tuple[tuple[int, int], ...]
    alignment_class_sizes: tuple[tuple[int, int], ...]
    nonperiodic_bridges: int
    failure: str | None = None


def certify_marked_quotient() -> MarkedQuotientCertificate:
    universe = objects()
    gauges = gauge_eight()
    orbits = gauge_orbits()
    groups = alignment_classes()
    bridges = missing_bridges()
    hist_gauge = tuple(sorted(Counter(map(len, orbits)).items()))
    hist_classes = tuple(sorted(Counter(map(len, groups)).items()))
    status = "CLOSED_GAUGE_ACTION_INCOMPLETE_FOR_COINDUCTIVE_ARROWS"
    failure = None
    if (len(seeds()), len(universe), len(gauges), len(orbits),
        len(groups), len(bridges)) != (162, 270, 8, 36, 34, 2):
        status = "OPEN_UNEXPECTED_CLASSIFICATION"
        failure = "object closure, operator orbit or witness quotient diverged"
    if sum(len(g) for g in groups) != len(universe):
        status, failure = "OPEN_INCOMPLETE_PARTITION", "alignment groups lost objects"
    return MarkedQuotientCertificate(
        status, len(seeds()), len(universe), len(gauges),
        len(orbits), len(groups), hist_gauge, hist_classes,
        len(bridges), failure
    )
