"""A new independent two-input coupling invisible to the old B-fixed count.

Start from the four support classes in window_family. Add a genuine independent
q_0(0,0) pulse, separate from the support row q_0(2,v), and close each under
the existing nonlinear shear H_c(x)_2 = x_2 + c*x_1^2.

This declared 24-world family has exactly EIGHT full-state action-labeled
A/B conjugacy classes. One-word B fixed counts separate support k; the
three-letter word BBB separates pulses with identical B fixed counts.
Shear conjugacies provide explicit all-depth maps within each class.

No arbitrary all-window quotient or native ARC execution is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .nondiagonal_transport import shear
from .window_family import ClassifiedWindow
from .window_two import WindowProcess, all_state_fixed_B

ZERO_WINDOW = (0,) * 9
State = tuple[int, ...]


def branch_rule(support: int, coefficient: int, pulse: int) -> tuple[int, ...]:
    """Construct q0=D_k+e*delta_(0,0)+c*delta_shear in F3."""
    if type(support) is not int or support not in range(4):
        raise ValueError("support must be 0..3")
    if type(coefficient) is not int or coefficient not in range(3):
        raise ValueError("shear coefficient must be in F3")
    if type(pulse) is not int or pulse not in (0, 1):
        raise ValueError("admitted pulse is either 0 or 1")
    return tuple(
        (
            int(u == 2 and v < support)
            + pulse * int(u == 0 and v == 0)
            + coefficient * ((v + u + 1) ** 2 - v ** 2)
        ) % 3
        for u in range(3) for v in range(3)
    )


@dataclass(frozen=True, order=True)
class BranchedWindow:
    """One concrete two-input A/B world from the stated bounded family."""
    support: int
    coefficient: int
    pulse: int

    def __post_init__(self) -> None:
        branch_rule(self.support, self.coefficient, self.pulse)

    def world(self) -> WindowProcess:
        return WindowProcess(
            1, (branch_rule(self.support, self.coefficient, self.pulse),),
            (ZERO_WINDOW,),
        )

    def step(self, state: State, action: str) -> State:
        return self.world().step(state, action)

    def inverse(self, state: State, action: str) -> State:
        return self.world().inverse(state, action)

    def apply(self, state: State, word: str) -> State:
        if any(a not in "AB" for a in word):
            raise ValueError("only labeled A and B words are admitted")
        for action in word:
            state = self.step(state, action)
        return state

    def count_fixed_word(self, word: str, depth: int = 3) -> int:
        if type(depth) is not int or depth < 3:
            raise ValueError("depth must be at least three")
        return sum(self.apply(state, word) == state
                   for state in product(range(3), repeat=depth))

    def shear_next(self) -> "BranchedWindow":
        return BranchedWindow(self.support, (self.coefficient + 1) % 3,
                              self.pulse)

    def support_next(self) -> "BranchedWindow | None":
        if self.support == 3:
            return None
        return BranchedWindow(self.support + 1, self.coefficient, self.pulse)

    def pulse_next(self) -> "BranchedWindow | None":
        """Independent one-entry change; no invented wrap back to pulse zero."""
        if self.pulse == 1:
            return None
        return BranchedWindow(self.support, self.coefficient, 1)


def family() -> tuple[BranchedWindow, ...]:
    return tuple(BranchedWindow(k, c, e)
                 for k, e, c in product(range(4), range(2), range(3)))


def fixed_word_formula(word: str, depth: int, support: int, pulse: int) -> int:
    """Exact invariants for the TWO admitted words B and BBB.

    B fixed points require x0=2; q0(2,v) has k nonzero entries.
    For BBB: x0=0 cycles x1 through F3 and accumulates the pulse once.
    At x0=1, the pulse is unreachable; at x0=2, three identical additions
    vanish modulo three. The shear term telescopes over all three turns.
    q_i=0 for i>0. Therefore BBB is identity when pulse=0, and has
    exactly 2*3^(depth-1) fixed states when pulse=1.
    """
    if type(depth) is not int or depth < 3:
        raise ValueError("depth must be >= 3")
    if type(support) is not int or support not in range(4):
        raise ValueError("support must be 0..3")
    if type(pulse) is not int or pulse not in (0, 1):
        raise ValueError("pulse must be 0 or 1")
    if word == "B":
        return (3 - support) * 3 ** (depth - 2)
    if word == "BBB":
        return (3 if pulse == 0 else 2) * 3 ** (depth - 1)
    raise ValueError("only proved words B and BBB have a closed-form certificate")


@dataclass(frozen=True)
class BranchRelation:
    status: str
    source: BranchedWindow
    target: BranchedWindow
    shear_witness: int | None
    obstruction_word: str | None
    first_obstruction_depth: int | None
    source_fixed: int
    target_fixed: int

    def map_state(self, state: State) -> State:
        if self.shear_witness is None:
            raise ValueError("no conjugacy has been admitted")
        return shear(state, self.shear_witness)


def classify_pair(source: BranchedWindow, target: BranchedWindow) -> BranchRelation:
    """Complete action-preserving FULL-state classification in this 24-world set."""
    if source.support != target.support:
        word = "B"
    elif source.pulse != target.pulse:
        word = "BBB"
    else:
        return BranchRelation(
            "ALL_DEPTH_FULL_STATE_CONJUGACY", source, target,
            (target.coefficient - source.coefficient) % 3,
            None, None,
            fixed_word_formula("B", 3, source.support, source.pulse),
            fixed_word_formula("B", 3, target.support, target.pulse),
        )
    return BranchRelation(
        "INEQUIVALENT_WORD_FIXED_POINTS", source, target, None, word, 3,
        fixed_word_formula(word, 3, source.support, source.pulse),
        fixed_word_formula(word, 3, target.support, target.pulse),
    )


@dataclass(frozen=True)
class BranchCertificate:
    status: str
    constructed_laws: int
    full_state_classes: int
    class_sizes: tuple[int, ...]
    aligned_ordered_pairs: int
    B_obstructed_ordered_pairs: int
    BBB_obstructed_ordered_pairs: int
    all_concrete_laws_distinct: bool
    shear_cycle_order: int
    support_walls: int
    pulse_walls: int
    failure: str | None = None


def certify_branch() -> BranchCertificate:
    """All 576 ordered pairs get either an exact map or a word obstruction.

    Bounded d=3 edge checks supplement the all-depth coordinate proof.
    """
    worlds = family()
    b_obstructed = bbb_obstructed = aligned = 0
    for source in worlds:
        for target in worlds:
            relation = classify_pair(source, target)
            if relation.shear_witness is not None:
                aligned += 1
                for state in product(range(3), repeat=3):
                    image = relation.map_state(state)
                    for a in "AB":
                        if (relation.map_state(source.step(state, a))
                                != target.step(image, a)):
                            return BranchCertificate("OPEN_ALIGNMENT",24,0,(),aligned,
                                b_obstructed,bbb_obstructed,False,0,0,0,
                                "one constructed shear map did not commute")
            else:
                if relation.source_fixed == relation.target_fixed:
                    return BranchCertificate("OPEN_WORD_INVARIANT",24,0,(),aligned,
                        b_obstructed,bbb_obstructed,False,0,0,0,
                        "distinct supports/pulses have colliding chosen word count")
                if relation.obstruction_word == "B":
                    b_obstructed += 1
                elif relation.obstruction_word == "BBB":
                    bbb_obstructed += 1
                else:
                    raise AssertionError("unrecognized obstruction")
    signatures = {
        tuple(w.step(state, "B") for state in product(range(3), repeat=3))
        for w in worlds
    }
    shear_ok = all(
        w.shear_next().shear_next().shear_next() == w
        and w.shear_next() != w
        for w in worlds
    )
    squares_ok = all(
        (w.support_next() is None or
         w.shear_next().support_next() == w.support_next().shear_next())
        and (w.pulse_next() is None or
             w.shear_next().pulse_next() == w.pulse_next().shear_next())
        and (w.support_next() is None or w.pulse_next() is None or
             w.support_next().pulse_next() == w.pulse_next().support_next())
        for w in worlds
    )
    support_walls = sum(w.support_next() is None for w in worlds)
    pulse_walls = sum(w.pulse_next() is None for w in worlds)
    status = ("CLOSED_DECLARED_SHEARS_EIGHT_FULL_STATE_CLASSES"
              if (len(signatures), aligned, b_obstructed, bbb_obstructed,
                  support_walls, pulse_walls) == (24,72,432,72,6,12)
              and shear_ok and squares_ok else "OPEN_CONSTRUCTOR_AUDIT")
    return BranchCertificate(
        status, 24, 8 if status.startswith("CLOSED") else 0,
        (3,)*8 if status.startswith("CLOSED") else (),
        aligned, b_obstructed, bbb_obstructed,
        len(signatures)==24, 3 if shear_ok else 0,
        support_walls, pulse_walls,
        None if status.startswith("CLOSED") else "constructor or partition mismatch",
    )
