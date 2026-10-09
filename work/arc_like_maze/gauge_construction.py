"""World-construction gauge loop and a genuinely new inverse-limit relation.

These operations make new A/B dynamics; they do NOT observe an existing ARC
world. The nonlinear gauge is a conjugacy, not a new A/B equivalence class.
The alternative coupling has a different B fixed-point invariant at depth 4.
All-depth algebra is recorded in the adjacent research report.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .inverse_limit import Phi, TowerPoint, check_phi
from .math import World

State = tuple[int, ...]


def _state(state: State) -> None:
    if len(state) < 3 or any(type(v) is not int or v not in (0, 1, 2) for v in state):
        raise ValueError("requires a state in F_3^d with d >= 3")


def gauge(state: State, coefficient: int) -> State:
    """G_c: add c*x_2^2 to x_3, leaving every other coordinate unchanged.

    G_c G_e = G_(c+e), G_c^-1 = G_(-c). Its coordinate formula is
    compatible with EVERY projection from depth d+1 onto depth d.
    """
    _state(state)
    if type(coefficient) is not int or coefficient not in range(3):
        raise ValueError("gauge coefficient must be in F_3")
    if len(state) < 4:
        return state
    values = list(state)
    values[3] = (state[3] + coefficient * state[2] ** 2) % 3
    return tuple(values)


@dataclass(frozen=True)
class GaugedWorld:
    """Construct an action system T_c = G_c T G_c^-1."""
    depth: int
    phi: Phi = (0, 1, 2)
    coefficient: int = 0

    def __post_init__(self) -> None:
        check_phi(self.phi)
        if self.depth < 3:
            raise ValueError("gauge construction requires depth >= 3")
        if type(self.coefficient) is not int or self.coefficient not in range(3):
            raise ValueError("coefficient outside F_3")

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def step(self, state: State, action: str) -> State:
        _state(state)
        if len(state) != self.depth:
            raise ValueError("state depth mismatch")
        if action not in ("A", "B"):
            raise ValueError("unknown A/B operation")
        old = gauge(state, (-self.coefficient) % 3)
        moved = World(self.depth, self.phi).step(old, action)
        return gauge(moved, self.coefficient)

    def apply(self, actions: str) -> State:
        current = self.origin
        for action in actions:
            current = self.step(current, action)
        return current

    def construct_next(self) -> "GaugedWorld":
        """Invert A/B construction by one gauge turn."""
        return GaugedWorld(self.depth, self.phi, (self.coefficient + 1) % 3)


def gauge_alignment(state: State, source: int, target: int) -> State:
    """Exact G_target G_source^-1 alignment for every depth."""
    return gauge(gauge(state, (-source) % 3), target)


@dataclass(frozen=True, eq=False)
class GaugedTower:
    """The same constructed gauge on every prefix of an inverse-limit point."""
    base: TowerPoint
    coefficient: int = 0

    def __post_init__(self) -> None:
        if type(self.coefficient) is not int or self.coefficient not in range(3):
            raise ValueError("invalid gauge coefficient")

    def prefix(self, depth: int) -> State:
        return gauge(self.base.prefix(depth), self.coefficient)

    def move(self, action: str) -> "GaugedTower":
        """Act by T_c, represented exactly as G_c T G_c^-1."""
        return GaugedTower(self.base.move(action), self.coefficient)

    def construct_next(self) -> "GaugedTower":
        # Same actual point represented in next world via G_(c+1)G_c^-1.
        return GaugedTower(self.base, (self.coefficient + 1) % 3)


@dataclass(frozen=True)
class SplitCouplingWorld:
    """Alter the constructed B relation at coordinate 3.

    Base B: x'_3 = x_3 + x_2.
    Split B: x'_3 = x_3 + x_2(x_2-1).
    All higher coordinate updates still use the OLD lower coordinate.
    This remains a triangular invertible homeomorphism, yet is not an
    exact projective conjugate of GaugedWorld under a rooted finite
    prefix alignment: the number of B fixed points at depth 4 differs.
    """
    depth: int
    phi: Phi = (0, 1, 2)

    def __post_init__(self) -> None:
        check_phi(self.phi)
        if self.depth < 3:
            raise ValueError("split construction requires depth >= 3")

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def step(self, state: State, action: str) -> State:
        _state(state)
        if len(state) != self.depth:
            raise ValueError("state depth mismatch")
        result = list(World(self.depth, self.phi).step(state, action))
        if action == "B" and self.depth >= 4:
            result[3] = (state[3] + state[2] * (state[2] - 1)) % 3
        return tuple(result)


def fixed_B(world: GaugedWorld | SplitCouplingWorld) -> int:
    """Whole finite-state count, not only the origin-reachable orbit."""
    count = 0
    for state in product(range(3), repeat=world.depth):
        if world.step(state, "B") == state:
            count += 1
    return count


@dataclass(frozen=True)
class BoundaryWitness:
    status: str
    three_turn_gauge_loop: bool
    three_concrete_B_rules: bool
    base_fixed_B: int
    split_fixed_B: int
    difference_depth: int | None


def construct_boundary(phi: Phi = (0, 1, 2)) -> BoundaryWitness:
    """Exact 4D finite witness; all-depth extension is a separate theorem."""
    check_phi(phi)
    worlds = [GaugedWorld(4, phi, coefficient) for coefficient in range(3)]
    # Test all 81 states, not selected origin moves.
    signatures = [tuple(world.step(state, "B") for state in product(range(3), repeat=4))
                  for world in worlds]
    differences = len(set(signatures)) == 3
    closure = worlds[0].construct_next().construct_next().construct_next() == worlds[0]
    base, split = fixed_B(worlds[0]), fixed_B(SplitCouplingWorld(4, phi))
    return BoundaryWitness(
        "NEW_RELATION_AT_DEPTH_FOUR" if closure and differences and base != split
        else "UNKNOWN_OR_NO_SEPARATION",
        closure, differences, base, split, 4 if base != split else None,
    )
