"""A five-letter A/B word resolves a collision in two shorter invariants.

A finite, justified extension of the previous 24 worlds. At each support k,
the three independent relational branches are:
  - ordinary (pulse=0, balanced=0),
  - independently balanced row-1 edit (pulse=0, balanced=1),
  - previous row-0 pulse (pulse=1, balanced=0).
Each is constructed in three H_c shear charts.

The balanced edit adds +1 at q0(1,0) and -1 at q0(1,1). It preserves
Fix(B) and Fix(BBB), yet changes Fix(AABAB) from 9 to 3 at depth three.
For pulse=1 the same five-word count is 6 (the row-1 edit is not
admitted on that branch). Thus 36 laws have exactly 12 full-state A/B
conjugacy classes, with a concrete all-depth shear witness inside each.

This is not a classification of arbitrary F3 window rules or ARC play.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .nondiagonal_transport import shear
from .window_branch import BranchedWindow, branch_rule
from .window_two import WindowProcess

ZERO_WINDOW = (0,) * 9
_ALLOWED = frozenset({(0, 0), (0, 1), (1, 0)})
State = tuple[int, ...]


def collision_rule(support: int, coefficient: int,
                   pulse: int, balanced: int) -> tuple[int, ...]:
    """Return the full nine-entry q0 table, independently of its interpreter."""
    original = branch_rule(support, coefficient, pulse)
    if type(balanced) is not int or (pulse, balanced) not in _ALLOWED:
        raise ValueError("admitted branches are (pulse,balanced) 00, 01, 10")
    edited = list(original)
    edited[3] = (edited[3] + balanced) % 3   # q0(1,0)
    edited[4] = (edited[4] - balanced) % 3   # q0(1,1)
    return tuple(edited)


@dataclass(frozen=True, order=True)
class CollisionWorld:
    support: int
    coefficient: int
    pulse: int
    balanced: int

    def __post_init__(self) -> None:
        collision_rule(self.support, self.coefficient, self.pulse, self.balanced)

    def world(self) -> WindowProcess:
        return WindowProcess(
            1, (collision_rule(self.support, self.coefficient,
                               self.pulse, self.balanced),),
            (ZERO_WINDOW,),
        )

    def step(self, state: State, action: str) -> State:
        return self.world().step(state, action)

    def inverse(self, state: State, action: str) -> State:
        return self.world().inverse(state, action)

    def move(self, state: State, word: str) -> State:
        if any(a not in "AB" for a in word):
            raise ValueError("word must contain only A and B")
        for a in word:
            state = self.step(state, a)
        return state

    def fixed_word(self, word: str, depth: int = 3) -> int:
        if type(depth) is not int or depth < 3:
            raise ValueError("depth >= 3 required")
        return sum(self.move(x, word) == x
                   for x in product(range(3), repeat=depth))

    def shear_next(self) -> "CollisionWorld":
        return CollisionWorld(self.support, (self.coefficient + 1) % 3,
                              self.pulse, self.balanced)

    def support_next(self) -> "CollisionWorld | None":
        if self.support == 3:
            return None
        return CollisionWorld(self.support + 1, self.coefficient,
                              self.pulse, self.balanced)

    def pulse_next(self) -> "CollisionWorld | None":
        """An independent fork from the ordinary world, not from its edit."""
        if self.pulse != 0 or self.balanced != 0:
            return None
        return CollisionWorld(self.support, self.coefficient, 1, 0)

    def balanced_next(self) -> "CollisionWorld | None":
        """A competing fork; the (pulse=1,balanced=1) world is NOT admitted."""
        if self.pulse != 0 or self.balanced != 0:
            return None
        return CollisionWorld(self.support, self.coefficient, 0, 1)


def family() -> tuple[CollisionWorld, ...]:
    return tuple(CollisionWorld(k, c, e, t)
                 for k in range(4)
                 for e, t in ((0, 0), (0, 1), (1, 0))
                 for c in range(3))


def fixed_word_formula(word: str, depth: int,
                       support: int, pulse: int, balanced: int) -> int:
    """All-depth formulas for the three *admitted* complete-state invariants.

    Every word acts trivially on coordinates >=3, so a depth-three
    fixed-state count is multiplied by 3^(depth-3) at depth d.
    """
    if type(depth) is not int or depth < 3:
        raise ValueError("depth >= 3 required")
    if type(support) is not int or support not in range(4):
        raise ValueError("support must be 0..3")
    if type(pulse) is not int or type(balanced) is not int or (
            pulse, balanced) not in _ALLOWED:
        raise ValueError("branch outside admitted family")
    if word == "B":
        base = (3 - support) * 3
    elif word == "BBB":
        base = 18 if pulse else 27
    elif word == "AABAB":
        base = 6 if pulse else (3 if balanced else 9)
    else:
        raise ValueError("no all-depth formula for this word")
    return base * 3 ** (depth - 3)


@dataclass(frozen=True)
class CollisionRelation:
    status: str
    source: CollisionWorld
    target: CollisionWorld
    shear_witness: int | None
    obstruction_word: str | None
    first_obstruction_depth: int | None
    source_fixed: int
    target_fixed: int

    def map_state(self, state: State) -> State:
        if self.shear_witness is None:
            raise ValueError("no state conjugacy was certified")
        return shear(state, self.shear_witness)


def classify_pair(source: CollisionWorld,
                  target: CollisionWorld) -> CollisionRelation:
    """Complete classification within the declared 36-world family."""
    if source.support != target.support:
        word = "B"
    elif source.pulse != target.pulse:
        word = "BBB"
    elif source.balanced != target.balanced:
        word = "AABAB"
    else:
        word = None
    if word is None:
        return CollisionRelation(
            "ALL_DEPTH_FULL_STATE_CONJUGACY", source, target,
            (target.coefficient - source.coefficient) % 3,
            None, None,
            fixed_word_formula("B", 3, source.support, source.pulse,
                               source.balanced),
            fixed_word_formula("B", 3, target.support, target.pulse,
                               target.balanced),
        )
    a = fixed_word_formula(word, 3, source.support,
                           source.pulse, source.balanced)
    b = fixed_word_formula(word, 3, target.support,
                           target.pulse, target.balanced)
    if a == b:
        raise AssertionError("word does not separate these parameters")
    return CollisionRelation(
        "INEQUIVALENT_WORD_FIXED_POINTS", source, target, None, word,
        3, a, b,
    )


def first_fixed_count_break(source: CollisionWorld,
                            target: CollisionWorld, max_length: int = 5
                            ) -> tuple[str, int, int] | None:
    """Search fixed-word-count differences only; matching counts imply UNKNOWN.

    The words are enumerated length-first, with A before B, so the
    result is a reproducible first *count* obstruction, not a general
    minimal distinguishing state relation.
    """
    if type(max_length) is not int or max_length < 0:
        raise ValueError("max_length must be nonnegative")
    for length in range(1, max_length + 1):
        for letters in product("AB", repeat=length):
            word = "".join(letters)
            a, b = source.fixed_word(word), target.fixed_word(word)
            if a != b:
                return word, a, b
    return None


@dataclass(frozen=True)
class CollisionCertificate:
    status: str
    concrete_laws: int
    full_state_classes: int
    class_sizes: tuple[int, ...]
    aligned_pairs: int
    B_obstructions: int
    BBB_obstructions: int
    AABAB_obstructions: int
    first_balanced_word: str | None
    shortest_fixed_count_obstruction: bool
    failure: str | None = None


def certify_collision() -> CollisionCertificate:
    """Every ordered pair receives an exact map or explicit word obstruction."""
    worlds = family()
    signatures = {
        tuple(w.step(x, "B") for x in product(range(3), repeat=3))
        for w in worlds
    }
    count = {"B": 0, "BBB": 0, "AABAB": 0}
    aligned = 0
    for source in worlds:
        for target in worlds:
            result = classify_pair(source, target)
            if result.shear_witness is not None:
                aligned += 1
                for x in product(range(3), repeat=3):
                    image = result.map_state(x)
                    for action in "AB":
                        if result.map_state(source.step(x, action)) != target.step(
                                image, action):
                            return CollisionCertificate(
                                "OPEN_BAD_ALIGNMENT", len(signatures), 0, (),
                                aligned, count["B"], count["BBB"], count["AABAB"],
                                None, False, "shear conjugacy failed")
            else:
                count[result.obstruction_word] += 1
                if result.source_fixed == result.target_fixed:
                    return CollisionCertificate(
                        "OPEN_INVARIANT_COLLISION", len(signatures), 0, (),
                        aligned, count["B"], count["BBB"], count["AABAB"],
                        None, False, "word fixed counts do not differ")
    a, b = CollisionWorld(0, 0, 0, 0), CollisionWorld(0, 0, 0, 1)
    first = first_fixed_count_break(a, b, 5)
    shortest = first == ("AABAB", 9, 3)
    expect = (len(signatures), aligned, count["B"],
              count["BBB"], count["AABAB"])
    success = expect == (36, 108, 972, 144, 72) and shortest
    return CollisionCertificate(
        "CLOSED_DECLARED_12_FULL_STATE_CLASSES" if success
        else "OPEN_CLASSIFICATION",
        len(signatures), 12 if success else 0, (3,)*12 if success else (),
        aligned, count["B"], count["BBB"], count["AABAB"],
        first[0] if first else None, shortest,
        None if success else f"unexpected pair or word counts: {expect} / {first}",
    )
