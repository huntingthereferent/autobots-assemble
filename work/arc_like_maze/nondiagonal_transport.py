"""Non-diagonal coordinate transport of *marked* A/B process worlds.

A lower-triangular, nonlinear coordinate shear is an exact all-depth
conjugacy, but its conjugated B action lies outside the existing
one-variable-coupling Process representation. This distinction is crucial:
schema nonclosure is NOT a new A/B equivalence class.

Admitted operations: F_3 coordinate shear at coordinate two, existing
coinductively certified MarkedArrow scalings, root-aware forward shifts,
and separately verified diagonal boundary gauges. These are constructed
mathematical systems, not ARC gameplay.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .root_transport import Process, MarkedWorld, marked_map, Witness
from .marked_operator_system import (
    MarkedObject, MarkedArrow, BoundaryGauge, compose_arrows,
    invert_arrow, shift_arrow, transform_arrow, same_arrow,
    identical_streams,
)

State = tuple[int, ...]


def shear(state: State, coefficient: int) -> State:
    """H_c(x)_2 = x_2 + c*x_1^2, all other coordinates unchanged.

    H_c H_e = H_(c+e), H_c^-1=H_-c. All projections commute from
    every higher-dimensional world onto its depth>=3 prefixes.
    The zero state is fixed. Coefficient belongs to F_3.
    """
    if (len(state) < 3 or any(type(x) is not int or x not in (0, 1, 2)
                              for x in state)):
        raise ValueError("a shear requires at least three F_3 coordinates")
    if type(coefficient) is not int or coefficient not in (0, 1, 2):
        raise ValueError("coefficient must be in F_3")
    values = list(state)
    values[2] = (state[2] + coefficient * state[1] * state[1]) % 3
    return tuple(values)


def _native_inverse(world: MarkedWorld, state: State, action: str) -> State:
    """Inverse of the triangular marked A/B law on the complete state set."""
    if len(state) < 3 or any(type(v) is not int or v not in (0, 1, 2) for v in state):
        raise ValueError("invalid F_3 state")
    old = list(state)
    if action == "A":
        old[0] = (state[0] - 1) % 3
    elif action == "B":
        old[1] = (state[1] - world.gain * (state[0] + 1)) % 3
        for coordinate in range(2, len(state)):
            old[coordinate] = (
                state[coordinate] - world.process.rule(coordinate - 2)[old[coordinate - 1]]
            ) % 3
    else:
        raise ValueError("only A and B are admitted")
    return tuple(old)


@dataclass(frozen=True)
class ShearedMarkedWorld:
    """Constructed T_c=H_c T H_-c, not a native Process rule-table world."""
    base: MarkedObject
    coefficient: int

    def __post_init__(self) -> None:
        if type(self.coefficient) is not int or self.coefficient not in (0, 1, 2):
            raise ValueError("invalid shear coefficient")

    def step(self, state: State, action: str) -> State:
        old = shear(state, (-self.coefficient) % 3)
        return shear(self.base.world().step(old, action), self.coefficient)

    def inverse(self, state: State, action: str) -> State:
        old = shear(state, (-self.coefficient) % 3)
        return shear(_native_inverse(self.base.world(), old, action), self.coefficient)

    def origin(self, depth: int) -> State:
        if type(depth) is not int or depth < 3:
            raise ValueError("depth must be >=3")
        return (0,) * depth

    def construct_next(self) -> "ShearedMarkedWorld":
        return ShearedMarkedWorld(self.base, (self.coefficient + 1) % 3)


@dataclass(frozen=True)
class ShearedMarkedArrow:
    """Transport a verified diagonal marked arrow through two separate shears.

    The actual state map is H_target ○ M_witness ○ H_source^-1.
    Its stored witness remains the ORIGINAL full coinductive lasso;
    a scalar Witness alone is not the correct type for the final map.
    """
    base: MarkedArrow
    source_coefficient: int
    target_coefficient: int

    def __post_init__(self) -> None:
        for coefficient in (self.source_coefficient, self.target_coefficient):
            if type(coefficient) is not int or coefficient not in (0, 1, 2):
                raise ValueError("invalid shear coefficient")

    @property
    def source(self) -> ShearedMarkedWorld:
        return ShearedMarkedWorld(self.base.source, self.source_coefficient)

    @property
    def target(self) -> ShearedMarkedWorld:
        return ShearedMarkedWorld(self.base.target, self.target_coefficient)

    def map_state(self, state: State) -> State:
        unsheared = shear(state, (-self.source_coefficient) % 3)
        aligned = marked_map(unsheared, self.base.witness)
        return shear(aligned, self.target_coefficient)

    def verify_depth(self, depth: int) -> bool:
        """Exhaust the full state set, not only origin-reachable states."""
        if type(depth) is not int or depth < 3:
            raise ValueError("depth must be >=3")
        for state in product(range(3), repeat=depth):
            mapped = self.map_state(state)
            for operation in ("A", "B"):
                if (self.map_state(self.source.step(state, operation))
                        != self.target.step(mapped, operation)):
                    return False
        return True

    def inverse(self) -> "ShearedMarkedArrow":
        return ShearedMarkedArrow(invert_arrow(self.base),
                                  self.target_coefficient, self.source_coefficient)

    def compose(self, after: "ShearedMarkedArrow") -> "ShearedMarkedArrow":
        """Composition only when the complete sheared middle world agrees."""
        if (self.target_coefficient != after.source_coefficient
                or self.base.target.gain != after.base.source.gain
                or not identical_streams(self.base.target.process,
                                         after.base.source.process)):
            raise ValueError("marked sheared middle objects do not agree")
        return ShearedMarkedArrow(compose_arrows(self.base, after.base),
                                  self.source_coefficient, after.target_coefficient)

    def shift(self, turns: int, *, new_source_gain: int = 1) -> "ShearedMarkedArrow":
        """Re-root both processes and shears at the new marked boundary.

        The shear is defined relative to LOCAL x1 and x2. This is a
        transported mathematical representation, not a claim that a
        deleted global prefix can be reconstructed.
        """
        return ShearedMarkedArrow(
            shift_arrow(self.base, turns, new_source_gain=new_source_gain),
            self.source_coefficient, self.target_coefficient)

    def gauge(self, source_gauge: BoundaryGauge,
              target_gauge: BoundaryGauge) -> "ShearedMarkedArrow":
        """Conjugate the existing diagonal gauges into the sheared frame."""
        return ShearedMarkedArrow(
            transform_arrow(self.base, source_gauge, target_gauge),
            self.source_coefficient, self.target_coefficient)


def same_sheared_arrow(left: ShearedMarkedArrow,
                       right: ShearedMarkedArrow) -> bool:
    return (left.source_coefficient == right.source_coefficient
            and left.target_coefficient == right.target_coefficient
            and same_arrow(left.base, right.base))


def shear_interchange(arrow: ShearedMarkedArrow,
                      source_gauge: BoundaryGauge,
                      target_gauge: BoundaryGauge,
                      turns: int) -> bool:
    """Literal witness plus local coordinate chart commute with marked shift."""
    shifted_source = source_gauge.shifted(turns)
    shifted_target = target_gauge.shifted(turns)
    left = arrow.shift(turns).gauge(shifted_source, shifted_target)
    right = arrow.gauge(source_gauge, target_gauge).shift(
        turns, new_source_gain=shifted_source.incoming)
    return same_sheared_arrow(left, right)


@dataclass(frozen=True)
class ShearCertificate:
    status: str
    distinct_depth_three_rules: int
    group_order: int
    native_representation_breaks: int
    alignment_edges_checked: int
    failure: str | None = None


def certify_shear() -> ShearCertificate:
    """Finite evidence of distinct laws; algebra certifies any-depth conjugacy."""
    from .root_transport import ZERO
    source = MarkedObject(Process.repeat(ZERO), 1)
    worlds = [ShearedMarkedWorld(source, c) for c in (0, 1, 2)]
    states = tuple(product(range(3), repeat=3))
    signatures = {tuple(w.step(s, "B") for s in states) for w in worlds}
    edges = 0
    for state in states:
        for action in ("A", "B"):
            for a in (0, 1, 2):
                for b in (0, 1, 2):
                    transformed = shear(state, (b - a) % 3)
                    left = shear(worlds[a].step(state, action), (b-a) % 3)
                    right = worlds[b].step(transformed, action)
                    edges += 1
                    if left != right:
                        return ShearCertificate("OPEN_CONJUGACY",len(signatures),3,0,edges,
                                                f"noncommuting {action} at {state}")
    # Every admissible native marked process has B(origin)_2 == rule(0)[0] == 0.
    native_breaks = sum(w.step((0, 0, 0), "B")[2] != 0 for w in worlds)
    order = 0
    w = worlds[0]
    while True:
        order += 1
        w = w.construct_next()
        if w == worlds[0]:
            break
        if order > 3:
            return ShearCertificate("OPEN_ORDER",len(signatures),order,native_breaks,edges)
    return ShearCertificate(
        "CLOSED_SHEAR_CONJUGACY_OUTSIDE_NATIVE_PROCESS_SCHEMA"
        if len(signatures) == 3 and native_breaks == 2 and order == 3
        else "OPEN_MISSING_WITNESS",
        len(signatures),order,native_breaks,edges,
    )
