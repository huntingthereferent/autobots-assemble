"""A corrected coordinate-translation symmetry, and its exact fiber obstruction.

The generators act over F3: A increments x0; B increments x1 by
gain*(x0+1), x2 by a constant drift, x3 by c3*x2 and
x4 by c4*x2. All coordinates >=5 are fixed. Every action is
triangular, invertible, and consistent under coordinate projection.

When drift != 0, T_r(x2)=x2+r extends to a triangular action of F3:
 x3 -> x3+(c3/drift)*(r*x2+binom(r,2)), similarly x4.
When drift == 0 and (c3,c4) != (0,0), no B-equivariant bijection
preserving x0,x1 and translating x2 by a nonzero constant exists:
the invariant fiber over (x0=2,x1=0,x2=0) consists of B-fixed states,
but the translated fiber contains no B-fixed states at its first
relevant finite dimension (4 or 5). This is a specified-lift
obstruction, NOT universal absence of all conjugacies.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product

from .window_two import WindowProcess

State = tuple[int, ...]
F3 = (0, 1, 2)
ZERO_TABLE = (0,) * 9


def _validate_element(value: int) -> None:
    if type(value) is not int or value not in F3:
        raise ValueError('expected an element of F3')


def _validate_state(state: State) -> None:
    if type(state) is not tuple or len(state) < 3 or any(type(x) is not int or x not in F3 for x in state):
        raise ValueError('expected an F3 state of dimension >=3')


@dataclass(frozen=True)
class LinearHigherCoupling:
    """The specified full-depth two-predecessor action of two generators."""
    drift: int
    coefficient3: int
    coefficient4: int
    gain: int = 1

    def __post_init__(self):
        for value in (self.drift, self.coefficient3, self.coefficient4):
            _validate_element(value)
        if type(self.gain) is not int or self.gain not in (1, 2):
            raise ValueError('gain must be a nonzero F3 element')

    def world(self) -> WindowProcess:
        q0 = (self.drift,) * 9
        q1 = tuple(self.coefficient3 * v % 3 for u, v in product(F3, repeat=2))
        q2 = tuple(self.coefficient4 * u % 3 for u, v in product(F3, repeat=2))
        return WindowProcess(self.gain, (q0, q1, q2), (ZERO_TABLE,))

    def step(self, state: State, generator: str) -> State:
        return self.world().step(state, generator)

    def inverse(self, state: State, generator: str) -> State:
        return self.world().inverse(state, generator)

    @property
    def first_obstruction_dimension(self) -> int | None:
        if self.drift != 0 or (self.coefficient3, self.coefficient4) == (0, 0):
            return None
        return 4 if self.coefficient3 else 5

    @property
    def repairable(self) -> bool:
        return self.first_obstruction_dimension is None

    def correction(self, state: State, amount: int) -> State:
        """Exact all-depth action of F3 or refuse an invalid repaired lift."""
        _validate_state(state)
        _validate_element(amount)
        if amount and not self.repairable:
            raise ValueError('fixed-fiber obstruction forbids this lifted translation')
        out = list(state)
        out[2] = (state[2] + amount) % 3
        if not amount or self.drift == 0:
            return tuple(out)
        inv_drift = pow(self.drift, -1, 3)
        # Binomial(r,2) is 0,0,1 for r=0,1,2 in the prime field.
        binomial = amount * (amount - 1) // 2
        correction = inv_drift * (amount * state[2] + binomial)
        if len(state) > 3:
            out[3] = (state[3] + self.coefficient3 * correction) % 3
        if len(state) > 4:
            out[4] = (state[4] + self.coefficient4 * correction) % 3
        return tuple(out)


@dataclass(frozen=True)
class FiberObstruction:
    """Counterexample for any equivariant bijection extending x2 += 1."""
    dimension: int
    source_prefix: State
    target_prefix: State
    source_B_fixed: int
    translated_B_fixed: int


def obstruction(system: LinearHigherCoupling) -> FiberObstruction | None:
    dimension = system.first_obstruction_dimension
    if dimension is None:
        return None
    # Fix x0=2, x1=0 and x2=0 or x2=1; higher digits vary freely.
    left = (2, 0, 0)
    right = (2, 0, 1)
    source_count = target_count = 0
    for suffix in product(F3, repeat=dimension-3):
        a = left + suffix
        b = right + suffix
        source_count += system.step(a, 'B') == a
        target_count += system.step(b, 'B') == b
    if source_count != 3**(dimension-3) or target_count != 0:
        raise AssertionError('the stated fiber obstruction was not witnessed')
    return FiberObstruction(dimension, left, right, source_count, target_count)


@dataclass(frozen=True)
class PointedHigherSystem:
    system: LinearHigherCoupling
    mark: State  # Full five-coordinate prefix; all omitted tail coordinates are zero.

    def __post_init__(self):
        if type(self.mark) is not tuple or len(self.mark) != 5 or any(type(v) is not int or v not in F3 for v in self.mark):
            raise ValueError('a coherent distinguished point requires five F3 digits')

    def point(self, dimension: int) -> State:
        if type(dimension) is not int or dimension < 5:
            raise ValueError('dimension must be at least five')
        return self.mark + (0,) * (dimension-5)


@dataclass(frozen=True)
class CorrectedConjugacy:
    """Full-state bijection between explicitly pointed *same-law* systems."""
    source: PointedHigherSystem
    target: PointedHigherSystem
    factors: tuple[int, ...]

    def __post_init__(self):
        if not self.factors or self.source.system != self.target.system:
            raise ValueError('literal factors and identical laws are required')
        for amount in self.factors:
            _validate_element(amount)
            if amount and not self.source.system.repairable:
                raise ValueError('the proposed correction does not centralize B')
        if self.map_state(self.source.mark) != self.target.mark:
            raise ValueError('source point does not map to target point')

    def map_state(self, state: State) -> State:
        for amount in self.factors:
            state = self.source.system.correction(state, amount)
        return state

    def then(self, after: 'CorrectedConjugacy') -> 'CorrectedConjugacy':
        if self.target != after.source:
            raise ValueError('distinct intermediate pointed objects')
        return CorrectedConjugacy(self.source, after.target, self.factors + after.factors)

    def inverse(self) -> 'CorrectedConjugacy':
        return CorrectedConjugacy(self.target, self.source,
                                  tuple((-r) % 3 for r in reversed(self.factors)))


def corrected_point(source: PointedHigherSystem, amount: int) -> CorrectedConjugacy:
    mark = source.system.correction(source.mark, amount)
    return CorrectedConjugacy(source, PointedHigherSystem(source.system, mark), (amount,))


@dataclass(frozen=True)
class CorrectionCertificate:
    status: str
    repairable: bool
    first_obstruction_dimension: int | None
    centralizing_amounts: tuple[int, ...]
    fiber_fixed_counts: tuple[int, int] | None


def certify_correction(system: LinearHigherCoupling) -> CorrectionCertificate:
    failure = obstruction(system)
    if failure is not None:
        return CorrectionCertificate('OBSTRUCTED_BY_B_FIXED_FIBER',False,failure.dimension,
                                     (0,), (failure.source_B_fixed,failure.translated_B_fixed))
    # The all-depth proof is given by the polynomial formulas; this checks
    # finite-state witnesses independently for all three amounts.
    for d in range(3, 7):
        for state in product(F3, repeat=d):
            for r in F3:
                for s in F3:
                    if system.correction(system.correction(state,r),s) != system.correction(state,(r+s)%3):
                        raise AssertionError('corrected translations do not form an F3 action')
                for generator in ('A','B'):
                    if system.correction(system.step(state,generator),r) != system.step(system.correction(state,r),generator):
                        raise AssertionError('corrected translation does not commute')
    return CorrectionCertificate('CORRECTED_CENTRALIZER_ACTION',True,None,F3,None)
