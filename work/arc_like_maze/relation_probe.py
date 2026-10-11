"""Bounded observation-guided identification of finite A/B transformation systems.

This is a mathematical probe, not a chatbot or general-purpose A/B solver.
It reuses the native finite-field laws and rooted alignment checker. The
observer supplies only equality of endpoints of two action words; the engine
chooses questions and filters candidate relations without an LLM.

A resolved class is CONDITIONAL on membership in the admitted candidate family.
A finite probe signature is never a certificate of that membership.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable

from .alignment import discover_alignment, equivalent_classes
from .math import World, inverse_candidates

Probe = tuple[str, str]
Observer = Callable[[Probe], bool]


@dataclass(frozen=True)
class Observation:
    probe: Probe
    equal: bool
    remaining: tuple[int, ...]


@dataclass(frozen=True)
class ProbeResult:
    status: str  # CONDITIONAL_CLASS / NO_MATCH / UNKNOWN_BUDGET
    candidate_indices: tuple[int, ...]
    observations: tuple[Observation, ...]


def endpoint_equal(system: World, probe: Probe) -> bool:
    """Relabeling-invariant observable from the declared origin."""
    return system.apply(probe[0]) == system.apply(probe[1])


def separating_probes(candidates: tuple[World, ...]) -> tuple[Probe, ...]:
    """Extract A/B-word collisions only from exact rooted alignment witnesses."""
    if not candidates or len(set(candidates)) != len(candidates):
        raise ValueError("candidate family must be nonempty and duplicate-free")
    probes: set[Probe] = set()
    for i, j in combinations(range(len(candidates)), 2):
        witness = discover_alignment(candidates[i], candidates[j])
        if witness.status == "UNKNOWN":
            raise ValueError("alignment budget exhausted: no probe admitted")
        if witness.status != "OPEN":
            continue
        if witness.conflicting_words is None:
            raise AssertionError("OPEN alignment lacks a separating witness")
        pair = tuple(sorted(witness.conflicting_words))
        if endpoint_equal(candidates[i], pair) == endpoint_equal(candidates[j], pair):
            raise AssertionError("witness does not separate the candidates")
        probes.add(pair)
    return tuple(sorted(probes, key=lambda p: (sum(map(len, p)), max(map(len, p)), p)))


def identify(
    candidates: tuple[World, ...],
    observe: Observer,
    probes: tuple[Probe, ...],
    *,
    max_queries: int | None = None,
) -> ProbeResult:
    """Choose next separating observation without inspecting the hidden law.

    A nonempty result is only a class conditional on supplied family membership.
    Query limits stop as UNKNOWN_BUDGET, never as a positive classification.
    """
    if not candidates:
        raise ValueError("candidate family must be nonempty")
    if max_queries is not None and max_queries < 0:
        raise ValueError("max_queries must be nonnegative")
    remaining = tuple(range(len(candidates)))
    observations: list[Observation] = []
    while True:
        available = []
        for pair in probes:
            yes = tuple(i for i in remaining if endpoint_equal(candidates[i], pair))
            no = tuple(i for i in remaining if not endpoint_equal(candidates[i], pair))
            if yes and no:
                available.append((max(len(yes), len(no)), abs(len(yes) - len(no)),
                                  sum(map(len, pair)), pair))
        if not available:
            return ProbeResult("CONDITIONAL_CLASS", remaining, tuple(observations))
        if max_queries is not None and len(observations) >= max_queries:
            return ProbeResult("UNKNOWN_BUDGET", remaining, tuple(observations))
        pair = min(available)[-1]
        observed = bool(observe(pair))
        remaining = tuple(i for i in remaining if endpoint_equal(candidates[i], pair) == observed)
        observations.append(Observation(pair, observed, remaining))
        if not remaining:
            return ProbeResult("NO_MATCH", (), tuple(observations))


def main() -> None:
    candidates = inverse_candidates()
    probes = separating_probes(candidates)
    classes = equivalent_classes(candidates)
    assert sorted(len(c) for c in classes) == [1, 2, 2, 2, 2]
    query_counts = []
    for target in candidates:
        result = identify(candidates, lambda p, t=target: endpoint_equal(t, p), probes)
        expected = next(group for group in classes if target in group)
        assert result.status == "CONDITIONAL_CLASS"
        assert tuple(candidates[i] for i in result.candidate_indices) == expected
        query_counts.append(len(result.observations))

    print("Scope: nine F3^3 candidate transformation systems, rooted A/B action")
    print("Exact reachable classes:", [[w.phi for w in group] for group in classes])
    print("Separating probe pairs:", len(probes), "queries needed:", query_counts)
    outsider = World(3, (1, 0, 0))  # Outside the declared phi(0)=0 grammar
    result = identify(candidates, lambda p: endpoint_equal(outsider, p), probes)
    print("Outside-family negative control:", outsider.phi,
          "matches candidate signature", [candidates[i].phi for i in result.candidate_indices])
    print("Interpretation: classification remains conditional; membership unproved")


if __name__ == "__main__":
    main()
