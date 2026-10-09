"""Construct and classify a two-relation A/B family, not native ARC gameplay.

Phi controls coordinate 2, h independently controls coordinate 3.
The 21-class certificate concerns the ORIGIN-REACHABLE rooted A/B graph.
Full inverse-limit equivalence is a stronger condition, treated separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

from .alignment import discover_alignment, equivalent_classes

Rule = tuple[int, int, int]
State = tuple[int, ...]


def _validate_rule(rule: Rule) -> None:
    if len(rule) != 3 or rule[0] != 0 or any(type(v) is not int or v not in range(3) for v in rule):
        raise ValueError("rule must be (0,a,b) over F_3")


@dataclass(frozen=True)
class CoupledWorld:
    depth: int
    phi: Rule
    h: Rule

    def __post_init__(self) -> None:
        if self.depth < 3:
            raise ValueError("world depth must be at least three")
        _validate_rule(self.phi)
        _validate_rule(self.h)

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def step(self, state: State, action: str) -> State:
        if len(state) != self.depth or any(type(v) is not int or v not in range(3) for v in state):
            raise ValueError("state shape or digit invalid")
        next_state = list(state)
        if action == "A":
            next_state[0] = (state[0] + 1) % 3
        elif action == "B":
            next_state[1] = (state[1] + state[0] + 1) % 3
            next_state[2] = (state[2] + self.phi[state[1]]) % 3
            if self.depth >= 4:
                next_state[3] = (state[3] + self.h[state[2]]) % 3
            for i in range(4, self.depth):
                next_state[i] = (state[i] + state[i - 1]) % 3
        else:
            raise ValueError("action must be A or B")
        return tuple(next_state)

    def inverse(self, state: State, action: str) -> State:
        if len(state) != self.depth or any(type(v) is not int or v not in range(3) for v in state):
            raise ValueError("state shape or digit invalid")
        before = list(state)
        if action == "A":
            before[0] = (state[0] - 1) % 3
        elif action == "B":
            before[1] = (state[1] - state[0] - 1) % 3
            before[2] = (state[2] - self.phi[before[1]]) % 3
            if self.depth >= 4:
                before[3] = (state[3] - self.h[before[2]]) % 3
            for i in range(4, self.depth):
                before[i] = (state[i] - before[i - 1]) % 3
        else:
            raise ValueError("action must be A or B")
        return tuple(before)


def all_couplings(depth: int = 4) -> tuple[CoupledWorld, ...]:
    rules = tuple((0,a,b) for a,b in product(range(3), repeat=2))
    return tuple(CoupledWorld(depth, phi, h) for phi in rules for h in rules)


def scale_world(state: State, phi_scale: int, tail_scale: int) -> State:
    """Coherent all-depth rooted conjugacy when phi' and h' are scaled.

    Coordinate 2 receives phi_scale; all coordinates >=3 receive tail_scale.
    """
    if len(state) < 3 or any(type(v) is not int or v not in range(3) for v in state):
        raise ValueError("invalid state")
    if phi_scale not in (1,2) or tail_scale not in (1,2):
        raise ValueError("both scales must be nonzero")
    return state[:2] + ((phi_scale * state[2]) % 3,) + tuple((tail_scale * v) % 3 for v in state[3:])


def scaling_witness(source: CoupledWorld, target: CoupledWorld) -> tuple[int,int] | None:
    """Search the explicit two-scalar all-depth conjugacy family."""
    for s,t in product((1,2), repeat=2):
        if tuple(s*v%3 for v in source.phi) != target.phi:
            continue
        if all(target.h[(s*k)%3] == (t*source.h[k])%3 for k in range(3)):
            return s,t
    return None


@dataclass(frozen=True)
class CouplingCertificate:
    status: str
    worlds: int
    rooted_classes: int
    class_sizes: tuple[int, ...]
    verified_equivalences: int
    scoped_orbit_only_pairs: int
    witness_depth: int
    failure: str | None = None


def certify_coupling_family(*, depth: int = 4) -> CouplingCertificate:
    """Exact finite rooted partition plus all-depth formula for admitted pairs.

    phi=0 cases can be indistinguishable only on the origin orbit: h is
    never visited. Do not promote that special degeneracy to an isomorphism
    of FULL infinite-coordinate dynamical systems.
    """
    if depth < 4:
        return CouplingCertificate("UNKNOWN", 0, 0, (), 0, 0, depth,
                                   "h is not visible before depth four")
    worlds = all_couplings(depth)
    groups = equivalent_classes(worlds)
    checked = 0
    orbit_only = 0
    for group in groups:
        for index, source in enumerate(group):
            for target in group[index+1:]:
                witness = discover_alignment(source, target)
                if not witness.aligned:
                    return CouplingCertificate("OPEN", len(worlds),len(groups),
                        (), checked, orbit_only, depth,"group has non-equivalent pair")
                checked += 1
                if source.phi == (0,0,0) and source.h != target.h:
                    orbit_only += 1
                elif scaling_witness(source,target) is None:
                    return CouplingCertificate("OPEN",len(worlds),len(groups),
                        (),checked,orbit_only,depth,"same-class pair has no all-depth scalar witness")
    return CouplingCertificate("CLOSED_ROOTED_CLASSES_IN_DECLARED_FAMILY",len(worlds),
        len(groups),tuple(sorted(len(g) for g in groups)),checked,orbit_only,depth)


@dataclass(frozen=True)
class RotationCertificate:
    """An explicitly chosen constructor, not a unique inverse A/B solution."""
    status: str
    worlds: int
    classes: int
    orbit_lengths: tuple[int, ...]
    global_order: int
    moved_every_world: bool


def rotate_within_class(depth: int = 4) -> dict[CoupledWorld, CoupledWorld]:
    """Construct a permutation from the witnessed rooted quotient.

    It changes parameters while preserving rooted A/B equivalence. In the
    phi=0 block only origin-orbit equivalence is certified, not full-space.
    """
    if depth < 4:
        raise ValueError("new coupling not visible before depth four")
    groups = equivalent_classes(all_couplings(depth))
    return {world: group[(index + 1) % len(group)]
            for group in groups for index, world in enumerate(group)}


def certify_rotation(depth: int = 4) -> RotationCertificate:
    from math import lcm
    groups = equivalent_classes(all_couplings(depth))
    rotated = rotate_within_class(depth)
    sizes = tuple(sorted(len(g) for g in groups))
    order = lcm(*sizes)
    for world in rotated:
        moved = world
        for _ in range(order):
            moved = rotated[moved]
        if moved != world:
            return RotationCertificate("OPEN",len(rotated),len(groups),sizes,order,False)
    return RotationCertificate("CLOSED_ROOTED_CONSTRUCTION_PERMUTATION",
        len(rotated), len(groups), sizes, order,
        all(rotated[w] != w for w in rotated))
