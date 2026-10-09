"""A second nonconstant coupling creates order-three and order-nine lifts.

Given a previously admitted q0 and its normalized potential phi(v,z),
the second coupling q1(v,z) updates x3. All later couplings are zero.

Look for the SPECIFIED triangular centralizer generator
    C(v,z,y) = (v,z+1,y+K(v,z))
fixing x0,x1 and the remaining coordinates.

Its commutation equation is:
 K(E_u(v,z))-K(v,z) = q1(v,z+1)-q1(v,z).
Here E_u is the induced lower-coordinate B permutation.

The complete exact criterion is that q1(v,z)=Q(phi(v,z))+k(v)
for functions Q,k:F3->F3. Of 3**9 possible q1 tables,
exactly 243 satisfy it. The normalized primitive K depends on phi
alone. Its translation trace is the sum of K over three successive
shifts of z. Of the 243, exactly 81 have trace zero and give an
order-three symmetry; 162 have nonzero trace and give order NINE.

All conjugacies are over the full coherent finite-dimensional systems,
not mere origin orbits. The explicitly specified coordinate form is
essential: a rejected lift does not rule out other centralizer maps.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product

from .nonconstant_drift import Potential, solve_potential
from .window_two import WindowProcess

F3 = (0, 1, 2)
ZERO = (0,) * 9
State = tuple[int, ...]
Lower = tuple[int, int]


def _element(n: int) -> None:
    if type(n) is not int or n not in F3:
        raise ValueError("expected an element of F3")


def _table(q: tuple[int, ...]) -> None:
    if type(q) is not tuple or len(q) != 9 or any(
            type(x) is not int or x not in F3 for x in q):
        raise ValueError("expected a nine-entry F3 coupling table")


def _state(x: State) -> None:
    if type(x) is not tuple or len(x) < 3 or any(
            type(v) is not int or v not in F3 for v in x):
        raise ValueError("state must contain at least three F3 coordinates")


@dataclass(frozen=True)
class WeightedEdge:
    start: Lower
    end: Lower
    lower_parameter: int
    direction: int
    voltage: int


@dataclass(frozen=True)
class VoltageObstruction:
    """Two rigorously checkable lower-state paths requiring different K."""
    start: Lower
    end: Lower
    path_a: tuple[WeightedEdge, ...]
    path_b: tuple[WeightedEdge, ...]
    voltage_a: int
    voltage_b: int

    def validate(self, lower: tuple[int, ...], upper: tuple[int, ...],
                 gain: int) -> bool:
        if self.voltage_a == self.voltage_b:
            return False

        def check(steps: tuple[WeightedEdge, ...]) -> tuple[Lower,int] | None:
            here, total = self.start, 0
            for edge in steps:
                if edge.start != here or edge.direction not in (-1, 1) or (
                        edge.lower_parameter not in F3):
                    return None
                u = edge.lower_parameter
                if edge.direction == 1:
                    v, z = here
                    nxt = ((v+gain*(u+1)) % 3, (z+lower[3*u+v]) % 3)
                    weight = (upper[3*v+(z+1)%3]-upper[3*v+z]) % 3
                else:
                    v, z = here
                    old_v = (v-gain*(u+1)) % 3
                    old_z = (z-lower[3*u+old_v]) % 3
                    nxt = (old_v,old_z)
                    weight = (upper[3*old_v+old_z]
                              -upper[3*old_v+(old_z+1)%3]) % 3
                if edge.end != nxt or edge.voltage != weight:
                    return None
                here, total = nxt, (total+weight) % 3
            return here, total

        return (check(self.path_a) == (self.end,self.voltage_a)
                and check(self.path_b) == (self.end,self.voltage_b))


def signed_cycle_obstruction(lower: tuple[int, ...],
                             upper: tuple[int, ...], gain: int
                             ) -> VoltageObstruction | None:
    """Graph-based, independent obstruction to the correction equation."""
    _table(lower)
    _table(upper)
    if type(gain) is not int or gain not in (1,2):
        raise ValueError("gain must be 1 or 2")
    adj: dict[Lower,list[WeightedEdge]] = {
        (v,z): [] for v,z in product(F3,repeat=2)}
    for u,v,z in product(F3,repeat=3):
        s=(v,z)
        t=((v+gain*(u+1))%3, (z+lower[3*u+v])%3)
        d=(upper[3*v+(z+1)%3]-upper[3*v+z])%3
        adj[s].append(WeightedEdge(s,t,u,1,d))
        adj[t].append(WeightedEdge(t,s,u,-1,(-d)%3))

    def history(node: Lower, parents: dict[Lower, tuple[Lower,WeightedEdge] | None]
                ) -> tuple[WeightedEdge,...]:
        chain = []
        while parents[node] is not None:
            prev, step = parents[node]
            chain.append(step)
            node=prev
        return tuple(reversed(chain))

    assigned: dict[Lower,int] = {}
    for root in adj:
        if root in assigned:
            continue
        assigned[root]=0
        parents: dict[Lower,tuple[Lower,WeightedEdge]|None] = {root:None}
        queue=deque([root])
        while queue:
            here=queue.popleft()
            for edge in adj[here]:
                expected=(assigned[here]+edge.voltage)%3
                if edge.end in assigned:
                    if assigned[edge.end]!=expected:
                        p1=history(edge.end,parents)
                        p2=history(here,parents)+(edge,)
                        result=VoltageObstruction(root,edge.end,p1,p2,
                                                  assigned[edge.end],expected)
                        if not result.validate(lower,upper,gain):
                            raise AssertionError("signed-cycle witness is invalid")
                        return result
                else:
                    assigned[edge.end]=expected
                    parents[edge.end]=(here,edge)
                    queue.append(edge.end)
    return None


@dataclass(frozen=True)
class LiftAnalysis:
    """Exact classification of a prescribed additive x3 correction."""
    status: str
    order: int | None
    quotient: tuple[int, int, int] | None
    row_offsets: tuple[int, int, int] | None
    primitive: tuple[int, int, int] | None
    three_turn_trace: int | None
    obstruction: VoltageObstruction | None


def classify_upper(lower: tuple[int, ...], upper: tuple[int, ...],
                   gain: int) -> LiftAnalysis:
    """Algebraic factorization plus an independently validated graph witness."""
    _table(upper)
    potential=solve_potential(lower,gain)
    if potential is None:
        raise ValueError("lower table has no previously admitted potential")
    a=potential.drift
    inverse=pow(a,-1,3)
    Q=tuple(upper[a*w] for w in F3)   # alpha(0)=0
    k=tuple((upper[3*v+(-a*potential.alpha[v])%3]-Q[0])%3
            for v in F3)
    is_factorized=all(
        upper[3*v+z]==(Q[potential.value(v,z)]+k[v])%3
        for v,z in product(F3,repeat=2)
    )
    if not is_factorized:
        witness=signed_cycle_obstruction(lower,upper,gain)
        if witness is None:
            raise AssertionError("algebraic obstruction lacks graph witness")
        return LiftAnalysis("COHOMOLOGICAL_OBSTRUCTION",None,None,None,
                            None,None,witness)

    # Primitive h(w+1)-h(w)=Q(w+a^-1)-Q(w).
    h=[0,0,0]
    h[1]=(Q[inverse]-Q[0])%3
    h[2]=(h[1]+Q[(1+inverse)%3]-Q[1])%3
    if (h[0]-h[2]-Q[(2+inverse)%3]+Q[2])%3:
        raise AssertionError("cyclic primitive does not close")
    # Signed voltage test is logically independent of the row factorization.
    if signed_cycle_obstruction(lower,upper,gain) is not None:
        raise AssertionError("admitted factorization failed graph test")
    trace=sum(h)%3
    return LiftAnalysis("ORDER_THREE_CENTRALIZER" if trace==0
                        else "ORDER_NINE_CENTRALIZER",
                        3 if trace==0 else 9,Q,k,tuple(h),trace,None)


@dataclass(frozen=True)
class HigherCouplingSystem:
    """The constructed system with an arbitrary nonconstant q1 and zero tail."""
    lower: tuple[int, ...]
    gain: int
    upper: tuple[int, ...]

    def __post_init__(self) -> None:
        _table(self.lower)
        _table(self.upper)
        if solve_potential(self.lower,self.gain) is None:
            raise ValueError("this extension requires the admitted lower potential")

    @property
    def potential(self) -> Potential:
        p=solve_potential(self.lower,self.gain)
        if p is None:
            raise AssertionError("missing previously checked lower potential")
        return p

    @property
    def analysis(self) -> LiftAnalysis:
        return classify_upper(self.lower,self.upper,self.gain)

    def world(self) -> WindowProcess:
        return WindowProcess(self.gain,(self.lower,self.upper),(ZERO,))

    def step(self,x:State,generator:str)->State:
        return self.world().step(x,generator)

    def inverse(self,x:State,generator:str)->State:
        return self.world().inverse(x,generator)

    def generator_lift(self,x:State)->State:
        """One corrected translation, when the cohomological equation admits it."""
        _state(x)
        analysis=self.analysis
        if analysis.order is None:
            raise ValueError("no commuting additive higher-coordinate lift exists")
        w=self.potential.value(x[1],x[2])
        out=list(x)
        out[2]=(x[2]+1)%3
        if len(x)>=4:
            out[3]=(x[3]+analysis.primitive[w])%3
        return tuple(out)

    def apply_power(self,x:State,power:int)->State:
        """Retain order nine when the three-turn trace is nonzero."""
        _state(x)
        order=self.analysis.order
        if order is None:
            raise ValueError("the proposed correction is obstructed")
        if type(power) is not int or power < 0 or power >= order:
            raise ValueError("power must use the proven finite cyclic order")
        for _ in range(power):
            x=self.generator_lift(x)
        return x


@dataclass(frozen=True)
class PointedHigherSystem:
    system: HigherCouplingSystem
    mark: State

    def __post_init__(self) -> None:
        if type(self.mark) is not tuple or len(self.mark)!=4 or any(
                type(x) is not int or x not in F3 for x in self.mark):
            raise ValueError("distinguished point must have four explicit F3 digits")

    def at_depth(self,depth:int)->State:
        if type(depth) is not int or depth<4:
            raise ValueError("distinguished point requires dimension >=4")
        return self.mark+(0,)*(depth-4)


@dataclass(frozen=True)
class PointedHigherConjugacy:
    """Proven centralizer map between explicitly different pointed systems."""
    source: PointedHigherSystem
    target: PointedHigherSystem
    exponents: tuple[int,...]

    def __post_init__(self) -> None:
        if not self.exponents or self.source.system!=self.target.system:
            raise ValueError("requires factors and an unchanged system law")
        order=self.source.system.analysis.order
        if order is None or any(type(e) is not int or not 0<=e<order
                                for e in self.exponents):
            raise ValueError("factor uses an unproved centralizer map")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("pointed conjugacy does not transport the mark")

    def map_state(self,x:State)->State:
        for e in self.exponents:
            x=self.source.system.apply_power(x,e)
        return x

    def inverse(self)->"PointedHigherConjugacy":
        order=self.source.system.analysis.order
        return PointedHigherConjugacy(
            self.target,self.source,
            tuple((-e)%order for e in reversed(self.exponents)),
        )

    def then(self,after:"PointedHigherConjugacy")->"PointedHigherConjugacy":
        if self.target!=after.source:
            raise ValueError("intermediate pointed systems disagree")
        return PointedHigherConjugacy(
            self.source,after.target,self.exponents+after.exponents,
        )


def transport_point(source:PointedHigherSystem,power:int=1)->PointedHigherConjugacy:
    mark=source.system.apply_power(source.mark,power)
    return PointedHigherConjugacy(
        source,PointedHigherSystem(source.system,mark),(power,),
    )
