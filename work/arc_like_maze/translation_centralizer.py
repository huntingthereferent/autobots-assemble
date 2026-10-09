"""Centralizer criterion for coordinate translations in two-predecessor systems.

A and B are the two generating transformations (not a project label).
For each triangular finite-field system, T_r translates coordinate x2.
T_r centralizes the generated action iff both q1(u,v+r)=q1(u,v)
and q2(u+r,v)=q2(u,v) for all u,v in F3. For nonzero r this
is exactly independence of the corresponding table argument.

Only q1 and q2 read x2; q0 and q_i for i>=3 do not. Thus the
criterion holds at every finite dimension, not just sampled prefixes.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .window_two import WindowProcess

State = tuple[int, ...]


def coordinate_translation(state: State, amount: int) -> State:
    if (type(state) is not tuple or len(state) < 3 or
            any(type(x) is not int or x not in (0, 1, 2) for x in state)):
        raise ValueError("state must be a finite-field tuple of dimension >=3")
    if type(amount) is not int or amount not in (0, 1, 2):
        raise ValueError("amount must be an element of F3")
    return state[:2] + ((state[2] + amount) % 3,) + state[3:]


@dataclass(frozen=True)
class CommutationObstruction:
    """Two unequal paths through an explicit generating transformation."""
    first_dimension: int
    coordinate: int
    amount: int
    state: State
    generator: str
    generator_after_translation: State
    translation_after_generator: State

    def __post_init__(self) -> None:
        if self.generator != "B":
            raise ValueError("only the second generator can fail this criterion")
        if self.generator_after_translation == self.translation_after_generator:
            raise ValueError("a counterexample must have different endpoints")


def first_obstruction(world: WindowProcess, amount: int) -> CommutationObstruction | None:
    """Find the first dimension where translation fails to commute with B.

    Exact table search, not a bounded state-space heuristic: by arity two,
    no rule except q1 and q2 can read the translated coordinate x2.
    """
    if type(amount) is not int or amount not in (0, 1, 2):
        raise ValueError("amount must be an element of F3")
    if amount == 0:
        return None
    q1 = world.rule(1)
    for u, v in product(range(3), repeat=2):
        if q1[3 * u + (v + amount) % 3] != q1[3 * u + v]:
            state = (0, u, v, 0)
            p = world.step(coordinate_translation(state, amount), "B")
            q = coordinate_translation(world.step(state, "B"), amount)
            return CommutationObstruction(4, 3, amount, state, "B", p, q)
    q2 = world.rule(2)
    for u, v in product(range(3), repeat=2):
        if q2[3 * ((u + amount) % 3) + v] != q2[3 * u + v]:
            state = (0, 0, u, v, 0)
            p = world.step(coordinate_translation(state, amount), "B")
            q = coordinate_translation(world.step(state, "B"), amount)
            return CommutationObstruction(5, 4, amount, state, "B", p, q)
    return None


def centralizing_amounts(world: WindowProcess) -> tuple[int, ...]:
    """Full subgroup of F3 acting by translations in coordinate x2."""
    return tuple(r for r in range(3) if first_obstruction(world, r) is None)


@dataclass(frozen=True)
class PointedSystem:
    """Complete dynamical system plus an explicit finite-support point."""
    world: WindowProcess
    mark: tuple[int, int, int]

    def __post_init__(self) -> None:
        if (type(self.mark) is not tuple or len(self.mark) != 3 or
                any(type(x) is not int or x not in (0, 1, 2) for x in self.mark)):
            raise ValueError("mark must be an F3 triple with zero higher tail")

    def point(self, dimension: int) -> State:
        if type(dimension) is not int or dimension < 3:
            raise ValueError("dimension must be >=3")
        return self.mark + (0,) * (dimension - 3)


@dataclass(frozen=True)
class PointPreservingConjugacy:
    """Witnessed map between EXPLICIT points in the same dynamical system.

    A change of point is not silently treated as an automorphism of the
    originally pointed system. Factor amounts are kept individually.
    """
    source: PointedSystem
    target: PointedSystem
    amounts: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.amounts:
            raise ValueError("the explicit conjugacy requires its factors")
        if self.source.world != self.target.world:
            raise ValueError("the translation does not change the system law")
        for amount in self.amounts:
            if type(amount) is not int or amount not in centralizing_amounts(self.source.world):
                raise ValueError("translation fails to centralize the generating action")
        if self.map_state(self.source.mark) != self.target.mark:
            raise ValueError("the translation does not preserve the chosen point")

    def map_state(self, state: State) -> State:
        for amount in self.amounts:
            state = coordinate_translation(state, amount)
        return state

    def inverse(self) -> PointPreservingConjugacy:
        return PointPreservingConjugacy(
            self.target, self.source,
            tuple((-amount) % 3 for amount in reversed(self.amounts)),
        )

    def then(self, after: PointPreservingConjugacy) -> PointPreservingConjugacy:
        if self.target != after.source:
            raise ValueError("the intermediate pointed systems do not match")
        return PointPreservingConjugacy(
            self.source, after.target, self.amounts + after.amounts,
        )


def translate_point(source: PointedSystem, amount: int) -> PointPreservingConjugacy:
    """Return an arrow to a NEW explicit point or reject a broken symmetry."""
    mark = coordinate_translation(source.mark, amount)
    return PointPreservingConjugacy(source, PointedSystem(source.world, mark), (amount,))


@dataclass(frozen=True)
class CentralizerCertificate:
    admitted_amounts: tuple[int, ...]
    first_failure_dimension: int | None
    failure_state: State | None
    status: str


def certify_centralizer(world: WindowProcess) -> CentralizerCertificate:
    amounts = centralizing_amounts(world)
    failure = first_obstruction(world, 1)
    # Over the prime field F3, any nonzero additive shift generates all F3.
    if amounts not in ((0,), (0, 1, 2)):
        raise AssertionError("admitted amounts did not form a subgroup of F3")
    if failure is not None:
        if failure.generator_after_translation == failure.translation_after_generator:
            raise AssertionError("invalid B commutation obstruction")
    return CentralizerCertificate(
        amounts, failure.first_dimension if failure else None,
        failure.state if failure else None,
        "CENTRAL_TRANSLATION" if failure is None else "BROKEN_CENTRAL_TRANSLATION",
    )
