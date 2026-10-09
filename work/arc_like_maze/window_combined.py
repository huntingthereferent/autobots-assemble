"""Completion of the declared two-edit F3 A/B window, keeping the root marked.

Admit the previously withheld (pulse,balanced)=(1,1) coupling. 48 concrete
full-state laws form 14 full-state labeled conjugacy classes, but 16
ORIGIN-PRESERVING classes. The difference is witnessed, not guessed:
for support k=0,3 the pulse-only and simultaneous-edit worlds are
conjugate by a state map moving the origin, with explicit rooted word
collisions. For support k=1,2, Fix(ABABAB) proves inequivalence.

The shear coefficient is a genuine three-turn aligned coordinate chart.
All claims are scoped to this explicit 48-world finite-stem, zero-tail
two-predecessor family. No universal closure or native ARC solve.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .nondiagonal_transport import shear
from .window_branch import branch_rule
from .window_two import WindowProcess

ZERO = (0,) * 9
State = tuple[int, ...]


def combined_rule(support: int, coefficient: int,
                  pulse: int, balanced: int) -> tuple[int, ...]:
    if type(balanced) is not int or balanced not in (0, 1):
        raise ValueError("balanced edit must be zero or one")
    q = list(branch_rule(support, coefficient, pulse))
    q[3] = (q[3] + balanced) % 3  # q0(1,0)
    q[4] = (q[4] - balanced) % 3  # q0(1,1)
    return tuple(q)


@dataclass(frozen=True, order=True)
class CombinedWorld:
    support: int
    coefficient: int
    pulse: int
    balanced: int

    def __post_init__(self) -> None:
        combined_rule(self.support, self.coefficient,
                      self.pulse, self.balanced)

    def world(self) -> WindowProcess:
        return WindowProcess(1, (
            combined_rule(self.support, self.coefficient,
                          self.pulse, self.balanced),), (ZERO,))

    def step(self, state: State, action: str) -> State:
        return self.world().step(state, action)

    def inverse(self, state: State, action: str) -> State:
        return self.world().inverse(state, action)

    def apply(self, state: State, word: str) -> State:
        if any(letter not in "AB" for letter in word):
            raise ValueError("only A/B labeled words admitted")
        for letter in word:
            state = self.step(state, letter)
        return state

    def fixed_word(self, word: str, depth: int = 3) -> int:
        if type(depth) is not int or depth < 3:
            raise ValueError("depth must be >=3")
        return sum(self.apply(x, word) == x
                   for x in product(range(3), repeat=depth))

    def shear_next(self) -> "CombinedWorld":
        return CombinedWorld(self.support, (self.coefficient + 1) % 3,
                             self.pulse, self.balanced)

    def support_next(self) -> "CombinedWorld | None":
        if self.support == 3:
            return None
        return CombinedWorld(self.support + 1, self.coefficient,
                             self.pulse, self.balanced)

    def pulse_next(self) -> "CombinedWorld | None":
        if self.pulse == 1:
            return None
        return CombinedWorld(self.support, self.coefficient, 1, self.balanced)

    def balanced_next(self) -> "CombinedWorld | None":
        if self.balanced == 1:
            return None
        return CombinedWorld(self.support, self.coefficient, self.pulse, 1)


def family() -> tuple[CombinedWorld, ...]:
    return tuple(CombinedWorld(k, c, e, t)
                 for k, e, t, c in product(range(4), range(2),
                                            range(2), range(3)))


def fixed_word_formula(word: str, depth: int, k: int,
                       e: int, t: int) -> int:
    """Exact all-depth fixed-state counts; only the named words are admitted.

    Every action leaves coordinates >=3 unchanged, so the 27-state
    three-coordinate table multiplies by 3**(depth-3). The ABABAB rows
    were derived from the nine (x0,x1) states and their accumulated q0
    increments; an independent checker recomputes them from transitions.
    """
    if type(depth) is not int or depth < 3:
        raise ValueError("depth must be >=3")
    if type(k) is not int or k not in range(4):
        raise ValueError("support must be 0..3")
    if any(type(v) is not int or v not in (0, 1) for v in (e, t)):
        raise ValueError("pulse/balance must be 0/1")
    if word == "B":
        return (3-k) * 3 ** (depth-2)
    if word == "BBB":
        count3 = 18 if e else 27
    elif word == "AABAB":
        count3 = 6 if e else (3 if t else 9)
    elif word == "ABABAB":
        count3 = {
            (0, 0): (27, 18, 9, 0),
            (0, 1): (9, 18, 9, 9),
            (1, 0): (18, 18, 9, 0),
            (1, 1): (18, 9, 0, 0),
        }[(e, t)][k]
    else:
        raise ValueError("word has no proved closed-form count here")
    return count3 * 3 ** (depth-3)


def _fiber_shift(state: State, direction: int) -> State:
    """Non-diagonal, origin-moving conjugacy R for support 0 or 3.

    R:(u,v,z,tail) -> (u,v+2,z+f(v),tail), with f(1)=2 and
    f(0)=f(2)=0. For reverse direction use its exact inverse.
    """
    if type(direction) is not int or direction not in (1, -1):
        raise ValueError("direction must be 1 or -1")
    if len(state) < 3 or any(type(a) is not int or a not in range(3)
                            for a in state):
        raise ValueError("state must have >=3 F3 coordinates")
    u, v, z, *tail = state
    if direction == 1:
        return (u, (v+2)%3, (z+(2 if v == 1 else 0))%3, *tail)
    prev_v = (v+1)%3
    return (u, prev_v, (z-(2 if prev_v == 1 else 0))%3, *tail)


@dataclass(frozen=True)
class CombinedRelation:
    status: str
    source: CombinedWorld
    target: CombinedWorld
    kind: str | None
    shear_delta: int | None
    direction: int | None
    root_preserving: bool
    obstruction_word: str | None
    obstruction_depth: int | None
    source_count: int | None
    target_count: int | None

    def map_state(self, state: State) -> State:
        if self.kind is None or self.shear_delta is None:
            raise ValueError("inequivalent worlds have no proved alignment")
        if self.kind == "SHEAR":
            return shear(state, self.shear_delta)
        if self.kind == "FIBER_SHIFT":
            initial = shear(state, (-self.source.coefficient)%3)
            moved = _fiber_shift(initial, self.direction)
            return shear(moved, self.target.coefficient)
        raise AssertionError("unknown exact witness kind")


def classify_pair(source: CombinedWorld, target: CombinedWorld
                  ) -> CombinedRelation:
    """Explicit all-depth maps or word-fixed obstruction for every pair."""
    if source.support != target.support:
        word = "B"
    elif source.pulse != target.pulse:
        word = "BBB"
    elif source.balanced != target.balanced:
        if source.pulse == 0:
            word = "AABAB"
        elif source.support in (1, 2):
            word = "ABABAB"
        else:
            direction = 1 if source.balanced == 0 else -1
            return CombinedRelation(
                "ALL_DEPTH_FULL_STATE_NONROOT_CONJUGACY",
                source, target, "FIBER_SHIFT",
                None if direction is None else 0, direction,
                False, None, None, None, None,
            )
    else:
        return CombinedRelation(
            "ALL_DEPTH_ROOT_PRESERVING_CONJUGACY",
            source, target, "SHEAR",
            (target.coefficient-source.coefficient)%3,
            None, True, None, None, None, None,
        )
    first = fixed_word_formula(word, 3, source.support,
                               source.pulse, source.balanced)
    second = fixed_word_formula(word, 3, target.support,
                                target.pulse, target.balanced)
    if first == second:
        raise AssertionError(f"{word} does not separate the worlds")
    return CombinedRelation(
        "INEQUIVALENT_ACTION_WORD", source, target, None, None,
        None, False, word, 3, first, second,
    )


def rooted_conflict(source: CombinedWorld, target: CombinedWorld
                    ) -> tuple[str, str, State, State, State] | None:
    """Two positive A/B words collapse at source origin, split at target.

    Deterministic BFS from the marked root. Returns an exact witness
    rather than a claim that an arbitrary nonrooted map preserves it.
    """
    origin = (0, 0, 0)
    from collections import deque
    visited = {origin: (origin, "")}
    queue = deque([(origin, origin, "")])
    while queue:
        a, b, path = queue.popleft()
        for action in "AB":
            successor_a = source.step(a, action)
            successor_b = target.step(b, action)
            next_path = path + action
            if successor_a in visited:
                former_b, former_path = visited[successor_a]
                if former_b != successor_b:
                    return (former_path, next_path, successor_a,
                            former_b, successor_b)
            else:
                visited[successor_a] = (successor_b, next_path)
                queue.append((successor_a, successor_b, next_path))
    return None


@dataclass(frozen=True)
class CombinedCertificate:
    status: str
    concrete_worlds: int
    full_state_classes: int
    rooted_classes: int
    full_class_sizes: tuple[int, ...]
    rooted_class_sizes: tuple[int, ...]
    rooted_ordered_maps: int
    nonroot_ordered_maps: int
    B_obstructed: int
    BBB_obstructed: int
    AABAB_obstructed: int
    ABABAB_obstructed: int
    verified_root_collisions: int
    failure: str | None = None


def certify_combined() -> CombinedCertificate:
    """Complete finite pair classification using explicit all-depth proofs."""
    worlds = family()
    count = {"root": 0, "nonroot": 0, "B": 0, "BBB": 0,
             "AABAB": 0, "ABABAB": 0}
    rooted_witnesses = 0
    for source in worlds:
        for target in worlds:
            result = classify_pair(source, target)
            if result.kind is not None:
                name = "root" if result.root_preserving else "nonroot"
                count[name] += 1
                # Check a full 27-state transition square for each labeled action.
                for state in product(range(3), repeat=3):
                    image = result.map_state(state)
                    for action in "AB":
                        if (result.map_state(source.step(state, action))
                                != target.step(image, action)):
                            return CombinedCertificate(
                                "OPEN_ALIGNMENT",len(worlds),0,0,(),(),
                                count["root"],count["nonroot"],count["B"],
                                count["BBB"],count["AABAB"],count["ABABAB"],
                                rooted_witnesses,"state map did not commute")
                if not result.root_preserving:
                    conflict = rooted_conflict(source, target)
                    if conflict is None:
                        return CombinedCertificate(
                            "OPEN_ROOT_RELATION",len(worlds),0,0,(),(),
                            count["root"],count["nonroot"],count["B"],
                            count["BBB"],count["AABAB"],count["ABABAB"],
                            rooted_witnesses,"nonroot map lacks root counterexample")
                    rooted_witnesses += 1
            else:
                count[result.obstruction_word] += 1
    signature = {
        tuple(w.step(s, "B") for s in product(range(3), repeat=3))
        for w in worlds
    }
    expect = (len(worlds),len(signature),count["root"],count["nonroot"],
              count["B"],count["BBB"],count["AABAB"],count["ABABAB"],
              rooted_witnesses)
    required = (48,48,144,36,1728,288,72,36,36)
    good = expect == required
    return CombinedCertificate(
        "CLOSED_DECLARED_FULL_AND_ROOTED_QUOTIENTS" if good
        else "OPEN_COUNT_OR_CLASSIFICATION",
        len(worlds),14 if good else 0,16 if good else 0,
        (3,)*12+(6,)*2 if good else (),
        (3,)*16 if good else (),count["root"],count["nonroot"],
        count["B"],count["BBB"],count["AABAB"],count["ABABAB"],
        rooted_witnesses,
        None if good else f"observed={expect}; expected={required}",
    )
