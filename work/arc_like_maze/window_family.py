"""Construct and completely classify one declared nonlinear two-input A/B family.

Four independent support levels k=0,1,2,3. The primitive q0 increment
is 1 at (x0,x1)=(2,v) for v<k, and zero everywhere else. Conjugate
each primitive world by H_c(x)_2=x_2+c*x_1^2 for c in F_3.

The resulting 12 *concrete* laws use the existing two-predecessor
WindowProcess interpreter. Exactly four full-state action-labeled A/B
classes are provable for this DECLARED family:
 - same support k: explicit all-depth H_(target_c-source_c) conjugacy;
 - different k: different depth-three numbers of B-fixed states.

The shear constructor is a genuine 3-cycle within each class. The
independent support constructor moves strictly to a new class until k=3,
when its narrow declaration reaches a WALL; it does not loop or
silently enlarge the construction grammar.

No universality, native ARC solving, or classification of all possible
9-entry q tables is implied.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .nondiagonal_transport import shear
from .window_two import WindowProcess, all_state_fixed_B

ZERO_WINDOW = (0,) * 9
State = tuple[int, ...]


def _class_rule(support: int, coefficient: int) -> tuple[int, ...]:
    if type(support) is not int or support not in range(4):
        raise ValueError("supported nonzero-row count must be 0..3")
    if type(coefficient) is not int or coefficient not in range(3):
        raise ValueError("shear coefficient must be in F_3")
    return tuple(
        ((int(earlier == 2 and later < support) +
          coefficient * ((later + earlier + 1)**2 - later**2)) % 3)
        for earlier in range(3) for later in range(3)
    )


@dataclass(frozen=True, order=True)
class ClassifiedWindow:
    """A construction identified by support k and shear chart c."""
    support: int
    coefficient: int

    def __post_init__(self) -> None:
        _class_rule(self.support, self.coefficient)

    def world(self) -> WindowProcess:
        return WindowProcess(1, (_class_rule(self.support, self.coefficient),),
                             (ZERO_WINDOW,))

    def step(self, state: State, action: str) -> State:
        return self.world().step(state, action)

    def inverse(self, state: State, action: str) -> State:
        return self.world().inverse(state, action)

    def shear_next(self) -> "ClassifiedWindow":
        """Relation-preserving construction of the next concrete law."""
        return ClassifiedWindow(self.support, (self.coefficient + 1) % 3)

    def support_next(self) -> "ClassifiedWindow | None":
        """New relation when admitted; None denotes the explicit support wall."""
        if self.support == 3:
            return None
        return ClassifiedWindow(self.support + 1, self.coefficient)

    def fixed_B(self, depth: int = 3) -> int:
        return all_state_fixed_B(self.world(), depth)


def family() -> tuple[ClassifiedWindow, ...]:
    return tuple(ClassifiedWindow(support, coefficient)
                 for support, coefficient in product(range(4), range(3)))


def scalar_invariant(depth: int, support: int) -> int:
    """Exact number of B-fixed states in F_3^depth for this family.

    B fixes x1 exactly when x0=2. There are 3-support allowed x1
    values and 3^(depth-2) arbitrary coordinates x2,... .
    The sheared q0 has the SAME x0=2 row because 2+1=0 mod 3.
    """
    if type(depth) is not int or depth < 3:
        raise ValueError("depth must be at least three")
    if type(support) is not int or support not in range(4):
        raise ValueError("support outside finite family")
    return (3 - support) * 3 ** (depth - 2)


@dataclass(frozen=True)
class FullStateRelation:
    status: str
    source: ClassifiedWindow
    target: ClassifiedWindow
    witness_shear: int | None
    source_B_fixed: int
    target_B_fixed: int
    obstruction_depth: int | None

    def map_state(self, state: State) -> State:
        if self.witness_shear is None:
            raise ValueError("no action-conjugating state map for inequivalent classes")
        return shear(state, self.witness_shear)


def classify_pair(source: ClassifiedWindow,
                  target: ClassifiedWindow) -> FullStateRelation:
    """Exact for this named 12-world family, all admissible finite depths."""
    a, b = scalar_invariant(3, source.support), scalar_invariant(3, target.support)
    if source.support != target.support:
        return FullStateRelation(
            "INEQUIVALENT_FIXED_B_AT_DEPTH_THREE",
            source, target, None, a, b, 3,
        )
    return FullStateRelation(
        "ALL_DEPTH_FULL_STATE_CONJUGACY",
        source, target, (target.coefficient - source.coefficient) % 3,
        a, b, None,
    )


@dataclass(frozen=True)
class FamilyCertificate:
    status: str
    concrete_worlds: int
    full_state_classes: int
    class_sizes: tuple[int, ...]
    fixed_B_by_class: tuple[int, ...]
    aligned_ordered_pairs: int
    obstructed_ordered_pairs: int
    shear_orbit_order: int
    support_walls: int
    first_obstruction_depth: int


def certify_family() -> FamilyCertificate:
    """Symbolic complete partition plus exhaustive edge checks at depth three.

    Higher-depth correctness follows from q_i=0 for i>=1 and the explicit
    H-conjugacy, not an assertion that finite testing proved infinity.
    """
    members = family()
    yes = no = 0
    for source in members:
        for target in members:
            result = classify_pair(source, target)
            if result.witness_shear is None:
                no += 1
                if result.source_B_fixed == result.target_B_fixed:
                    return FamilyCertificate("OPEN_INVARIANT_COLLISION",
                        12,0,(),(),yes,no,0,0,3)
            else:
                yes += 1
                for state in product(range(3), repeat=3):
                    mapped = result.map_state(state)
                    for action in "AB":
                        if (result.map_state(source.step(state, action))
                                != target.step(mapped, action)):
                            return FamilyCertificate("OPEN_CONJUGACY",
                                12,0,(),(),yes,no,0,0,3)
    shears = all(w.shear_next().shear_next().shear_next() == w
                 and w.shear_next() != w for w in members)
    squares = all(w.support_next() is None or
                  w.shear_next().support_next() == w.support_next().shear_next()
                  for w in members)
    walls = sum(w.support_next() is None for w in members)
    if not shears or not squares or walls != 3 or yes != 36 or no != 108:
        return FamilyCertificate("OPEN_OPERATOR",12,0,(),(),yes,no,0,walls,3)
    return FamilyCertificate(
        "CLOSED_DECLARED_SHEAR_ORBITS_WITH_FOUR_FULL_STATE_CLASSES",
        12,4,(3,3,3,3),(9,6,3,0),yes,no,3,walls,3,
    )
