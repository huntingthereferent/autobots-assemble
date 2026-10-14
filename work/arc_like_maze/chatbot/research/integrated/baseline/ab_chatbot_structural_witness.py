"""A bounded relational reconstruction experiment for the A/B chatbot research.

Scope: X = F_3^3; A and B are labeled transformations. This demonstrates
four-anchor *reconstruction under independently established covariances*.
An arbitrary black-box oracle is never certified by four anchor queries.

The immutable CovariantSource is a small proof-carrying *implementation*: its
form enforces the covariance equations by construction. It is not evidence
that a separate, unrelated physical or external oracle shares those laws.

Run beside ab_chatbot_relation_probe.py and ab_chatbot_admission_probe.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable

from ab_chatbot_admission_probe import OffOrbitAlteration, check_full_state_law
from ab_chatbot_relation_probe import FiniteSystem

State = tuple[int, int, int]
StepOracle = Callable[[State, str], State]
F3 = range(3)
ZERO = (0, 0, 0)
A_INCREMENT = (1, 0, 0)
B_X0_INCREMENT = (1, 1, 0)
B_X2_INCREMENT = (0, 0, 1)
ANCHORS = (((0, 0, 0), "A"),) + tuple(((0, j, 0), "B") for j in F3)


def add(x: State, y: State) -> State:
    return tuple((a + b) % 3 for a, b in zip(x, y))  # type: ignore[return-value]


def scale(n: int, x: State) -> State:
    return tuple((n * a) % 3 for a in x)  # type: ignore[return-value]


def is_state(x: object) -> bool:
    return (isinstance(x, tuple) and len(x) == 3 and
            all(type(a) is int and a in F3 for a in x))


@dataclass(frozen=True)
class CovariantSource:
    """A source representation where the translation laws hold identically.

    A(x+t)=A(x)+t for all t.
    B(x+e0)=B(x)+(1,1,0); B(x+e2)=B(x)+e2.

    These equalities are true from the executable representation, not guessed
    from a few observations. They say nothing about a separate black box.
    """
    a_origin: State
    b_anchors: tuple[State, State, State]

    def __post_init__(self) -> None:
        if not is_state(self.a_origin):
            raise ValueError("A origin is not a three-coordinate F3 state")
        if len(self.b_anchors) != 3 or any(not is_state(b) for b in self.b_anchors):
            raise ValueError("B anchors must be three F3 states")

    @classmethod
    def for_law(cls, phi: tuple[int, int, int]) -> "CovariantSource":
        if not is_state(phi):
            raise ValueError("phi must be in F3^3")
        return cls(A_INCREMENT,
                   tuple((0, (j + 1) % 3, phi[j]) for j in F3))  # type: ignore[arg-type]

    def step(self, x: State, action: str) -> State:
        if not is_state(x):
            raise ValueError("invalid state")
        i, j, k = x
        if action == "A":
            return add(x, self.a_origin)
        if action == "B":
            return add(add(self.b_anchors[j], scale(i, B_X0_INCREMENT)),
                       scale(k, B_X2_INCREMENT))
        raise ValueError("action must be A or B")


@dataclass(frozen=True)
class StructuralResult:
    status: str
    phi: tuple[int, int, int] | None
    queries: tuple[tuple[State, str, State], ...]
    counterexample: tuple[State, str, object, object] | None = None

    @property
    def calls(self) -> int:
        return len(self.queries)


def reconstruct(
    observe_step: StepOracle,
    *,
    max_calls: int = 4,
    source: CovariantSource | None = None,
) -> StructuralResult:
    """Four observations. Admit a full law only from the bound source form.

    Without source: the inferred phi is CONDITIONAL_ON_COVARIANCE, never
    verified. To claim that an independent oracle has the structural form,
    supply external mathematical evidence; a boolean assertion is not a proof.

    With source: observe_step must be the *same native CovariantSource.step*
    bound to that exact immutable instance, not an arbitrary external callback.
    This establishes only the behavior of that source implementation.
    """
    if max_calls < 0:
        raise ValueError("negative observation budget")
    if source is not None and not (
        type(source) is CovariantSource and
        getattr(observe_step, "__self__", None) is source and
        getattr(observe_step, "__func__", None) is CovariantSource.step
    ):
        raise ValueError("supplied source does not own this transition oracle")

    records: list[tuple[State, str, State]] = []
    values: list[State] = []
    for state, action in ANCHORS:
        if len(records) >= max_calls:
            return StructuralResult("UNKNOWN_BUDGET", None, tuple(records))
        value = observe_step(state, action)
        records.append((state, action, value))
        if not is_state(value):
            return StructuralResult("OBSTRUCTED_BY_ANCHOR", None, tuple(records),
                                    (state, action, value, "valid F3^3 state"))
        if action == "A":
            expected = A_INCREMENT
            if value != expected:
                return StructuralResult("OBSTRUCTED_BY_ANCHOR", None, tuple(records),
                                        (state, action, value, expected))
        else:
            j = state[1]
            if value[:2] != (0, (j + 1) % 3):
                return StructuralResult("OBSTRUCTED_BY_ANCHOR", None, tuple(records),
                                        (state, action, value, (0, (j + 1) % 3, "phi[j]")))
        values.append(value)

    phi = (values[1][2], values[2][2], values[3][2])
    if source is None:
        return StructuralResult("CONDITIONAL_ON_COVARIANCE", phi, tuple(records))
    return StructuralResult("VERIFIED_SOURCE_CONSTRUCTION", phi, tuple(records))


def reconstruct_known_a(
    observe_step: StepOracle,
    *,
    max_calls: int = 3,
    source: CovariantSource | None = None,
) -> StructuralResult:
    """Three B anchors when A is separately known to be x -> x + e0.

    With a native source, both A and the B-covariance identities follow from
    the implementation and are checked at the source boundary. Otherwise the
    result is conditional on BOTH premises; samples alone prove neither.
    """
    if max_calls < 0:
        raise ValueError("negative observation budget")
    if source is not None:
        if not (type(source) is CovariantSource and
                getattr(observe_step, "__self__", None) is source and
                getattr(observe_step, "__func__", None) is CovariantSource.step):
            raise ValueError("supplied source does not own this transition oracle")
        if source.a_origin != A_INCREMENT:
            return StructuralResult("OBSTRUCTED_BY_SOURCE", None, ())

    records: list[tuple[State, str, State]] = []
    phi: list[int] = []
    for j in F3:
        if len(records) >= max_calls:
            return StructuralResult("UNKNOWN_BUDGET", None, tuple(records))
        state = (0, j, 0)
        value = observe_step(state, "B")
        records.append((state, "B", value))
        if not is_state(value):
            return StructuralResult("OBSTRUCTED_BY_ANCHOR", None, tuple(records),
                                    (state, "B", value, "valid F3^3 state"))
        if value[:2] != (0, (j + 1) % 3):
            return StructuralResult("OBSTRUCTED_BY_ANCHOR", None, tuple(records),
                                    (state, "B", value, (0, (j + 1) % 3, "phi[j]")))
        phi.append(value[2])

    status = ("VERIFIED_SOURCE_CONSTRUCTION" if source is not None else
              "CONDITIONAL_ON_KNOWN_A_AND_COVARIANCE")
    return StructuralResult(status, tuple(phi), tuple(records))  # type: ignore[arg-type]


def reconstruct_full_table(phi: tuple[int, int, int]) -> dict[tuple[State, str], State]:
    """All 54 transitions mathematically implied *if* covariances hold."""
    source = CovariantSource.for_law(phi)
    return {(s, act): source.step(s, act)
            for s in product(F3, repeat=3) for act in "AB"}


def check_covariances(
    observe_step: StepOracle,
) -> tuple[bool, tuple[State, str, object, object] | None, int]:
    """Full-domain black-box audit, NOT a four-observation shortcut."""
    cache: dict[tuple[State, str], State] = {}

    def read(s: State, action: str) -> State:
        key = (s, action)
        if key not in cache:
            cache[key] = observe_step(s, action)
        return cache[key]

    e0 = (1, 0, 0)
    e1 = (0, 1, 0)
    e2 = (0, 0, 1)
    for s in product(F3, repeat=3):
        for e in (e0, e1, e2):
            left, right = read(add(s, e), "A"), add(read(s, "A"), e)
            if left != right:
                return False, (s, "A", left, right), len(cache)
        for e, image_change in ((e0, B_X0_INCREMENT), (e2, e2)):
            left, right = read(add(s, e), "B"), add(read(s, "B"), image_change)
            if left != right:
                return False, (s, "B", left, right), len(cache)
    return True, None, len(cache)


def main() -> None:
    ok = 0
    for phi in product(F3, repeat=3):
        law = FiniteSystem(phi)
        native = CovariantSource.for_law(phi)
        observed = reconstruct(native.step, source=native)
        assert observed.status == "VERIFIED_SOURCE_CONSTRUCTION" and observed.calls == 4
        assert observed.phi == phi
        assert reconstruct(law.step).status == "CONDITIONAL_ON_COVARIANCE"
        assert reconstruct_full_table(phi) == {
            (s, act): law.step(s, act)
            for s in product(F3, repeat=3) for act in "AB"
        }
        ok += 1
    mutated = OffOrbitAlteration()
    ambiguous = reconstruct(mutated.step)
    assert ambiguous.status == "CONDITIONAL_ON_COVARIANCE"
    assert ambiguous.phi == (0, 0, 0)
    valid, mismatch, _ = check_covariances(mutated.step)
    assert not valid and mismatch is not None
    rejected = check_full_state_law(mutated.step)
    assert rejected.status == "OUTSIDE_27_GRAMMAR"
    for phi in product(F3, repeat=3):
        source = CovariantSource.for_law(phi)
        short = reconstruct_known_a(source.step, source=source)
        assert short.status == "VERIFIED_SOURCE_CONSTRUCTION"
        assert short.phi == phi and short.calls == 3
    print(f"Certified-by-construction source: {ok} / 27 laws reconstructed in four reads")
    print("When A is already source-certified: 27 / 27 laws reconstructed in three B reads")
    print("Black-box four-anchor reconstruction: CONDITIONAL_ON_COVARIANCE")
    print("Unobserved structural counterexample: same anchors, violated covariance")
    print("Full black-box scan detects altered law:", rejected.mismatch)
    print("No unrestricted four-query admission theorem is claimed")


if __name__ == "__main__":
    main()
