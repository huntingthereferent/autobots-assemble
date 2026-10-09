"""Fifth-coordinate centralizer lifts while varying the fourth-coordinate law.

The two prior nonconstant q0 systems have phi(v,z)=z+alpha(v).
Admit every q1(v,z)=Q(phi(v,z))+k(v), with k(0)=0, subject to
sum(Q) != 0. This gives 162 preceding ORDER-NINE systems per gain.
The canonical commuting transformation changes z by +1 and y by
h(phi)=Q(phi)-Q(0). Add any nine-entry q2(z,y) into coordinate x4.

A fiber-additive x4 correction L(v,z,y) exists iff its exact 27-state
voltage equation is consistent. Row-reduction gives 324 admission
spaces (both gains), whose constraint ranks are 5, 6 or 7.
All admitted extensions retain exact order NINE; this is proved
by checking linear basis vectors and all 27 lower states, not by
assuming that nine-turn closure survives another coordinate.
The obstruction is a literal signed-cycle witness.

Only the specified additive triangular centralizer maps are classified.
Other state automorphisms and broader couplings remain unknown.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from .fifth_coordinate_lift import BASE
from .nonconstant_drift import solve_potential
from .window_two import WindowProcess

F3=(0,1,2)
ZERO=(0,)*9
State=tuple[int,...]
Vertex=tuple[int,int,int]


def _field(x:int)->None:
    if type(x) is not int or x not in F3:
        raise ValueError("expected an F3 element")


def _triple(t:tuple[int,...])->None:
    if type(t) is not tuple or len(t)!=3:
        raise ValueError("expected a three-element tuple")
    for x in t:_field(x)


def _table(t:tuple[int,...])->None:
    if type(t) is not tuple or len(t)!=9:
        raise ValueError("expected a nine-entry coupling table")
    for x in t:_field(x)


def _state(x:State)->None:
    if type(x) is not tuple or len(x)<3:
        raise ValueError("expected dimension >=3")
    for a in x:_field(a)


@dataclass(frozen=True)
class FourthCoordinateParameters:
    gain:int
    quotient:tuple[int,int,int]
    offsets:tuple[int,int,int]

    def __post_init__(self):
        if type(self.gain) is not int or self.gain not in (1,2):
            raise ValueError("the two admitted gains are one and two")
        _triple(self.quotient)
        _triple(self.offsets)
        if self.offsets[0]!=0:
            raise ValueError("normalize the first row offset to zero")
        if sum(self.quotient)%3==0:
            raise ValueError("this movement requires a witnessed order-nine base")

    @property
    def alpha(self)->tuple[int,int,int]:
        potential=solve_potential(BASE[self.gain],self.gain)
        if potential is None or potential.drift!=1:
            raise AssertionError("missing preceding nonconstant lower proof")
        return potential.alpha

    @property
    def fourth_rule(self)->tuple[int,...]:
        a=self.alpha
        return tuple((self.quotient[(z+a[v])%3]+self.offsets[v])%3
                     for v,z in product(F3,repeat=2))

    @property
    def primitive(self)->tuple[int,int,int]:
        return tuple((q-self.quotient[0])%3 for q in self.quotient)

    def B_lower(self,node:Vertex,u:int)->Vertex:
        _field(u)
        v,z,y=node
        w=(z+self.alpha[v])%3
        return ((v+self.gain*(u+1))%3,
                (z+BASE[self.gain][3*u+v])%3,
                (y+self.quotient[w]+self.offsets[v])%3)

    def B_lower_inverse(self,node:Vertex,u:int)->Vertex:
        _field(u)
        v,z,y=node
        old_v=(v-self.gain*(u+1))%3
        old_z=(z-BASE[self.gain][3*u+old_v])%3
        old_w=(old_z+self.alpha[old_v])%3
        old_y=(y-self.quotient[old_w]-self.offsets[old_v])%3
        return old_v,old_z,old_y

    def C_lower(self,node:Vertex)->Vertex:
        v,z,y=node
        w=(z+self.alpha[v])%3
        return v,(z+1)%3,(y+self.primitive[w])%3

    def world(self,fifth:tuple[int,...])->WindowProcess:
        _table(fifth)
        return WindowProcess(self.gain,(BASE[self.gain],self.fourth_rule,fifth),(ZERO,))


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

    def validate(self,p:FourthCoordinateParameters,fifth:tuple[int,...])->bool:
        _table(fifth)
        if self.first_voltage==self.second_voltage:return False
        def follow(path):
            node=self.start
            voltage=0
            for step in path:
                if step.source!=node or step.direction not in (-1,1):
                    return None
                if type(step.parameter) is not int or step.parameter not in F3:
                    return None
                if step.direction==1:
                    predecessor=node
                    target=p.B_lower(node,step.parameter)
                    image=p.C_lower(predecessor)
                    delta=(fifth[3*image[1]+image[2]]
                           -fifth[3*predecessor[1]+predecessor[2]])%3
                else:
                    predecessor=p.B_lower_inverse(node,step.parameter)
                    target=predecessor
                    image=p.C_lower(predecessor)
                    delta=(fifth[3*predecessor[1]+predecessor[2]]
                           -fifth[3*image[1]+image[2]])%3
                if target!=step.target or delta!=step.voltage:
                    return None
                voltage=(voltage+delta)%3
                node=target
            return node,voltage
        return (follow(self.first_path)==(self.end,self.first_voltage)
                and follow(self.second_path)==(self.end,self.second_voltage))


def _edges(p:FourthCoordinateParameters):
    """B-group edges, each with symbolic voltage in the nine q2 entries."""
    adj={node:[] for node in product(F3,repeat=3)}
    for u,v,z,y in product(F3,repeat=4):
        here=(v,z,y)
        nxt=p.B_lower(here,u)
        translated=p.C_lower(here)
        difference=[0]*9
        difference[3*translated[1]+translated[2]]+=1
        difference[3*z+y]-=1
        vector=tuple(a%3 for a in difference)
        adj[here].append((nxt,u,1,vector))
        adj[nxt].append((here,u,-1,tuple((-a)%3 for a in vector)))
    return adj


def _rref(matrix:list[list[int]],n:int=9):
    rows=[[x%3 for x in row] for row in matrix if any(row)]
    pivots=[]
    head=0
    for column in range(n):
        nextrow=next((i for i in range(head,len(rows))
                      if rows[i][column]!=0),None)
        if nextrow is None:continue
        rows[head],rows[nextrow]=rows[nextrow],rows[head]
        inv=pow(rows[head][column],-1,3)
        rows[head]=[(x*inv)%3 for x in rows[head]]
        for i in range(len(rows)):
            if i!=head and rows[i][column]:
                c=rows[i][column]
                rows[i]=[(x-c*y)%3 for x,y in zip(rows[i],rows[head])]
        pivots.append(column)
        head+=1
    return rows[:head],pivots


@lru_cache(maxsize=1024)
def linear_certificate(p:FourthCoordinateParameters):
    """Exact finite elimination: rank, components, full q2 nullspace basis."""
    adj=_edges(p)
    path_vectors={}
    equations=[]
    components=0
    for root in adj:
        if root in path_vectors:continue
        components+=1
        path_vectors[root]=(0,)*9
        todo=deque([root])
        while todo:
            node=todo.popleft()
            for target,u,direction,voltage in adj[node]:
                proposed=tuple((x+y)%3 for x,y in
                               zip(path_vectors[node],voltage))
                if target in path_vectors:
                    equations.append([(x-y)%3 for x,y in
                                      zip(proposed,path_vectors[target])])
                else:
                    path_vectors[target]=proposed
                    todo.append(target)
    rows,pivots=_rref(equations)
    free=[i for i in range(9) if i not in pivots]
    basis=[]
    for j in free:
        vector=[0]*9
        vector[j]=1
        for row,i in zip(rows,pivots):
            vector[i]=(-row[j])%3
        basis.append(tuple(vector))
    return len(pivots),components,tuple(basis)


def solve_voltage(p:FourthCoordinateParameters,fifth:tuple[int,...]):
    """Return a 27-state correction or a reproducible signed-cycle witness."""
    _table(fifth)
    adj=_edges(p)
    assigned={}
    for root in adj:
        if root in assigned:continue
        assigned[root]=0
        parents={root:None}
        todo=deque([root])
        def path(node):
            result=[]
            while parents[node] is not None:
                parent,edge=parents[node]
                result.append(edge)
                node=parent
            return tuple(reversed(result))
        while todo:
            node=todo.popleft()
            for target,u,direction,vector in adj[node]:
                voltage=sum(x*y for x,y in zip(fifth,vector))%3
                new=(assigned[node]+voltage)%3
                edge=VoltageStep(node,target,u,direction,voltage)
                if target in assigned:
                    if assigned[target]!=new:
                        obstruction=CycleObstruction(
                            root,target,path(target),path(node)+(edge,),
                            assigned[target],new)
                        if not obstruction.validate(p,fifth):
                            raise AssertionError("cycle witness did not replay")
                        return None,obstruction
                else:
                    assigned[target]=new
                    parents[target]=(node,edge)
                    todo.append(target)
    return assigned,None


@dataclass(frozen=True)
class FifthCouplingAnalysis:
    status:str
    rank:int
    admitted_tables:int
    order:int|None
    correction:dict[Vertex,int]|None
    obstruction:CycleObstruction|None


def classify(p:FourthCoordinateParameters,
             fifth:tuple[int,...])->FifthCouplingAnalysis:
    rank,components,basis=linear_certificate(p)
    if components!=1:
        raise AssertionError("order-nine lower action must be connected")
    admitted=all(sum(a*b for a,b in zip(eq,fifth))%3==0
                 for eq in _rref(_constraint_rows(p))[0])
    # Independently test graph solvability, not just symbolic elimination.
    correction,witness=solve_voltage(p,fifth)
    if admitted!=(correction is not None):
        raise AssertionError("graph and exact linear constraints disagree")
    if correction is None:
        return FifthCouplingAnalysis("SIGNED_CYCLE_OBSTRUCTION",rank,3**(9-rank),
                                     None,None,witness)
    return FifthCouplingAnalysis("ORDER_NINE_POINTED_CENTRALIZER",rank,
                                 3**(9-rank),9,correction,None)


def _constraint_rows(p:FourthCoordinateParameters)->list[list[int]]:
    adj=_edges(p)
    paths={}
    equations=[]
    for root in adj:
        if root in paths:continue
        paths[root]=(0,)*9
        todo=deque([root])
        while todo:
            node=todo.popleft()
            for target,_,_,vec in adj[node]:
                proposed=tuple((x+y)%3 for x,y in zip(paths[node],vec))
                if target in paths:
                    equations.append([(x-y)%3 for x,y in
                                      zip(proposed,paths[target])])
                else:
                    paths[target]=proposed
                    todo.append(target)
    return equations


@dataclass(frozen=True)
class VariableFourthSystem:
    parameters:FourthCoordinateParameters
    fifth:tuple[int,...]

    def __post_init__(self):
        _table(self.fifth)

    @property
    def analysis(self):
        return classify(self.parameters,self.fifth)

    def step(self,x:State,label:str)->State:
        return self.parameters.world(self.fifth).step(x,label)

    def inverse(self,x:State,label:str)->State:
        return self.parameters.world(self.fifth).inverse(x,label)

    def centralizer(self,x:State)->State:
        _state(x)
        correction=self.analysis.correction
        if correction is None:
            raise ValueError("a signed-cycle obstruction forbids this lift")
        v,z=x[1:3]
        if len(x)>=4:y=x[3]
        w=(z+self.parameters.alpha[v])%3
        out=list(x)
        out[2]=(z+1)%3
        if len(x)>=4:
            out[3]=(x[3]+self.parameters.primitive[w])%3
        if len(x)>=5:
            out[4]=(x[4]+correction[(v,z,y)])%3
        return tuple(out)

    def power(self,x:State,exponent:int)->State:
        _state(x)
        if type(exponent) is not int or exponent not in range(9):
            raise ValueError("exponent must use the proved order nine")
        for _ in range(exponent):
            x=self.centralizer(x)
        return x


@dataclass(frozen=True)
class DistinguishedSystem:
    system:VariableFourthSystem
    mark:State

    def __post_init__(self):
        if type(self.mark) is not tuple or len(self.mark)!=5:
            raise ValueError("the coherent mark requires five coordinates")
        for x in self.mark:_field(x)


@dataclass(frozen=True)
class PointedConjugacy:
    source:DistinguishedSystem
    target:DistinguishedSystem
    exponents:tuple[int,...]

    def __post_init__(self):
        if not self.exponents or self.source.system!=self.target.system:
            raise ValueError("pointed systems and factor record must match")
        if any(type(n) is not int or n not in range(9) for n in self.exponents):
            raise ValueError("only witnessed powers zero through eight")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("the map does not transport the distinguished point")

    def map_state(self,x:State)->State:
        for n in self.exponents:
            x=self.source.system.power(x,n)
        return x

    def inverse(self)->"PointedConjugacy":
        return PointedConjugacy(self.target,self.source,
                                tuple((-n)%9 for n in reversed(self.exponents)))

    def then(self,after:"PointedConjugacy")->"PointedConjugacy":
        if self.target!=after.source:
            raise ValueError("distinct intermediate pointed systems")
        return PointedConjugacy(self.source,after.target,
                                self.exponents+after.exponents)


def transport_point(source:DistinguishedSystem,exponent:int=1)->PointedConjugacy:
    return PointedConjugacy(
        source,DistinguishedSystem(source.system,
                    source.system.power(source.mark,exponent)),(exponent,))


@dataclass(frozen=True)
class FamilyCertificate:
    status:str
    fourth_coordinate_configurations:int
    rank_histogram:tuple[tuple[int,int],...]
    admitted_fifth_combinations:int
    verified_basis_vectors:int
    nontrivial_fourth_dependence_at_rank7:int
    order27_counterexamples:int


def certify_order_nine_family()->FamilyCertificate:
    """Exhaust all Q, row offsets and both gains, proving all q2 via bases.

    Each admissible q2 is a linear combination of exact nullspace vectors.
    The 27-state potential is linear in q2 modulo a global constant.
    Nine copies of any constant vanish, so checking the basis vectors
    proves nine-turn closure for EVERY admitted coupling.
    """
    ranks=Counter()
    checked=0
    rank7_dependence=0
    order27=0
    admitted=0
    configurations=0
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            if sum(Q)%3==0:continue
            for j,k in product(F3,repeat=2):
                p=FourthCoordinateParameters(gain,Q,(0,j,k))
                rank,components,basis=linear_certificate(p)
                if components!=1:
                    raise AssertionError("unconnected order-nine base graph")
                configurations+=1
                ranks[rank]+=1
                admitted+=3**len(basis)
                for q2 in basis:
                    L,obstruction=solve_voltage(p,q2)
                    if obstruction is not None or L is None:
                        raise AssertionError("basis vector was obstructed")
                    checked+=1
                    if rank==7 and any(q2[3*z+y]!=q2[3*z]
                                       for z,y in product(F3,repeat=2)):
                        rank7_dependence+=1
                    for start in product(F3,repeat=3):
                        node=start
                        displacement=0
                        for _ in range(9):
                            displacement=(displacement+L[node])%3
                            node=p.C_lower(node)
                        if node!=start:
                            raise AssertionError("previous order-nine map broke")
                        if displacement!=0:
                            order27+=1
    correct=(configurations==324 and
             ranks==Counter({5:60,6:48,7:216}) and
             admitted==8100 and checked==816 and
             rank7_dependence==0 and order27==0)
    return FamilyCertificate(
        "EXACT_VARIABLE_FOURTH_ORDER_NINE_CLASSIFICATION" if correct
        else "OPEN_CERTIFICATE_COUNTS",configurations,
        tuple(sorted(ranks.items())),admitted,checked,
        rank7_dependence,order27)
