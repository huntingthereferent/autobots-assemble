"""Minimal two-predecessor local schema for non-diagonal F3 shears.

For coordinate i >= 2, B may add q_i(x[i-2], x[i-1]) rather than
forcing a one-input table p_i(x[i-1]). This is the smallest uniform
local widening that directly represents H_c B H_-c for H_c(x)_2 =
x_2 + c*x_1**2. It is a finite-depth representation of an all-depth
formula, not a universal definition of the language referent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product

from .marked_operator_system import MarkedObject
from .nondiagonal_transport import ShearedMarkedWorld, shear

State = tuple[int, ...]
Rule2 = tuple[int, ...]


def _check_state(state: State, depth: int) -> None:
    if (len(state) != depth
            or any(type(value) is not int or value not in (0, 1, 2)
                   for value in state)):
        raise ValueError("state must have the declared depth over F_3")


@dataclass(frozen=True)
class TwoPredecessorWorld:
    """Finite-depth world with B-coordinate increments q_i(x[i-2], x[i-1])."""

    base: MarkedObject
    coefficient: int
    depth: int
    rules: tuple[Rule2, ...] = field(init=False)

    def __post_init__(self) -> None:
        if type(self.coefficient) is not int or self.coefficient not in (0, 1, 2):
            raise ValueError("coefficient must be in F_3")
        if type(self.depth) is not int or self.depth < 3:
            raise ValueError("depth must be >= 3")

        process = self.base.process
        gain = self.base.gain
        c = self.coefficient
        rules = []
        for coordinate in range(2, self.depth):
            table = []
            for left, right in product(range(3), repeat=2):
                if coordinate == 2:
                    # (H_c B H_-c)(x)_2, derived exactly over F_3.
                    increment = (
                        process.rule(0)[right]
                        + c * (
                            (right + gain * (left + 1)) ** 2
                            - right ** 2
                        )
                    ) % 3
                elif coordinate == 3:
                    # H_-c changes the old x_2 to x_2 - c*x_1^2.
                    increment = process.rule(1)[
                        (right - c * left * left) % 3
                    ]
                else:
                    # Coordinates x_3 onward are not changed by H_c.
                    increment = process.rule(coordinate - 2)[right]
                table.append(increment)
            rules.append(tuple(table))
        object.__setattr__(self, "rules", tuple(rules))

    @property
    def origin(self) -> State:
        return (0,) * self.depth

    def increment(self, coordinate: int, left: int, right: int) -> int:
        if type(coordinate) is not int or not 2 <= coordinate < self.depth:
            raise ValueError("coordinate must be in [2, depth)")
        if left not in (0, 1, 2) or right not in (0, 1, 2):
            raise ValueError("rule inputs must be in F_3")
        return self.rules[coordinate - 2][3 * left + right]

    def step(self, state: State, action: str) -> State:
        _check_state(state, self.depth)
        result = list(state)
        if action == "A":
            result[0] = (state[0] + 1) % 3
        elif action == "B":
            result[1] = (state[1] + self.base.gain * (state[0] + 1)) % 3
            for coordinate in range(2, self.depth):
                result[coordinate] = (
                    state[coordinate]
                    + self.increment(
                        coordinate, state[coordinate - 2], state[coordinate - 1]
                    )
                ) % 3
        else:
            raise ValueError("only A and B are admitted")
        return tuple(result)

    def matches_conjugated_world(self, state: State, action: str) -> bool:
        """Compare this table implementation with the direct H_c T H_-c map."""
        direct = ShearedMarkedWorld(self.base, self.coefficient)
        return self.step(state, action) == direct.step(state, action)

    def is_native_one_input_rule(self, coordinate: int) -> bool:
        """True iff q_i(u,v) is independent of u and q_i(0,0)=0."""
        if type(coordinate) is not int or not 2 <= coordinate < self.depth:
            raise ValueError("coordinate must be in [2, depth)")
        table = self.rules[coordinate - 2]
        by_right = [table[right] for right in range(3)]
        for left in range(1, 3):
            if [table[3 * left + right] for right in range(3)] != by_right:
                return False
        return by_right[0] == 0


def verify_conjugacy(source: TwoPredecessorWorld,
                     target: TwoPredecessorWorld) -> bool:
    """Exhaust the complete finite state set for H_(target-source)."""
    if (source.depth != target.depth
            or source.base != target.base):
        raise ValueError("conjugacy requires equal depth and the same marked base")
    coefficient = (target.coefficient - source.coefficient) % 3
    for state in product(range(3), repeat=source.depth):
        mapped = shear(state, coefficient)
        for action in "AB":
            if shear(source.step(state, action), coefficient) != target.step(mapped, action):
                return False
    return True
