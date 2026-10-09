"""Cohomological lift criterion for nonconstant finite-field lower couplings.

Let A increment x0 and B increment x1 by g*(x0+1), x2 by q0(x0,x1),
x3 by b*x2, and x4 by c*x2. All higher increments are zero.

Seek a symmetry of the PARTICULAR triangular form
 F_r: (u,v,z,x3,x4,tail) ->
 (u,v,z+r,x3+b*K_r(v,z),x4+c*K_r(v,z),tail).
The additive correction must commute with A, so it cannot depend on u.

When (b,c)!=(0,0), such a lift exists exactly if q0(2,v)=a!=0
is constant, the sum of q0(0,v) is 0, and
 q0(1,v)+q0(0,v-g)=2*a for every v, in F3.

Then an exact potential phi(v,z)=a^-1*z+alpha(v) satisfies
 phi(v+g*(u+1),z+q0(u,v))-phi(v,z)=1 for every u,v,z.
K_r(v,z)=r*phi(v,z)+a^-1*binom(r,2) yields an order-three,
projectively compatible action of centralizer symmetries.

A separate independent graph calculation exhibits a signed closed
walk of nonzero voltage when the potential does not exist. That
obstruction excludes the stated additive lifts; it does NOT
exclude arbitrary bijective conjugacies or other centralizer elements.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from collections import deque

from .window_two import WindowProcess

F3 = (0, 1, 2)
ZERO = (0,) * 9
State = tuple[int, ...]
Vertex = tuple[int, int]


def _field(value: int) -> None:
    if type(value) is not int or value not in F3:
        raise ValueError("expected an F3 element")


def _state(state: State) -> None:
    if type(state) is not tuple or len(state) < 3 or any(
            type(a) is not int or a not in F3 for a in state):
        raise ValueError("expected an F3 tuple of dimension >=3")


@dataclass(frozen=True)
class Potential:
    """Normalized phi(0,0)=0, with alpha(0)=0 and additive z-slope."""
    gain: int
    drift: int
    alpha: tuple[int, int, int]

    def value(self, v: int, z: int) -> int:
        _field(v)
        _field(z)
        return (pow(self.drift, -1, 3) * z + self.alpha[v]) % 3

    def correction(self, r: int, v: int, z: int) -> int:
        _field(r)
        # Explicit integers 0, 0, 1 represent binom(r,2) in F3.
        return (r * self.value(v, z) +
                pow(self.drift, -1, 3) * (r * (r - 1) // 2)) % 3


def solve_potential(rule: tuple[int, ...], gain: int) -> Potential | None:
    """Exact algebraic criterion, not an enumeration of candidate potentials."""
    if type(rule) is not tuple or len(rule) != 9 or any(
            type(x) is not int or x not in F3 for x in rule):
        raise ValueError("q0 must be a nine-entry F3 table")
    if type(gain) is not int or gain not in (1, 2):
        raise ValueError("gain must be a nonzero F3 element")
    row2 = rule[6:9]
    if row2 not in ((1, 1, 1), (2, 2, 2)):
        return None
    drift = row2[0]
    if sum(rule[:3]) % 3:
        return None
    if any((rule[3+v] + rule[(v-gain) % 3] - 2*drift) % 3
           for v in F3):
        return None
    alpha = [0, 0, 0]
    inv_drift = pow(drift, -1, 3)
    for step in range(2):
        v = (step * gain) % 3
        successor = (v + gain) % 3
        alpha[successor] = (alpha[v] + 1 - inv_drift * rule[v]) % 3
    result = Potential(gain, drift, tuple(alpha))
    # Audit every exact compatibility equation in the finite base.
    for u, v, z in product(F3, repeat=3):
        next_v = (v + gain * (u+1)) % 3
        next_z = (z + rule[3*u+v]) % 3
        if (result.value(next_v, next_z) - result.value(v, z)) % 3 != 1:
            raise AssertionError("symbolic criterion produced an invalid potential")
    return result


@dataclass(frozen=True)
class GraphStep:
    """One formal induced B step, or its inverse, on (x1,x2)."""
    source: Vertex
    target: Vertex
    lower_coordinate_u: int
    direction: int
    voltage: int


@dataclass(frozen=True)
class CycleObstruction:
    """Two paths with the same endpoints but different mod-three voltage."""
    start: Vertex
    end: Vertex
    first: tuple[GraphStep, ...]
    second: tuple[GraphStep, ...]
    first_voltage: int
    second_voltage: int

    def __post_init__(self) -> None:
        if self.first_voltage == self.second_voltage:
            raise ValueError("not a voltage inconsistency")

    def validate(self, rule: tuple[int, ...], gain: int) -> bool:
        """Check every literal edge, endpoint and unequal potential values."""
        def follow(path: tuple[GraphStep, ...]) -> tuple[Vertex, int] | None:
            here, voltage = self.start, 0
            for step in path:
                if step.source != here or step.direction not in (-1, 1):
                    return None
                u = step.lower_coordinate_u
                if type(u) is not int or u not in F3:
                    return None
                if step.direction == 1:
                    v, z = here
                    expected = ((v+gain*(u+1))%3, (z+rule[3*u+v])%3)
                else:
                    v, z = here
                    previous_v = (v-gain*(u+1))%3
                    expected = (previous_v, (z-rule[3*u+previous_v])%3)
                if expected != step.target or step.voltage != step.direction%3:
                    return None
                here, voltage = step.target, (voltage+step.voltage)%3
            return here, voltage
        one, two = follow(self.first), follow(self.second)
        return (one == (self.end, self.first_voltage)
                and two == (self.end, self.second_voltage))


def graph_obstruction(rule: tuple[int, ...], gain: int) -> CycleObstruction | None:
    """Independent finite voltage-graph test on nine lower-coordinate states.

    Edges E_u(v,z)=(v+g(u+1),z+q0(u,v)) are assigned voltage 1;
    their inverses get voltage -1. A potential exists exactly when
    every signed graph cycle has zero total voltage.
    """
    # Reuse the strict table validation but not the symbolic criterion.
    if type(rule) is not tuple or len(rule) != 9 or any(
            type(x) is not int or x not in F3 for x in rule):
        raise ValueError("q0 must be a nine-entry F3 table")
    if type(gain) is not int or gain not in (1, 2):
        raise ValueError("gain must be a nonzero F3 element")
    adjacency: dict[Vertex, list[GraphStep]] = {
        (v,z): [] for v,z in product(F3, repeat=2)}
    for u,v,z in product(F3, repeat=3):
        first=(v,z)
        second=((v+gain*(u+1))%3,(z+rule[3*u+v])%3)
        adjacency[first].append(GraphStep(first,second,u,1,1))
        adjacency[second].append(GraphStep(second,first,u,-1,2))

    def trace(point: Vertex, parent: dict[Vertex, tuple[Vertex,GraphStep] | None]
              ) -> tuple[GraphStep, ...]:
        result = []
        while parent[point] is not None:
            prior, step = parent[point]
            result.append(step)
            point = prior
        result.reverse()
        return tuple(result)

    potentials: dict[Vertex,int] = {}
    for root in adjacency:
        if root in potentials:
            continue
        potentials[root] = 0
        parent: dict[Vertex, tuple[Vertex,GraphStep] | None] = {root: None}
        queue = deque([root])
        while queue:
            here=queue.popleft()
            for edge in adjacency[here]:
                value=(potentials[here]+edge.voltage)%3
                if edge.target in potentials:
                    if potentials[edge.target] != value:
                        first=trace(edge.target,parent)
                        second=trace(here,parent)+(edge,)
                        witness=CycleObstruction(
                            root,edge.target,first,second,
                            potentials[edge.target],value)
                        if not witness.validate(rule,gain):
                            raise AssertionError("invalid signed-cycle witness")
                        return witness
                    continue
                potentials[edge.target]=value
                parent[edge.target]=(here,edge)
                queue.append(edge.target)
    return None


@dataclass(frozen=True)
class NonconstantCouplingSystem:
    """A and B, with q0 arbitrary, q1=b*x2, q2=c*x2, zero higher tail."""
    q0: tuple[int, ...]
    gain: int
    coefficient3: int
    coefficient4: int

    def __post_init__(self) -> None:
        if type(self.q0) is not tuple or len(self.q0) != 9 or any(
                type(x) is not int or x not in F3 for x in self.q0):
            raise ValueError("q0 must be a nine-entry F3 table")
        if type(self.gain) is not int or self.gain not in (1,2):
            raise ValueError("gain must be 1 or 2")
        _field(self.coefficient3)
        _field(self.coefficient4)

    def world(self) -> WindowProcess:
        q1=tuple(self.coefficient3*v%3 for u,v in product(F3,repeat=2))
        q2=tuple(self.coefficient4*u%3 for u,v in product(F3,repeat=2))
        return WindowProcess(self.gain,(self.q0,q1,q2),(ZERO,))

    def step(self,state:State,generator:str)->State:
        return self.world().step(state,generator)

    def inverse(self,state:State,generator:str)->State:
        return self.world().inverse(state,generator)

    @property
    def potential(self) -> Potential | None:
        return solve_potential(self.q0,self.gain)

    @property
    def admits_translation(self) -> bool:
        return ((self.coefficient3,self.coefficient4)==(0,0)
                or self.potential is not None)

    def correction(self,state:State,amount:int)->State:
        _state(state)
        _field(amount)
        if amount and not self.admits_translation:
            raise ValueError("the induced lower-state cocycle is inconsistent")
        out=list(state)
        out[2]=(state[2]+amount)%3
        if amount and (self.coefficient3 or self.coefficient4):
            p=self.potential
            if p is None:
                raise AssertionError("admitted lift lacks potential")
            k=p.correction(amount,state[1],state[2])
            if len(state)>3:
                out[3]=(state[3]+self.coefficient3*k)%3
            if len(state)>4:
                out[4]=(state[4]+self.coefficient4*k)%3
        return tuple(out)


@dataclass(frozen=True)
class DistinguishedSystem:
    system: NonconstantCouplingSystem
    mark: State

    def __post_init__(self) -> None:
        if type(self.mark) is not tuple or len(self.mark)!=5 or any(
                type(v) is not int or v not in F3 for v in self.mark):
            raise ValueError("point must be five F3 digits with a zero higher tail")

    def at_depth(self,depth:int)->State:
        if type(depth) is not int or depth<5:
            raise ValueError("the distinguished point requires depth >=5")
        return self.mark+(0,)*(depth-5)


@dataclass(frozen=True)
class PointedConjugacy:
    source: DistinguishedSystem
    target: DistinguishedSystem
    factors: tuple[int,...]

    def __post_init__(self)->None:
        if (not self.factors or self.source.system!=self.target.system):
            raise ValueError("pointed map requires compatible systems and factors")
        for r in self.factors:
            _field(r)
            if r and not self.source.system.admits_translation:
                raise ValueError("a factor is obstructed by the cocycle")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("the map does not carry the distinguished point")

    def map_state(self,state:State)->State:
        for r in self.factors:
            state=self.source.system.correction(state,r)
        return state

    def inverse(self)->"PointedConjugacy":
        return PointedConjugacy(self.target,self.source,
                               tuple((-r)%3 for r in reversed(self.factors)))

    def then(self,after:"PointedConjugacy")->"PointedConjugacy":
        if self.target!=after.source:
            raise ValueError("intermediate pointed system mismatches")
        return PointedConjugacy(self.source,after.target,self.factors+after.factors)


def translated_point(source:DistinguishedSystem,amount:int)->PointedConjugacy:
    target=DistinguishedSystem(source.system,
                               source.system.correction(source.mark,amount))
    return PointedConjugacy(source,target,(amount,))


@dataclass(frozen=True)
class CohomologyCertificate:
    status: str
    admitted: bool
    potential: Potential | None
    obstruction: CycleObstruction | None


def certify_cohomology(system: NonconstantCouplingSystem) -> CohomologyCertificate:
    if (system.coefficient3,system.coefficient4)==(0,0):
        return CohomologyCertificate("PURE_TRANSLATION_SYMMETRY",True,None,None)
    p=solve_potential(system.q0,system.gain)
    witness=graph_obstruction(system.q0,system.gain)
    if (p is None)!=(witness is not None):
        raise AssertionError("algebraic criterion and cycle obstruction disagree")
    return CohomologyCertificate(
        "EXPLICIT_COHOMOLOGICAL_LIFT" if p else "NONZERO_VOLTAGE_CYCLE",
        p is not None,p,witness,
    )
