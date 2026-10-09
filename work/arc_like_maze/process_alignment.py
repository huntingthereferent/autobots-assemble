"""Coinductive, all-depth alignment of eventually periodic A/B constructions.

The object being aligned is now an entire infinite sequence of coupling RULES,
not just one finite constructed world. Every rule maps F_3 to F_3 and fixes 0.

Scope of this proof: rooted, origin-preserving DIAGONAL coordinate changes
x_0 -> x_0, x_1 -> x_1, x_(i+2) -> s_i*x_(i+2), s_i in {1,2}.
Failure of this restricted alignment is NOT proof that no more general
non-diagonal A/B conjugacy exists. A finite certificate is exact for
eventually-periodic streams only; arbitrary rule oracles remain UNKNOWN.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import lcm

Rule = tuple[int, int, int]
State = tuple[int, ...]
IDENTITY: Rule = (0, 1, 2)
NEGATIVE: Rule = (0, 2, 1)
NONLINEAR: Rule = (0, 1, 1)
ZERO: Rule = (0, 0, 0)


def _check_rule(rule: Rule) -> None:
    if (len(rule) != 3 or rule[0] != 0 or
            any(type(v) is not int or v not in (0, 1, 2) for v in rule)):
        raise ValueError("each coupling must be a table (0,a,b) over F_3")


@dataclass(frozen=True)
class PeriodicProcess:
    """Finite prefix followed by a nonempty repeating tail of coupling rules."""
    stem: tuple[Rule, ...]
    period: tuple[Rule, ...]

    def __post_init__(self) -> None:
        if not self.period:
            raise ValueError("a repeating process requires a nonempty period")
        for rule in self.stem + self.period:
            _check_rule(rule)

    @classmethod
    def repeat(cls, *rules: Rule) -> "PeriodicProcess":
        return cls((), tuple(rules))

    def rule(self, index: int) -> Rule:
        if type(index) is not int or index < 0:
            raise ValueError("nonnegative coupling index required")
        if index < len(self.stem):
            return self.stem[index]
        return self.period[(index - len(self.stem)) % len(self.period)]

    def shift(self, turns: int) -> "PeriodicProcess":
        """A new construction blueprint beginning at a later coupling turn.

        This re-roots a process template; it is not the projection between
        existing world states and is not an ARC player action.
        """
        if type(turns) is not int or turns < 0:
            raise ValueError("shift must be nonnegative")
        if turns < len(self.stem):
            return PeriodicProcess(self.stem[turns:], self.period)
        phase = (turns - len(self.stem)) % len(self.period)
        return PeriodicProcess((), self.period[phase:] + self.period[:phase])

    def step(self, state: State, action: str) -> State:
        if len(state) < 3 or any(type(x) is not int or x not in (0, 1, 2) for x in state):
            raise ValueError("state requires at least three F_3 coordinates")
        result = list(state)
        if action == "A":
            result[0] = (state[0] + 1) % 3
        elif action == "B":
            result[1] = (state[1] + state[0] + 1) % 3
            for i in range(2, len(state)):
                result[i] = (state[i] + self.rule(i - 2)[state[i - 1]]) % 3
        else:
            raise ValueError("only A/B")
        return tuple(result)


def next_scales(source: Rule, target: Rule, previous: int) -> tuple[int, ...]:
    """Solve t(previous*u) = next*s(u) for all u in F_3."""
    _check_rule(source)
    _check_rule(target)
    if previous not in (1, 2):
        raise ValueError("previous scale must be invertible")
    return tuple(s for s in (1, 2)
                 if all(target[previous*u % 3] == s*source[u] % 3 for u in range(3)))


@dataclass(frozen=True)
class CoinductiveAlignment:
    """Ultimately periodic scalar sequence, with a finite exact lasso witness."""
    status: str
    head: tuple[int, ...] = ()
    period: tuple[int, ...] = ()
    first_impossible_depth: int | None = None
    checked_phase_states: int = 0

    def scale(self, index: int) -> int:
        if self.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT":
            raise ValueError("an OPEN result cannot be used as an alignment")
        if type(index) is not int or index < 0:
            raise ValueError("coordinate index must be nonnegative")
        if index < len(self.head):
            return self.head[index]
        return self.period[(index - len(self.head)) % len(self.period)]

    def map_state(self, state: State) -> State:
        if self.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT":
            raise ValueError("no construction map was certified")
        if len(state) < 3 or any(type(x) is not int or x not in (0, 1, 2) for x in state):
            raise ValueError("invalid state")
        return state[:2] + tuple(self.scale(i)*x % 3
                                 for i, x in enumerate(state[2:]))


def find_process_alignment(
    source: PeriodicProcess,
    target: PeriodicProcess,
) -> CoinductiveAlignment:
    """Decide existence of a coherent diagonal conjugacy for ALL depths.

    A finite automaton has states (periodic phase, previous scalar).
    Greatest-fixed-point elimination retains precisely states admitting
    an infinite path. A finite stem is propagated to that safe set.
    A repeated automaton state yields an explicit ultimately periodic
    scale sequence and therefore a mathematically exact infinite witness.
    If no such path exists, a finite incompatible coordinate is returned.
    """
    stem_end = max(len(source.stem), len(target.stem))
    period = lcm(len(source.period), len(target.period))
    nodes = {(phase, prev) for phase in range(period) for prev in (1, 2)}

    def outgoing(node: tuple[int, int]) -> tuple[tuple[tuple[int, int], int], ...]:
        phase, prev = node
        index = stem_end + phase
        nxt_phase = (phase + 1) % period
        return tuple(((nxt_phase, s), s)
                     for s in next_scales(source.rule(index), target.rule(index), prev))

    safe = set(nodes)
    while True:
        next_safe = {state for state in safe if any(
            successor in safe for successor, _ in outgoing(state))}
        if next_safe == safe:
            break
        safe = next_safe

    paths: dict[int, tuple[int, ...]] = {1: ()}  # s_(minus one) = 1
    for i in range(stem_end):
        expanded: dict[int, tuple[int, ...]] = {}
        for prev, witness in sorted(paths.items()):
            for s in next_scales(source.rule(i), target.rule(i), prev):
                expanded.setdefault(s, witness + (s,))
        paths = expanded
        if not paths:
            return CoinductiveAlignment("OPEN_DIAGONAL_ALIGNMENT",
                                         first_impossible_depth=i + 3,
                                         checked_phase_states=len(nodes))

    survivors = [(prev, witness) for prev, witness in sorted(paths.items())
                 if (0, prev) in safe]
    if not survivors:
        # No infinite path. Finite branching implies a bounded concrete
        # counterexample. Compute first depth where all partial maps die.
        reachable = {1}
        for i in range(stem_end + 2*len(nodes) + 2):
            new = {s for prev in reachable
                   for s in next_scales(source.rule(i), target.rule(i), prev)}
            if not new:
                return CoinductiveAlignment(
                    "OPEN_DIAGONAL_ALIGNMENT", first_impossible_depth=i + 3,
                    checked_phase_states=len(nodes))
            reachable = new
        raise AssertionError("finite-state coinduction and finite obstruction disagree")

    initial_prev, head = survivors[0]
    now = (0, initial_prev)
    seen: dict[tuple[int, int], int] = {}
    tail: list[int] = []
    while now not in seen:
        seen[now] = len(tail)
        successor, scalar = next(
            (successor, scalar) for successor, scalar in outgoing(now)
            if successor in safe)
        tail.append(scalar)
        now = successor
    entry = seen[now]
    result = CoinductiveAlignment(
        "COINDUCTIVE_DIAGONAL_ALIGNMENT",
        head + tuple(tail[:entry]), tuple(tail[entry:]),
        checked_phase_states=len(nodes))
    if not verify_lasso(source, target, result):
        raise AssertionError("constructed coinductive witness did not verify")
    return result


def verify_lasso(
    source: PeriodicProcess, target: PeriodicProcess,
    cert: CoinductiveAlignment,
) -> bool:
    """Exact check: a full joint period after all finite transients.

    Rule phases, gauge phases, and the PREVIOUS gauge value recur at the
    same time. Once their full joint state repeats, induction validates
    the scaling relation at every later dimension.
    """
    if cert.status != "COINDUCTIVE_DIAGONAL_ALIGNMENT" or not cert.period:
        return False
    start = max(len(source.stem), len(target.stem), len(cert.head) + 1)
    joint = lcm(len(source.period), len(target.period), len(cert.period))
    for index in range(start + joint):
        prev = 1 if index == 0 else cert.scale(index - 1)
        if cert.scale(index) not in next_scales(
                source.rule(index), target.rule(index), prev):
            return False
    # Both (phase, previous gauge) at the repetition boundary are the same.
    return (source.rule(start) == source.rule(start + joint)
            and target.rule(start) == target.rule(start + joint)
            and cert.scale(start - 1) == cert.scale(start + joint - 1)
            and cert.scale(start) == cert.scale(start + joint))


def compare_shift(
    construction: PeriodicProcess, turns: int = 1,
) -> CoinductiveAlignment:
    """Compare one process template with its next construction turn."""
    return find_process_alignment(construction, construction.shift(turns))
