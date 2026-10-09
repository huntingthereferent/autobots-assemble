"""Zero-trace fourth-coordinate centralizer: fifth-coordinate lifts over F3.

Previously admitted q0 and q1=Q(phi)+k(v), now with sum Q=0.
The canonical lower commuting map C acts by (v,z,y) ->
(v,z+1,y+Q(phi)-Q(0)) and has EXACT order three.

A fifth-coordinate additive correction L(v,z,y) must solve 81 equations
 L(E_u(s))-L(s) = q2(C(s))-q2(s)
on the 27 states s=(v,z,y). Signed graph components may number one
or three. Their independent correction constants can change the order.

There are 81 zero-trace (Q,k) configurations per gain. Both gains:
  162 configurations; 22,410 admitted (configuration,q2) combinations.
   9,918 combinations allow only order three;
  11,304 require order nine;
   1,188 allow BOTH orders via independently chosen component constants.

This is an exact classification of THIS triangular additive lift, not
all centralizer automorphisms or any general inverse-construction closure.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from .fifth_coordinate_lift import BASE
from .nonconstant_drift import solve_potential

F3=(0,1,2)
ZERO=(0,)*9
State=tuple[int,...]
Vertex=tuple[int,int,int]
VERTICES=tuple(product(F3,repeat=3))
INDEX={v:i for i,v in enumerate(VERTICES)}


def _field(x:int)->None:
    if type(x) is not int or x not in F3:
        raise ValueError("requires an element of F3")


def _triple(v:tuple[int,...])->None:
    if type(v) is not tuple or len(v)!=3:
        raise ValueError("requires a three-element tuple")
    for x in v:_field(x)


def _rule(q:tuple[int,...])->None:
    if type(q) is not tuple or len(q)!=9:
        raise ValueError("requires a nine-entry coupling table")
    for x in q:_field(x)


def _state(x:State)->None:
    if type(x) is not tuple or len(x)<3:
        raise ValueError("state must have at least three finite-field coordinates")
    for t in x:_field(t)


def _rank(vectors:tuple[tuple[int,...],...]|list[tuple[int,...]],width:int)->int:
    if not vectors:return 0
    rows=[list(v) for v in vectors if any(v)]
    i=0
    for j in range(width):
        p=next((n for n in range(i,len(rows)) if rows[n][j]),None)
        if p is None:continue
        rows[i],rows[p]=rows[p],rows[i]
        scale=pow(rows[i][j],-1,3)
        rows[i]=[(x*scale)%3 for x in rows[i]]
        for n in range(len(rows)):
            if n!=i and rows[n][j]:
                a=rows[n][j]
                rows[n]=[(x-a*y)%3 for x,y in zip(rows[n],rows[i])]
        i+=1
    return i


def _basis(constraints:list[tuple[int,...]])->tuple[int,tuple[tuple[int,...],...]]:
    rows=[list(row) for row in constraints if any(row)]
    pivots=[]
    i=0
    for j in range(9):
        p=next((n for n in range(i,len(rows)) if rows[n][j]),None)
        if p is None:continue
        rows[i],rows[p]=rows[p],rows[i]
        scale=pow(rows[i][j],-1,3)
        rows[i]=[(x*scale)%3 for x in rows[i]]
        for n in range(len(rows)):
            if n!=i and rows[n][j]:
                a=rows[n][j]
                rows[n]=[(x-a*y)%3 for x,y in zip(rows[n],rows[i])]
        pivots.append(j)
        i+=1
    free=[j for j in range(9) if j not in pivots]
    vectors=[]
    for j in free:
        q=[0]*9
        q[j]=1
        for pivot,row in zip(pivots,rows[:i]):
            q[pivot]=(-row[j])%3
        vectors.append(tuple(q))
    return i,tuple(vectors)


@dataclass(frozen=True)
class ZeroTraceParameters:
    gain:int
    quotient:tuple[int,int,int]
    offsets:tuple[int,int,int]

    def __post_init__(self):
        if type(self.gain) is not int or self.gain not in (1,2):
            raise ValueError("only the previously proved gains 1 and 2")
        _triple(self.quotient)
        _triple(self.offsets)
        if self.offsets[0]!=0:
            raise ValueError("first row offset must be normalized to zero")
        if sum(self.quotient)%3:
            raise ValueError("this family requires a ZERO three-turn trace")

    @property
    def alpha(self)->tuple[int,int,int]:
        phi=solve_potential(BASE[self.gain],self.gain)
        if phi is None or phi.drift!=1:
            raise AssertionError("previous lower potential is missing")
        return phi.alpha

    @property
    def fourth_rule(self)->tuple[int,...]:
        a=self.alpha
        return tuple((self.quotient[(z+a[v])%3]+self.offsets[v])%3
                     for v,z in product(F3,repeat=2))

    def induced_B(self,s:Vertex,u:int)->Vertex:
        _field(u)
        v,z,y=s
        w=(z+self.alpha[v])%3
        return ((v+self.gain*(u+1))%3,
                (z+BASE[self.gain][3*u+v])%3,
                (y+self.quotient[w]+self.offsets[v])%3)

    def inverse_B(self,s:Vertex,u:int)->Vertex:
        _field(u)
        v,z,y=s
        pv=(v-self.gain*(u+1))%3
        pz=(z-BASE[self.gain][3*u+pv])%3
        pw=(pz+self.alpha[pv])%3
        return pv,pz,(y-self.quotient[pw]-self.offsets[pv])%3

    def lower_symmetry(self,s:Vertex)->Vertex:
        v,z,y=s
        w=(z+self.alpha[v])%3
        return v,(z+1)%3,(y+self.quotient[w]-self.quotient[0])%3

    def step(self,state:State,generator:str,fifth:tuple[int,...])->State:
        _state(state);_rule(fifth)
        result=list(state)
        if generator=="A":
            result[0]=(state[0]+1)%3
        elif generator=="B":
            u,v,z=state[:3]
            result[1]=(v+self.gain*(u+1))%3
            result[2]=(z+BASE[self.gain][3*u+v])%3
            if len(state)>=4:
                result[3]=(state[3]+self.fourth_rule[3*v+z])%3
            if len(state)>=5:
                result[4]=(state[4]+fifth[3*z+state[3]])%3
        else:
            raise ValueError("generator must be A or B")
        return tuple(result)

    def inverse(self,state:State,generator:str,fifth:tuple[int,...])->State:
        _state(state);_rule(fifth)
        result=list(state)
        if generator=="A":
            result[0]=(state[0]-1)%3
        elif generator=="B":
            u=state[0]
            result[1]=(state[1]-self.gain*(u+1))%3
            pv=result[1]
            result[2]=(state[2]-BASE[self.gain][3*u+pv])%3
            pz=result[2]
            if len(state)>=4:
                result[3]=(state[3]-self.fourth_rule[3*pv+pz])%3
            if len(state)>=5:
                result[4]=(state[4]-fifth[3*pz+result[3]])%3
        else:
            raise ValueError("generator must be A or B")
        return tuple(result)


@dataclass(frozen=True)
class VoltageStep:
    source:Vertex
    target:Vertex
    parameter:int
    direction:int
    voltage:int


@dataclass(frozen=True)
class CycleObstruction:
    start:Vertex
    end:Vertex
    first_path:tuple[VoltageStep,...]
    second_path:tuple[VoltageStep,...]
    first_voltage:int
    second_voltage:int

    def verify(self,p:ZeroTraceParameters,q2:tuple[int,...])->bool:
        _rule(q2)
        if self.first_voltage==self.second_voltage:return False

        def path(steps):
            point=self.start
            value=0
            for edge in steps:
                if edge.source!=point or edge.direction not in (-1,1) or (
                        type(edge.parameter) is not int or edge.parameter not in F3):
                    return None
                if edge.direction==1:
                    old=point
                    dest=p.induced_B(old,edge.parameter)
                    updated=p.lower_symmetry(old)
                    voltage=(q2[3*updated[1]+updated[2]]-
                             q2[3*old[1]+old[2]])%3
                else:
                    old=p.inverse_B(point,edge.parameter)
                    dest=old
                    updated=p.lower_symmetry(old)
                    voltage=(q2[3*old[1]+old[2]]-
                             q2[3*updated[1]+updated[2]])%3
                if edge.target!=dest or edge.voltage!=voltage:
                    return None
                point=dest
                value=(value+voltage)%3
            return point,value
        return path(self.first_path)==(self.end,self.first_voltage) and (
            path(self.second_path)==(self.end,self.second_voltage))


def _adjacency(p:ZeroTraceParameters):
    graph={v:[] for v in VERTICES}
    for u,v,z,y in product(F3,repeat=4):
        start=(v,z,y)
        dest=p.induced_B(start,u)
        shifted=p.lower_symmetry(start)
        coefficients=[0]*9
        coefficients[3*shifted[1]+shifted[2]]+=1
        coefficients[3*z+y]-=1
        vec=tuple(a%3 for a in coefficients)
        graph[start].append((dest,u,1,vec))
        graph[dest].append((start,u,-1,tuple((-a)%3 for a in vec)))
    return graph


@dataclass(frozen=True)
class LinearCertificate:
    rank:int
    component_count:int
    coupling_basis:tuple[tuple[int,...],...]
    component_index:tuple[int,...]
    path_vectors:tuple[tuple[int,...],...]


@lru_cache(maxsize=256)
def linear_certificate(p:ZeroTraceParameters)->LinearCertificate:
    graph=_adjacency(p)
    components={}
    paths={}
    constraints=[]
    roots=[]
    for root in VERTICES:
        if root in paths:continue
        group=len(roots)
        roots.append(root)
        paths[root]=(0,)*9
        components[root]=group
        todo=deque([root])
        while todo:
            s=todo.popleft()
            for target,_,_,vec in graph[s]:
                proposed=tuple((a+b)%3 for a,b in zip(paths[s],vec))
                if target in paths:
                    assert components[target]==group
                    constraints.append(tuple((a-b)%3 for a,b in
                                             zip(proposed,paths[target])))
                else:
                    paths[target]=proposed
                    components[target]=group
                    todo.append(target)
    rank,basis=_basis(constraints)
    return LinearCertificate(
        rank,len(roots),basis,
        tuple(components[s] for s in VERTICES),
        tuple(paths[s] for s in VERTICES))


def _trace(p:ZeroTraceParameters,correction:tuple[int,...])->tuple[int,...]:
    return tuple(_trace_one(p,correction,start) for start in VERTICES)


def _trace_one(p:ZeroTraceParameters,correction:tuple[int,...],start:Vertex)->int:
    node=start
    total=0
    for _ in F3:
        total=(total+correction[INDEX[node]])%3
        node=p.lower_symmetry(node)
    if node!=start:
        raise AssertionError("zero-trace lower symmetry is not order three")
    return total


def _gauge_vectors(cert:LinearCertificate)->tuple[tuple[int,...],...]:
    return tuple(tuple(int(k==j) for k in cert.component_index)
                 for j in range(cert.component_count))


def _normalized_values(cert:LinearCertificate,q2:tuple[int,...])->tuple[int,...]:
    return tuple(sum(a*b for a,b in zip(vec,q2))%3 for vec in cert.path_vectors)


def trace_ranks(p:ZeroTraceParameters)->tuple[int,int]:
    cert=linear_certificate(p)
    gauge=_gauge_vectors(cert)
    correction=tuple(_normalized_values(cert,q) for q in cert.coupling_basis)
    grank=_rank([_trace(p,b) for b in gauge],27)
    combined=_rank([_trace(p,b) for b in gauge+correction],27)
    return grank,combined-grank


def solve(p:ZeroTraceParameters,q2:tuple[int,...]
          )->tuple[tuple[int,...]|None,CycleObstruction|None]:
    _rule(q2)
    graph=_adjacency(p)
    assigned={}
    for root in VERTICES:
        if root in assigned:continue
        assigned[root]=0
        parents={root:None}
        todo=deque([root])
        def path(vertex):
            edges=[]
            while parents[vertex] is not None:
                previous,edge=parents[vertex]
                edges.append(edge)
                vertex=previous
            return tuple(reversed(edges))
        while todo:
            s=todo.popleft()
            for dest,u,direction,vec in graph[s]:
                voltage=sum(a*b for a,b in zip(vec,q2))%3
                target=(assigned[s]+voltage)%3
                edge=VoltageStep(s,dest,u,direction,voltage)
                if dest in assigned:
                    if assigned[dest]!=target:
                        cert=CycleObstruction(
                            root,dest,path(dest),path(s)+(edge,),
                            assigned[dest],target)
                        if not cert.verify(p,q2):
                            raise AssertionError("signed-cycle witness did not replay")
                        return None,cert
                else:
                    assigned[dest]=target
                    parents[dest]=(s,edge)
                    todo.append(dest)
    return tuple(assigned[v] for v in VERTICES),None


@dataclass(frozen=True)
class LiftClassification:
    status:str
    rank:int
    component_count:int
    admitted_tables:int
    possible_orders:tuple[int,...]
    obstruction:CycleObstruction|None


def classify(p:ZeroTraceParameters,q2:tuple[int,...])->LiftClassification:
    _rule(q2)
    linear=linear_certificate(p)
    L,obstruction=solve(p,q2)
    if L is None:
        return LiftClassification("SIGNED_CYCLE_OBSTRUCTION",linear.rank,
                                  linear.component_count,3**(9-linear.rank),
                                  (),obstruction)
    # Each connected component contributes an independently chosen constant.
    opts=set()
    for constants in product(F3,repeat=linear.component_count):
        adjusted=tuple((value+constants[linear.component_index[j]])%3
                       for j,value in enumerate(L))
        opts.add(3 if all(t==0 for t in _trace(p,adjusted)) else 9)
    return LiftClassification("ADMITTED_POINTED_LIFT",linear.rank,
                              linear.component_count,3**(9-linear.rank),
                              tuple(sorted(opts)),None)


@dataclass(frozen=True)
class ZeroTraceLift:
    """An EXACT selected correction with its separate, proven cyclic order."""
    parameters:ZeroTraceParameters
    fifth:tuple[int,...]
    correction:tuple[int,...]
    order:int

    def __post_init__(self):
        _rule(self.fifth)
        if type(self.correction) is not tuple or len(self.correction)!=27:
            raise ValueError("requires all 27 exact correction values")
        for x in self.correction:_field(x)
        if self.order not in (3,9):
            raise ValueError("supported cyclic orders are three and nine")
        for u,s in product(F3,VERTICES):
            dest=self.parameters.induced_B(s,u)
            shifted=self.parameters.lower_symmetry(s)
            diff=(self.fifth[3*shifted[1]+shifted[2]]-
                  self.fifth[3*s[1]+s[2]])%3
            if (self.correction[INDEX[dest]]-self.correction[INDEX[s]])%3!=diff:
                raise ValueError("correction fails the cohomological equation")
        trace=_trace(self.parameters,self.correction)
        actual=3 if all(t==0 for t in trace) else 9
        if actual!=self.order:
            raise ValueError("claimed cyclic order disagrees with exact trace")

    def step(self,x:State,generator:str)->State:
        return self.parameters.step(x,generator,self.fifth)

    def inverse(self,x:State,generator:str)->State:
        return self.parameters.inverse(x,generator,self.fifth)

    def centralizer(self,x:State)->State:
        _state(x)
        result=list(x)
        v,z=x[1:3]
        w=(z+self.parameters.alpha[v])%3
        result[2]=(z+1)%3
        if len(x)>=4:
            result[3]=(x[3]+self.parameters.quotient[w]-
                       self.parameters.quotient[0])%3
        if len(x)>=5:
            result[4]=(x[4]+self.correction[INDEX[(v,z,x[3])]])%3
        return tuple(result)

    def power(self,x:State,exponent:int)->State:
        _state(x)
        if type(exponent) is not int or not 0<=exponent<self.order:
            raise ValueError("exponent is outside the proved cyclic order")
        for _ in range(exponent):
            x=self.centralizer(x)
        return x


def select_lift(p:ZeroTraceParameters,q2:tuple[int,...],
                desired_order:int)->ZeroTraceLift:
    _rule(q2)
    if type(desired_order) is not int or desired_order not in (3,9):
        raise ValueError("choose exact cyclic order three or nine")
    base,obstruction=solve(p,q2)
    if obstruction is not None or base is None:
        raise ValueError("voltage cycle obstructs this additive extension")
    structure=linear_certificate(p)
    for constants in product(F3,repeat=structure.component_count):
        adjusted=tuple((a+constants[structure.component_index[i]])%3
                       for i,a in enumerate(base))
        actual=3 if not any(_trace(p,adjusted)) else 9
        if actual==desired_order:
            return ZeroTraceLift(p,q2,adjusted,actual)
    raise ValueError("requested cyclic order cannot be realized")


@dataclass(frozen=True)
class PointedSystem:
    system:ZeroTraceLift
    mark:State

    def __post_init__(self):
        if type(self.mark) is not tuple or len(self.mark)!=5:
            raise ValueError("the distinguished point must have five coordinates")
        for a in self.mark:_field(a)


@dataclass(frozen=True)
class PointedConjugacy:
    source:PointedSystem
    target:PointedSystem
    exponents:tuple[int,...]

    def __post_init__(self):
        if not self.exponents or self.source.system!=self.target.system:
            raise ValueError("conjugacy must retain the chosen corrected system")
        order=self.source.system.order
        if any(type(e) is not int or not 0<=e<order for e in self.exponents):
            raise ValueError("unproved exponent in witness factor list")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("distinguished point was not transported")

    def map_state(self,x:State)->State:
        for exponent in self.exponents:
            x=self.source.system.power(x,exponent)
        return x

    def inverse(self)->"PointedConjugacy":
        order=self.source.system.order
        return PointedConjugacy(self.target,self.source,
                  tuple((-n)%order for n in reversed(self.exponents)))

    def then(self,after:"PointedConjugacy")->"PointedConjugacy":
        if self.target!=after.source:
            raise ValueError("different intermediate pointed objects")
        return PointedConjugacy(self.source,after.target,
                                self.exponents+after.exponents)


def transport_point(source:PointedSystem,exponent:int=1)->PointedConjugacy:
    target=PointedSystem(source.system,
                         source.system.power(source.mark,exponent))
    return PointedConjugacy(source,target,(exponent,))


@dataclass(frozen=True)
class FamilyCertificate:
    status:str
    configurations:int
    graph_components:tuple[tuple[int,int],...]
    rank_histogram:tuple[tuple[int,int,int],...]
    admitted_combinations:int
    order_three_possible:int
    order_nine_possible:int
    both_orders_possible:int
    nontrivial_gauge_cases:int


def certify_zero_trace_family()->FamilyCertificate:
    histogram=Counter()
    component_count=Counter()
    totals=Counter()
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            if sum(Q)%3:continue
            for j,k in product(F3,repeat=2):
                p=ZeroTraceParameters(gain,Q,(0,j,k))
                cert=linear_certificate(p)
                gauge_rank,relative_rank=trace_ranks(p)
                histogram[(cert.component_count,cert.rank)]+=1
                component_count[cert.component_count]+=1
                n=3**(9-cert.rank)
                m=n//3**relative_rank
                totals["admitted"]+=n
                totals["order3"]+=m
                totals["order9"]+=(n if gauge_rank else n-m)
                totals["both"]+=(m if gauge_rank else 0)
                totals["nontrivial_gauge"]+=int(gauge_rank>0)
                # A zero-coupling extension must always be compatible.
                q2=ZERO
                values,obstruction=solve(p,q2)
                if obstruction is not None or values is None:
                    raise AssertionError("zero coupling is not liftable")
    expected_hist=Counter({
        (1,3):12,(1,4):24,(1,5):36,(1,6):72,
        (3,3):2,(3,4):4,(3,5):4,(3,6):8,
    })
    expected=(162,22410,11106,12492,1188,12)
    actual=(sum(histogram.values()),totals["admitted"],totals["order3"],
            totals["order9"],totals["both"],totals["nontrivial_gauge"])
    return FamilyCertificate(
        "CLOSED_ZERO_TRACE_COHOMOLOGICAL_ORDER_CLASSIFICATION"
        if (histogram==expected_hist and actual==expected) else
        "OPEN_CLASSIFICATION_COUNTS",
        sum(histogram.values()),tuple(sorted(component_count.items())),
        tuple((c,r,n) for (c,r),n in sorted(histogram.items())),
        totals["admitted"],totals["order3"],totals["order9"],
        totals["both"],totals["nontrivial_gauge"])
