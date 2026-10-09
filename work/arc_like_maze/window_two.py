"""A self-contained, finite-representable two-predecessor A/B construction.

Generalize native B_i increments from p_i(x_(i-1)) to
q_i(x_(i-2), x_(i-1)) for i >= 2. This is enough to compile the
non-diagonal shear H_c(x)_2 = x_2+c*x_1^2 exactly.

All rules live in F_3. Each window q_i is a 9-entry table, with
index 3*earlier+later. Stems and nonempty repeating tails describe
the entire all-depth process: no finite exploration is promoted to
unrestricted closure. A/B are invertible triangular maps at every depth.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .marked_operator_system import MarkedObject
from .process_alignment import PeriodicProcess as Process

Window = tuple[int, ...]
State = tuple[int, ...]


def _window(values: Window) -> None:
    if len(values) != 9 or any(type(v) is not int or v not in (0, 1, 2) for v in values):
        raise ValueError("window rule must contain exactly nine F_3 values")


def _state(state: State) -> None:
    if len(state) < 3 or any(type(v) is not int or v not in (0, 1, 2) for v in state):
        raise ValueError("state must have at least three F_3 coordinates")


def lift_native(rule: tuple[int, int, int]) -> Window:
    if len(rule) != 3 or rule[0] != 0 or any(type(v) is not int or v not in (0, 1, 2)
                                               for v in rule):
        raise ValueError("a native rule must be (0,a,b)")
    return tuple(rule[right] for _left in range(3) for right in range(3))


@dataclass(frozen=True)
class WindowProcess:
    """Marked two-coordinate coupling process with an eventually periodic tail.

    B_1 adds gain*(x_0+1); B_(i+2) adds q_i(x_i,x_(i+1)).
    Every q_i depends only on PRE-MOVE coordinates.
    """
    gain: int
    stem: tuple[Window, ...]
    period: tuple[Window, ...]

    def __post_init__(self) -> None:
        if type(self.gain) is not int or self.gain not in (1, 2):
            raise ValueError("root gain must be an F_3 unit")
        if not self.period:
            raise ValueError("an infinite construction needs a nonempty period")
        for table in self.stem + self.period:
            _window(table)

    def rule(self, index: int) -> Window:
        if type(index) is not int or index < 0:
            raise ValueError("rule index must be nonnegative")
        if index < len(self.stem):
            return self.stem[index]
        return self.period[(index - len(self.stem)) % len(self.period)]

    def step(self, state: State, action: str) -> State:
        _state(state)
        result = list(state)
        if action == "A":
            result[0] = (state[0] + 1) % 3
        elif action == "B":
            result[1] = (state[1] + self.gain * (state[0] + 1)) % 3
            for coordinate in range(2, len(state)):
                left, right = state[coordinate - 2:coordinate]
                result[coordinate] = (
                    state[coordinate] + self.rule(coordinate - 2)[3 * left + right]
                ) % 3
        else:
            raise ValueError("action must be A or B")
        return tuple(result)

    def inverse(self, state: State, action: str) -> State:
        """Recover the unique predecessor from low to high coordinates."""
        _state(state)
        old = list(state)
        if action == "A":
            old[0] = (state[0] - 1) % 3
        elif action == "B":
            old[1] = (state[1] - self.gain * (state[0] + 1)) % 3
            for coordinate in range(2, len(state)):
                left, right = old[coordinate - 2:coordinate]
                old[coordinate] = (
                    state[coordinate] - self.rule(coordinate - 2)[3 * left + right]
                ) % 3
        else:
            raise ValueError("action must be A or B")
        return tuple(old)

    def native(self) -> MarkedObject | None:
        """Decode iff every window ignores its earlier input and fixes zero.

        Exact for the whole eventually periodic stream, not a finite prefix.
        """
        def decode(table: Window) -> tuple[int, int, int] | None:
            if table[:3] != table[3:6] or table[:3] != table[6:9] or table[0] != 0:
                return None
            return tuple(table[:3])

        stem = tuple(decode(table) for table in self.stem)
        period = tuple(decode(table) for table in self.period)
        if any(table is None for table in stem + period):
            return None
        return MarkedObject(Process(stem, period), self.gain)  # type: ignore[arg-type]

    def edit(self, index: int, earlier: int, later: int, delta: int) -> "WindowProcess":
        """Independent one-table-entry construction; keep all later rules."""
        if (type(index) is not int or index < 0 or
                any(type(v) is not int or v not in (0, 1, 2)
                    for v in (earlier, later, delta))):
            raise ValueError("edit requires nonnegative index and F_3 values")
        length = max(len(self.stem), index + 1)
        head = [self.rule(i) for i in range(length)]
        changed = list(head[index])
        pos = 3 * earlier + later
        changed[pos] = (changed[pos] + delta) % 3
        head[index] = tuple(changed)
        # Phase-correct the tail when a former periodic rule enters the stem.
        new_period = tuple(self.rule(length + j) for j in range(len(self.period)))
        return WindowProcess(self.gain, tuple(head), new_period)


def compile_native(obj: MarkedObject) -> WindowProcess:
    """Embed the old one-input coupling schema without losing the root mark."""
    p = obj.process
    return WindowProcess(obj.gain,
                         tuple(lift_native(rule) for rule in p.stem),
                         tuple(lift_native(rule) for rule in p.period))


def compile_shear(obj: MarkedObject, coefficient: int) -> WindowProcess:
    """Exact independent table compilation of H_c B H_-c.

    For i=0: x2's increment depends on x0 and x1.
    For i=1: x3's increment depends on x1 and x2.
    For i>=2: original p_i(x_(i+1)), independent of x_i.

    The c-dependent rule is derivable algebraically, with no sampling.
    """
    if type(coefficient) is not int or coefficient not in (0, 1, 2):
        raise ValueError("shear coefficient must be in F_3")
    p, gain = obj.process, obj.gain

    def table(index: int) -> Window:
        rule = p.rule(index)
        if index == 0:
            return tuple((
                rule[right] +
                coefficient * (
                    (right + gain * (left + 1)) ** 2 - right ** 2
                )
            ) % 3 for left in range(3) for right in range(3))
        if index == 1:
            return tuple(rule[(right - coefficient * left * left) % 3]
                         for left in range(3) for right in range(3))
        return lift_native(rule)

    transient = max(2, len(p.stem))
    period = len(p.period)
    return WindowProcess(
        gain,
        tuple(table(index) for index in range(transient)),
        tuple(table(index) for index in range(transient, transient + period)),
    )


def all_state_fixed_B(world: WindowProcess, depth: int) -> int:
    """Exhaustive B fixed-point invariant on FULL F_3^depth."""
    if type(depth) is not int or depth < 3:
        raise ValueError("depth must be >=3")
    return sum(world.step(state, "B") == state
               for state in product(range(3), repeat=depth))


@dataclass(frozen=True)
class WindowCertificate:
    status: str
    depth: int
    original_fixed: int
    independent_fixed: int
    compiled_same_steps: int
    checked_projection_edges: int
    reason: str


def certify_window_construction(depth: int = 5) -> WindowCertificate:
    """A bounded independently testable counterexample, not global closure."""
    if type(depth) is not int or depth < 3:
        return WindowCertificate("UNKNOWN", depth, 0, 0, 0, 0,
                                 "a full third coordinate is required")
    obj = MarkedObject(Process.repeat((0, 0, 0)), 1)
    baseline = compile_native(obj)
    independent = baseline.edit(0, 2, 0, 1)
    original_fixed = all_state_fixed_B(baseline, 3)
    changed_fixed = all_state_fixed_B(independent, 3)
    steps = 0
    edges = 0
    for state in product(range(3), repeat=depth):
        for action in ("A", "B"):
            steps += 1
            if baseline.step(state, action) != obj.world().step(state, action):
                return WindowCertificate("OPEN_COMPILATION", depth, original_fixed,
                                         changed_fixed, steps, edges,
                                         "native embedding changed a transition")
            if depth > 3:
                edges += 1
                if (independent.step(state, action)[:-1] !=
                        independent.step(state[:-1], action)):
                    return WindowCertificate("OPEN_PROJECTION", depth, original_fixed,
                                             changed_fixed, steps, edges,
                                             "independent coupling broke projection")
    return WindowCertificate(
        "CLOSED_WINDOW_LAWS_WITH_DISTINCT_B_FIXED_INVARIANT"
        if (original_fixed, changed_fixed) == (9, 6) else "OPEN_NO_SEPARATION",
        depth, original_fixed, changed_fixed, steps, edges,
        "full-state B fixed-point cardinality blocks any A/B conjugacy"
    )
