"""Finite-model continuity: minimal checks under *proved/source-owned* structure.

A/B is the investigator's language for continuing witnessed relationships;
these A/B-named finite generators are one mathematical test representation.

Claims here distinguish an observed changed edge, a black-box match, and a
match certified relative to an explicitly source-owned finite law family.
The source-owned guarantee is an *in-process construction* guarantee, not a
signature, an external oracle authentication, or evidence of time-immutability.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import (
    DOMAIN, DOMAIN_SET, Discovery, State, Step, verify_recorded_full,
)


@dataclass(frozen=True)
class EdgeWitness:
    state: State
    action: str
    old_value: State
    new_value: object


@dataclass(frozen=True)
class StabilityResult:
    status: str  # CHANGED / CONDITIONAL_MATCH / VERIFIED_WITHIN_OWNED_FAMILY /
                 # OBSERVED_FULL_TABLE_MATCH / UNKNOWN_BUDGET / WALL_INVALID
    observations: tuple[EdgeWitness, ...]
    scope: str

    @property
    def calls(self) -> int:
        return len(self.observations)


def _state(x: object) -> bool:
    return type(x) is tuple and len(x) == 3 and all(type(v) is int and v in (0, 1, 2) for v in x)


def _baseline(source: FiniteSystem, prior: Discovery) -> tuple[dict[State, State], dict[tuple[State, str], State]]:
    """Check the prior full recorded mathematical witness before reusing it."""
    if type(source) is not FiniteSystem or not verify_recorded_full(source, prior):
        raise ValueError('previous full A/B correspondence must be recorded and replay-valid')
    mapping = dict(prior.full_pairs)
    old = {(o.state, o.action): o.output for o in prior.observed}
    if len(old) != 54 or set(mapping) != DOMAIN_SET or set(mapping.values()) != DOMAIN_SET:
        raise ValueError('previous record is not a complete witnessed map')
    return mapping, old


@dataclass(frozen=True)
class TransportedLaw:
    """Owned construction of H A H^-1 and H B_phi H^-1, not an opaque oracle.

    `correspondence` is a 27-element tuple of target labels in DOMAIN order.
    Immutable parameters and exact owned-method identity provide an in-process
    *construction* guarantee that all edges obey this family. They do not prove
    any outside target actually follows this code or keeps running this version.
    """

    phi: tuple[int, int, int]
    correspondence: tuple[State, ...]
    require_phi0_zero: bool = False

    def __post_init__(self) -> None:
        if (type(self.phi) is not tuple or len(self.phi) != 3 or
                any(type(v) is not int or v not in (0, 1, 2) for v in self.phi)):
            raise ValueError('phi must consist of three F3 elements')
        if (type(self.correspondence) is not tuple or len(self.correspondence) != 27 or
                set(self.correspondence) != DOMAIN_SET):
            raise ValueError('correspondence must be a full bijection of F3^3')
        if type(self.require_phi0_zero) is not bool:
            raise ValueError('invalid declared subfamily')
        if self.require_phi0_zero and self.phi[0] != 0:
            raise ValueError('phi(0)=0 subfamily requirement violated')

    def step(self, state: State, action: str) -> State:
        if state not in DOMAIN_SET or action not in ('A', 'B'):
            raise ValueError('outside declared state/action domain')
        source_state = DOMAIN[self.correspondence.index(state)]
        next_state = FiniteSystem(self.phi).step(source_state, action)
        return self.correspondence[DOMAIN.index(next_state)]


def _owned_family_ok(
    owned: TransportedLaw | None, observe_current: Step, mapping: dict[State, State],
) -> bool:
    if owned is None:
        return False
    if (type(owned) is not TransportedLaw or
            getattr(observe_current, '__self__', None) is not owned or
            getattr(observe_current, '__func__', None) is not TransportedLaw.step or
            owned.correspondence != tuple(mapping[s] for s in DOMAIN)):
        raise ValueError('structural guarantee not owned by current oracle and witnessed H')
    return True


def compare_anchor_stability(
    source: FiniteSystem,
    prior: Discovery,
    observe_current: Step,
    *,
    owned_family: TransportedLaw | None = None,
    max_queries: int = 3,
) -> StabilityResult:
    """Check changed B anchors, keeping membership and identity distinct.

    Three transported B anchors discriminate all 27 laws under a *fixed H* and
    fixed A. When an owned law also guarantees phi(0)=0, two are sufficient.
    Otherwise agreement on three anchors is only a conditional signature.
    No unverified caller-supplied `trust=True` switch is available.
    """
    if type(max_queries) is not int or max_queries < 0:
        raise ValueError('max_queries must be a nonnegative integer')
    mapping, old = _baseline(source, prior)
    owns_structure = _owned_family_ok(owned_family, observe_current, mapping)
    short = owns_structure and owned_family.require_phi0_zero and source.phi[0] == 0
    positions = (1, 2) if short else (0, 1, 2)
    seen: list[EdgeWitness] = []
    for j in positions:
        if len(seen) >= max_queries:
            return StabilityResult('UNKNOWN_BUDGET', tuple(seen), 'insufficient anchor observations')
        state = mapping[(0, j, 0)]
        expected = old[(state, 'B')]
        actual = observe_current(state, 'B')
        seen.append(EdgeWitness(state, 'B', expected, actual))
        if not _state(actual):
            return StabilityResult('WALL_INVALID', tuple(seen), 'invalid observed transition')
        if actual != expected:
            return StabilityResult('CHANGED', tuple(seen), 'a witnessed prior B edge changed')
    return StabilityResult(
        'VERIFIED_WITHIN_OWNED_FAMILY' if owns_structure else 'CONDITIONAL_MATCH',
        tuple(seen),
        ('same entire A/B law under owned immutable parameters and fixed H'
         if owns_structure else
         'three B anchors match; external structural membership and full stability are UNKNOWN'),
    )


def recheck_full_record(
    source: FiniteSystem, prior: Discovery, observe_current: Step, *,
    max_queries: int = 54,
) -> StabilityResult:
    """Reread old transition entries; does NOT prove target was atomic/stable.

    Unrestricted target table: an unqueried value can differ. `OBSERVED_*`
    asserts comparison of 54 observations, not permanence beyond the reads.
    """
    if type(max_queries) is not int or max_queries < 0:
        raise ValueError('max_queries must be a nonnegative integer')
    _, old = _baseline(source, prior)
    seen: list[EdgeWitness] = []
    for state in DOMAIN:
        for action in 'AB':
            if len(seen) >= max_queries:
                return StabilityResult('UNKNOWN_BUDGET', tuple(seen), 'not all old edges were reread')
            expected = old[(state, action)]
            actual = observe_current(state, action)
            seen.append(EdgeWitness(state, action, expected, actual))
            if not _state(actual):
                return StabilityResult('WALL_INVALID', tuple(seen), 'invalid observed transition')
            if actual != expected:
                return StabilityResult('CHANGED', tuple(seen), 'a previously recorded transition differs')
    return StabilityResult('OBSERVED_FULL_TABLE_MATCH', tuple(seen),
                           'all 54 rereads matched, conditional on one coherent observation interval')


def recheck_bijective_target(
    source: FiniteSystem, prior: Discovery, observe_current: Step, *,
    independently_guaranteed_bijective: bool = False,
    max_queries: int = 52,
) -> StabilityResult:
    """26 edges per permutation suffice IF target's A and B are guaranteed bijections.

    Merely observing 26 distinct outputs does NOT prove the 27th is a
    permutation output; no such proof is provided by this black-box interface.
    The caller's guarantee is an explicit *conditional assumption*, not attested.
    """
    if type(max_queries) is not int or max_queries < 0:
        raise ValueError('max_queries must be a nonnegative integer')
    if independently_guaranteed_bijective is not True:
        return StabilityResult('UNKNOWN_STRUCTURE', (), 'new target permutations not independently witnessed')
    _, old = _baseline(source, prior)
    seen: list[EdgeWitness] = []
    for action in 'AB':
        for state in DOMAIN[:-1]:
            if len(seen) >= max_queries:
                return StabilityResult('UNKNOWN_BUDGET', tuple(seen), 'not enough permutation checks')
            expected = old[(state, action)]
            actual = observe_current(state, action)
            seen.append(EdgeWitness(state, action, expected, actual))
            if not _state(actual):
                return StabilityResult('WALL_INVALID', tuple(seen), 'invalid observed transition')
            if actual != expected:
                return StabilityResult('CHANGED', tuple(seen), 'prior generator edge differs')
    return StabilityResult('CONDITIONAL_ON_BIJECTIVITY', tuple(seen),
                           '26/27 edges per generator force missing two under an independent permutation guarantee')


def main() -> None:
    from ab_chatbot_discovered_correspondence import discover
    s0 = FiniteSystem((0, 0, 0))
    H = tuple((i, j, (k + i*j) % 3) for i, j, k in DOMAIN)
    old = TransportedLaw(s0.phi, H)
    previous = discover(s0, old.step, full=True)
    assert previous.status == 'FULL_CONJUGACY'
    recovered_h = tuple(dict(previous.full_pairs)[s] for s in DOMAIN)
    stable = TransportedLaw(s0.phi, recovered_h)
    wrong = TransportedLaw((0, 2, 1), recovered_h)
    print('Current referent: reuse a recorded finite-model correspondence')
    print('Owned structure, unchanged:', compare_anchor_stability(s0, previous, stable.step).status)
    print('Owned structure, unchanged + guarantee:', compare_anchor_stability(
        s0, previous, stable.step, owned_family=stable).status)
    print('Changed law:', compare_anchor_stability(
        s0, previous, wrong.step, owned_family=wrong).status)
    print('No structure / full reread:', recheck_full_record(s0, previous, stable.step).calls)
    print('Bijection conditional / reread:', recheck_bijective_target(
        s0, previous, stable.step, independently_guaranteed_bijective=True).calls)
    assert all(x.status in {'CHANGED', 'VERIFIED_WITHIN_OWNED_FAMILY'} for x in (
        compare_anchor_stability(s0, previous, stable.step, owned_family=stable),
        compare_anchor_stability(s0, previous, wrong.step, owned_family=wrong),
    ))


if __name__ == '__main__':
    main()
