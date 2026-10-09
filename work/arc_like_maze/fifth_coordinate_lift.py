"""Exact fifth-coordinate lift over two witnessed order-nine base systems.

The two nonconstant q0 couplings (gains 1,2) admit phi(v,z)=z+alpha(v).
Their selected nonlinear fourth-coordinate rule is q1(v,z)=phi(v,z)^2.
The previously verified centralizer generator translates z by one and
changes y by h(phi)=phi^2; this lower action has order NINE.

Add independently any q2(z,y) as the fifth-coordinate B increment.
Seek an additive fifth-coordinate correction L(v,z,y) which fixes x0,x1
and retains the exact earlier z/y centralizer generator.

The equation on 27 lower states is:
 L(B_lower(s))-L(s) = q2(C_lower(s))-q2(s).
A 27-vertex finite voltage graph has constraint rank five over F3,
so the solution space of q2 tables has dimension four. Precisely:
    q2(z,y) = a*z + f(y)   (a in F3; f:F3->F3).
For such a table L(v,z,y)=a*phi(v,z)+f(y) is an explicit solution.
There are 81 admitted tables, 19,602 obstructed ones per gain.
Every admitted corrected symmetry has order nine; no order-27 lift
arises in THIS prescribed family. Other centralizer maps are UNKNOWN.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from itertools import product

from .nonconstant_drift import solve_potential
from .window_two import WindowProcess

F3=(0,1,2)
State=tuple[int,...]
Vertex=tuple[int,int,int]
ZERO=(0,)*9
BASE={
    1:(0,1,2,0,2,1,1,1,1),
    2:(0,1,2,1,0,2,1,1,1),
}


def _table(values:tuple[int,...])->None:
    if type(values) is not tuple or len(values)!=9 or any(
            type(x) is not int or x not in F3 for x in values):
        raise ValueError("coupling must be a nine-entry F3 table")


def _state(values:State)->None:
    if type(values) is not tuple or len(values)<3 or any(
            type(x) is not int or x not in F3 for x in values):
        raise ValueError("state must be a finite-field tuple of dimension >=3")


def _gain(gain:int)->None:
    if type(gain) is not int or gain not in (1,2):
        raise ValueError("gain must be one or two")


def lower_rules(gain:int)->tuple[tuple[int,...],tuple[int,...],tuple[int,int,int]]:
    """The actual two previous exact laws, not new alias objects."""
    _gain(gain)
    q0=BASE[gain]
    potential=solve_potential(q0,gain)
    if potential is None or potential.drift!=1:
        raise AssertionError("the selected lower construction lost its witness")
    q1=tuple(potential.value(v,z)**2%3 for v,z in product(F3,repeat=2))
    return q0,q1,potential.alpha


def _higher_transition(node:Vertex,u:int,gain:int,
                       q0:tuple[int,...],q1:tuple[int,...])->Vertex:
    v,z,y=node
    return ((v+gain*(u+1))%3,(z+q0[3*u+v])%3,
            (y+q1[3*v+z])%3)


def _central_lower(node:Vertex,alpha:tuple[int,int,int])->Vertex:
    v,z,y=node
    w=(z+alpha[v])%3
    return (v,(z+1)%3,(y+w*w)%3)


@dataclass(frozen=True)
class VoltageEdge:
    source:Vertex
    target:Vertex
    parameter:int
    direction:int
    voltage:int


@dataclass(frozen=True)
class FifthCoordinateObstruction:
    start:Vertex
    end:Vertex
    first_path:tuple[VoltageEdge,...]
    second_path:tuple[VoltageEdge,...]
    first_voltage:int
    second_voltage:int

    def verify(self,gain:int,q2:tuple[int,...])->bool:
        _table(q2)
        q0,q1,alpha=lower_rules(gain)
        if self.first_voltage==self.second_voltage:
            return False

        def follow(steps:tuple[VoltageEdge,...]):
            point=self.start
            total=0
            for edge in steps:
                if edge.source!=point or edge.direction not in (-1,1) or (
                        type(edge.parameter) is not int or edge.parameter not in F3):
                    return None
                if edge.direction==1:
                    source=point
                    target=_higher_transition(point,edge.parameter,gain,q0,q1)
                    image=_central_lower(source,alpha)
                    delta=(q2[3*image[1]+image[2]]
                           -q2[3*source[1]+source[2]])%3
                else:
                    v,z,y=point
                    u=edge.parameter
                    pv=(v-gain*(u+1))%3
                    pz=(z-q0[3*u+pv])%3
                    py=(y-q1[3*pv+pz])%3
                    source=(pv,pz,py)
                    target=source
                    image=_central_lower(source,alpha)
                    delta=(q2[3*source[1]+source[2]]
                           -q2[3*image[1]+image[2]])%3
                if target!=edge.target or delta!=edge.voltage:
                    return None
                point=target
                total=(total+delta)%3
            return point,total
        return (follow(self.first_path)==(self.end,self.first_voltage)
                and follow(self.second_path)==(self.end,self.second_voltage))


def _adjacency(gain:int,q2:tuple[int,...])->dict[Vertex,list[VoltageEdge]]:
    q0,q1,alpha=lower_rules(gain)
    adj={x:[] for x in product(F3,repeat=3)}
    for u,v,z,y in product(F3,repeat=4):
        here=(v,z,y)
        nxt=_higher_transition(here,u,gain,q0,q1)
        shifted=_central_lower(here,alpha)
        voltage=(q2[3*shifted[1]+shifted[2]]-q2[3*z+y])%3
        adj[here].append(VoltageEdge(here,nxt,u,1,voltage))
        adj[nxt].append(VoltageEdge(nxt,here,u,-1,(-voltage)%3))
    return adj


def voltage_graph(gain:int,q2:tuple[int,...]
                  )->tuple[dict[Vertex,int]|None,FifthCoordinateObstruction|None]:
    """Independent signed graph consistency test on 27 vertices and 81 edges."""
    _gain(gain)
    _table(q2)
    adj=_adjacency(gain,q2)
    potentials:dict[Vertex,int]={}

    def path(point:Vertex,parents:dict[Vertex,tuple[Vertex,VoltageEdge]|None]
             )->tuple[VoltageEdge,...]:
        steps=[]
        while parents[point] is not None:
            parent,edge=parents[point]
            steps.append(edge)
            point=parent
        return tuple(reversed(steps))

    for root in adj:
        if root in potentials:
            continue
        potentials[root]=0
        parents:dict[Vertex,tuple[Vertex,VoltageEdge]|None]={root:None}
        queue=deque([root])
        while queue:
            current=queue.popleft()
            for edge in adj[current]:
                next_value=(potentials[current]+edge.voltage)%3
                if edge.target in potentials:
                    if potentials[edge.target]!=next_value:
                        record=FifthCoordinateObstruction(
                            root,edge.target,path(edge.target,parents),
                            path(current,parents)+(edge,),
                            potentials[edge.target],next_value)
                        if not record.verify(gain,q2):
                            raise AssertionError("constructed voltage witness failed")
                        return None,record
                else:
                    potentials[edge.target]=next_value
                    parents[edge.target]=(current,edge)
                    queue.append(edge.target)
    return potentials,None


def linear_constraint_rank(gain:int)->int:
    """Formal voltage constraints on nine symbolic q2 coefficients.

    Tree paths give linear expressions in the nine table entries.
    Each non-tree edge gives a homogeneous equation. Gaussian
    elimination modulo three computes its exact rank (five).
    """
    _gain(gain)
    q0,q1,alpha=lower_rules(gain)
    edges=[]
    adj={x:[] for x in product(F3,repeat=3)}
    for u,v,z,y in product(F3,repeat=4):
        source=(v,z,y)
        target=_higher_transition(source,u,gain,q0,q1)
        shifted=_central_lower(source,alpha)
        delta=[0]*9
        delta[3*shifted[1]+shifted[2]]+=1
        delta[3*z+y]-=1
        vec=tuple(x%3 for x in delta)
        adj[source].append((target,vec))
        adj[target].append((source,tuple((-x)%3 for x in vec)))
    vectors:dict[Vertex,tuple[int,...]]={}
    constraints=[]
    for root in adj:
        if root in vectors:
            continue
        vectors[root]=(0,)*9
        queue=deque([root])
        while queue:
            point=queue.popleft()
            for nxt,voltage in adj[point]:
                trial=tuple((a+b)%3 for a,b in zip(vectors[point],voltage))
                if nxt in vectors:
                    diff=tuple((a-b)%3 for a,b in zip(trial,vectors[nxt]))
                    if any(diff):
                        constraints.append(list(diff))
                else:
                    vectors[nxt]=trial
                    queue.append(nxt)
    rank=0
    for column in range(9):
        pivot=next((i for i in range(rank,len(constraints))
                    if constraints[i][column]),None)
        if pivot is None:
            continue
        constraints[rank],constraints[pivot]=constraints[pivot],constraints[rank]
        unit=pow(constraints[rank][column],-1,3)
        constraints[rank]=[(unit*x)%3 for x in constraints[rank]]
        for row in range(len(constraints)):
            if row!=rank and constraints[row][column]:
                multiplier=constraints[row][column]
                constraints[row]=[(a-multiplier*b)%3 for a,b in
                                  zip(constraints[row],constraints[rank])]
        rank+=1
    return rank


@dataclass(frozen=True)
class FifthAnalysis:
    status:str
    order:int|None
    slope:int|None
    fiber_function:tuple[int,int,int]|None
    obstruction:FifthCoordinateObstruction|None


def classify_fifth(gain:int,q2:tuple[int,...])->FifthAnalysis:
    _gain(gain)
    _table(q2)
    f=q2[:3]
    slope=(q2[3]-q2[0])%3
    admitted=all(q2[3*z+y]==(slope*z+f[y])%3
                 for z,y in product(F3,repeat=2))
    if admitted:
        return FifthAnalysis("ORDER_NINE_CENTRALIZER",9,slope,f,None)
    _,obstruction=voltage_graph(gain,q2)
    if obstruction is None:
        raise AssertionError("factorization criterion disagrees with graph")
    return FifthAnalysis("COHOMOLOGICAL_OBSTRUCTION",None,None,None,obstruction)


@dataclass(frozen=True)
class FifthCoordinateSystem:
    gain:int
    coupling:tuple[int,...]

    def __post_init__(self):
        _gain(self.gain)
        _table(self.coupling)

    @property
    def analysis(self)->FifthAnalysis:
        return classify_fifth(self.gain,self.coupling)

    def world(self)->WindowProcess:
        q0,q1,_=lower_rules(self.gain)
        return WindowProcess(self.gain,(q0,q1,self.coupling),(ZERO,))

    def step(self,x:State,generator:str)->State:
        return self.world().step(x,generator)

    def inverse(self,x:State,generator:str)->State:
        return self.world().inverse(x,generator)

    def generator_lift(self,x:State)->State:
        _state(x)
        proof=self.analysis
        if proof.order is None:
            raise ValueError("fifth-coordinate cocycle has an obstruction")
        _,_,alpha=lower_rules(self.gain)
        v,z,y=x[1:4] if len(x)>=4 else (x[1],x[2],None)
        w=(z+alpha[v])%3
        result=list(x)
        result[2]=(z+1)%3
        if len(x)>=4:
            result[3]=(x[3]+w*w)%3
        if len(x)>=5:
            result[4]=(x[4]+proof.slope*w+proof.fiber_function[y])%3
        return tuple(result)

    def apply_power(self,x:State,n:int)->State:
        _state(x)
        if type(n) is not int or n not in range(9):
            raise ValueError("exponent must be in 0..8")
        if self.analysis.order is None:
            raise ValueError("no proved commuting lift")
        for _ in range(n):
            x=self.generator_lift(x)
        return x


@dataclass(frozen=True)
class PointedFifthSystem:
    system:FifthCoordinateSystem
    mark:State

    def __post_init__(self):
        if type(self.mark) is not tuple or len(self.mark)!=5 or any(
                type(a) is not int or a not in F3 for a in self.mark):
            raise ValueError("mark must have five explicit finite-field digits")

    def at_depth(self,depth:int)->State:
        if type(depth) is not int or depth<5:
            raise ValueError("pointed system requires dimension >=5")
        return self.mark+(0,)*(depth-5)


@dataclass(frozen=True)
class PointedFifthConjugacy:
    source:PointedFifthSystem
    target:PointedFifthSystem
    exponents:tuple[int,...]

    def __post_init__(self):
        if not self.exponents or self.source.system!=self.target.system:
            raise ValueError("requires an unchanged law and explicit map factors")
        if self.source.system.analysis.order!=9 or any(
                type(n) is not int or n not in range(9)
                for n in self.exponents):
            raise ValueError("requires a proved cyclic-order-nine lift")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("pointed map does not preserve the chosen endpoints")

    def map_state(self,x:State)->State:
        for n in self.exponents:
            x=self.source.system.apply_power(x,n)
        return x

    def inverse(self)->"PointedFifthConjugacy":
        return PointedFifthConjugacy(
            self.target,self.source,
            tuple((-n)%9 for n in reversed(self.exponents)))

    def then(self,after:"PointedFifthConjugacy")->"PointedFifthConjugacy":
        if self.target!=after.source:
            raise ValueError("intermediate pointed objects differ")
        return PointedFifthConjugacy(
            self.source,after.target,self.exponents+after.exponents)


def transport_point(source:PointedFifthSystem,
                    exponent:int=1)->PointedFifthConjugacy:
    target=PointedFifthSystem(
        source.system,source.system.apply_power(source.mark,exponent))
    return PointedFifthConjugacy(source,target,(exponent,))
