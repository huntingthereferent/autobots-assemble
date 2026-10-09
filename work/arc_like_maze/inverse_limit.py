"""Inverse-limit A/B dynamics and projectively compatible world alignment.

Mathematical construction, not native ARC gameplay. The complete inverse limit
is the product of F_3 coordinates; TowerPoint is an *oracle presentation* of
one such point, not an enumeration of uncountably many points.

All-depth statements follow from the displayed coordinate equations and do
not follow merely from running finite tests. A seed oracle must be pure and
stable: returning different values on repeat calls violates the input contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .math import World

Phi = tuple[int, int, int]
DigitOracle = Callable[[int], int]
State = tuple[int, ...]

OPERATIONS = frozenset(("A", "B", "a", "b"))


def check_phi(phi: Phi) -> None:
    if len(phi) != 3 or phi[0] != 0 or any(type(v) is not int or v not in range(3) for v in phi):
        raise ValueError("the admitted tower requires phi=(0,a,b) over F_3")


def prefix_inverse(state: State, phi: Phi, operation: str) -> State:
    """Inverse of a finite A or B step, by recursive triangular solving."""
    check_phi(phi)
    if len(state) < 3 or any(type(v) is not int or v not in range(3) for v in state):
        raise ValueError("finite state must be at least depth three over F_3")
    old = list(state)
    if operation == "a":
        old[0] = (state[0] - 1) % 3
    elif operation == "b":
        old[1] = (state[1] - state[0] - 1) % 3
        old[2] = (state[2] - phi[old[1]]) % 3
        for i in range(3, len(state)):
            old[i] = (state[i] - old[i - 1]) % 3
    else:
        raise ValueError("only a and b denote inverse steps")
    return tuple(old)


def step_prefix(state: State, phi: Phi, operation: str) -> State:
    """Same action on every finite prefix; inverse labels use lower case."""
    check_phi(phi)
    if operation in ("A", "B"):
        return World(len(state), phi).step(state, operation)
    return prefix_inverse(state, phi, operation)


@dataclass(frozen=True, eq=False)
class TowerPoint:
    """Lazy coherent prefixes of one point in the infinite coordinate product.

    Equality of arbitrary infinite oracles is undecidable; do not silently
    compare TowerPoint objects by identity or a bounded sample.
    """
    phi: Phi
    seed_digit: DigitOracle
    operations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_phi(self.phi)
        if not callable(self.seed_digit):
            raise ValueError("seed needs a stable digit oracle")
        if any(action not in OPERATIONS for action in self.operations):
            raise ValueError("invalid A/B action")

    @classmethod
    def zeros(cls, phi: Phi = (0, 1, 2)) -> "TowerPoint":
        return cls(phi, lambda _index: 0)

    @classmethod
    def finite_support(cls, coordinates: State, phi: Phi = (0, 1, 2)) -> "TowerPoint":
        check_phi(phi)
        if any(type(v) is not int or v not in range(3) for v in coordinates):
            raise ValueError("seed coordinates must lie in F_3")
        values = tuple(coordinates)
        return cls(phi, lambda index: values[index] if index < len(values) else 0)

    def prefix(self, depth: int) -> State:
        if depth < 3:
            raise ValueError("inverse-limit prefixes begin at depth three")
        digits = []
        for index in range(depth):
            value = self.seed_digit(index)
            if type(value) is not int or value not in range(3):
                raise ValueError(f"seed digit {index} is outside F_3")
            digits.append(value)
        current = tuple(digits)
        for action in self.operations:
            current = step_prefix(current, self.phi, action)
        return current

    def move(self, operation: str) -> "TowerPoint":
        if operation not in OPERATIONS:
            raise ValueError("unrecognized operation")
        return TowerPoint(self.phi, self.seed_digit, self.operations + (operation,))

    def agree_through(self, other: "TowerPoint", depth: int) -> bool:
        """Only a finite observation, NEVER proof of infinite equality."""
        return self.phi == other.phi and self.prefix(depth) == other.prefix(depth)


def alignment_scalar(source: Phi, target: Phi) -> int | None:
    """Exact projective rooted A/B alignments of the admitted phi towers.

    Necessity: every projectively compatible alignment restricts at depth 3,
    where the full finite classification admits only phi and 2*phi.
    Sufficiency: for scalar s=1 or 2, scale every coordinate i >= 2.
    The A/B equations and forgetful projections commute for ALL depths.
    """
    check_phi(source)
    check_phi(target)
    for scalar in (1, 2):
        if tuple(scalar * c % 3 for c in source) == target:
            return scalar
    return None


def tower_class(phi: Phi) -> tuple[int, int]:
    """Canonical class of a complete tower under coherent rooted A/B maps."""
    check_phi(phi)
    a, b = phi[1:]
    return min((a, b), ((2 * a) % 3, (2 * b) % 3))


def align_point(point: TowerPoint, target: Phi) -> TowerPoint:
    """An exact compatible alignment of all finite prefixes.

    Changing to a different A/B class has no admitted state alignment;
    world-parameter construction between classes is a separate operation.
    """
    scalar = alignment_scalar(point.phi, target)
    if scalar is None:
        raise ValueError("no projective A/B alignment exists between these classes")
    def aligned_seed(index: int) -> int:
        value = point.seed_digit(index)
        return value if index < 2 else (scalar * value) % 3
    return TowerPoint(target, aligned_seed, point.operations)


@dataclass(frozen=True)
class FiniteTowerAudit:
    status: str
    phi: Phi
    checked_depths: tuple[int, ...]
    commuting_edges: int
    false_closure_depth: int | None
    break_depth: int | None
    failure: str | None = None


def audit_prefixes(
    phi: Phi = (0, 1, 2),
    *,
    deepest: int = 8,
    word: str = "BBB",
) -> FiniteTowerAudit:
    """Bounded witness for the theorem, not an exhaustive infinite proof.

    The symbolic all-depth proof is in the docstring and research record.
    """
    check_phi(phi)
    if deepest < 4 or any(c not in "AB" for c in word):
        return FiniteTowerAudit("UNKNOWN", phi, (), 0, None, None,
                                "need depth >=4 and an A/B word")
    start = TowerPoint.zeros(phi)
    moved = start
    for operation in word:
        moved = moved.move(operation)
    edges = 0
    for depth in range(3, deepest):
        for prefix in (start.prefix(depth + 1), moved.prefix(depth + 1)):
            for operation in "AB":
                higher = step_prefix(prefix, phi, operation)
                lower = step_prefix(prefix[:-1], phi, operation)
                edges += 1
                if higher[:-1] != lower:
                    return FiniteTowerAudit("OPEN", phi, tuple(range(3, depth + 2)),
                                           edges, None, None,
                                           f"projection square breaks at depth {depth}")
    equal_depths = [d for d in range(3, deepest + 1)
                    if start.prefix(d) == moved.prefix(d)]
    first_break = next((d for d in range(3, deepest + 1)
                        if start.prefix(d) != moved.prefix(d)), None)
    false_closure = (max(d for d in equal_depths if d < first_break)
                     if first_break is not None and any(d < first_break for d in equal_depths)
                     else None)
    return FiniteTowerAudit("FINITE_PREFIX_VERIFIED", phi,
                            tuple(range(3, deepest + 1)), edges,
                            false_closure, first_break)
