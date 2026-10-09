"""A witness-preserving interface over BOTH proved fifth-coordinate lift families.

Mathematical objects remain distinct:
  - CouplingLaw specifies the actual triangular transformation system.
  - AdmissionCertificate says whether the prescribed additive lift exists,
    preserves a literal signed-cycle obstruction, and lists possible orders.
  - SelectedSymmetry fixes the *actual* 27-value correction and component
    constants. Same law with different corrections is NOT the same symmetry.
  - PointedSystem fixes a distinguished state. PointedConjugacy stores every
    exponent factor and demands exact mark transport.

This is an adapter for the two previously proved fixed nonconstant q0
families, all three-entry Q and normalized k, and nine-entry q2. It does
not create new coupling laws, prove universal closure, or identify points
merely because the underlying unpointed systems coincide.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Union

from .fifth_coordinate_lift import BASE
from .window_two import WindowProcess
from . import variable_fourth_lift as order_nine
from . import zero_trace_lift as order_three

F3 = (0, 1, 2)
VERTICES = tuple(product(F3, repeat=3))
INDEX = {s: i for i, s in enumerate(VERTICES)}
ZERO_TABLE = (0,) * 9
Obstruction = Union[order_three.CycleObstruction, order_nine.CycleObstruction]


def _field(value: int) -> None:
    if type(value) is not int or value not in F3:
        raise ValueError("each coordinate must be an element of F3")


def _tuple_of(values: tuple[int, ...], count: int, label: str) -> None:
    if type(values) is not tuple or len(values) != count:
        raise ValueError(f"{label} must be an explicit {count}-element tuple")
    for value in values:
        _field(value)


@dataclass(frozen=True)
class CouplingLaw:
    """One explicitly specified pair of finite-field generating transformations."""
    gain: int
    quotient: tuple[int, int, int]
    offsets: tuple[int, int, int]
    fifth: tuple[int, ...]

    def __post_init__(self) -> None:
        if type(self.gain) is not int or self.gain not in (1, 2):
            raise ValueError("only the two previously admitted lower gains apply")
        _tuple_of(self.quotient, 3, "fourth-coordinate quotient")
        _tuple_of(self.offsets, 3, "normalized fourth-coordinate offsets")
        if self.offsets[0] != 0:
            raise ValueError("the first row offset must be zero")
        _tuple_of(self.fifth, 9, "fifth-coordinate coupling")

    @property
    def lower_order(self) -> int:
        return 3 if sum(self.quotient) % 3 == 0 else 9

    @property
    def branch(self) -> str:
        return "ZERO_TRACE" if self.lower_order == 3 else "NONZERO_TRACE"

    @property
    def parameters(self) -> (order_three.ZeroTraceParameters |
                             order_nine.FourthCoordinateParameters):
        if self.lower_order == 3:
            return order_three.ZeroTraceParameters(self.gain, self.quotient,
                                                   self.offsets)
        return order_nine.FourthCoordinateParameters(self.gain, self.quotient,
                                                    self.offsets)

    @property
    def alpha(self) -> tuple[int, int, int]:
        return self.parameters.alpha

    @property
    def fourth(self) -> tuple[int, ...]:
        return self.parameters.fourth_rule

    def world(self) -> WindowProcess:
        # Finite stem with a fully specified zero infinite tail.
        return _world(self)

    def lower_symmetry(self, s: tuple[int, int, int]) -> tuple[int, int, int]:
        _tuple_of(s, 3, "lower-coordinate state")
        v,z,y=s
        w=(z+self.alpha[v])%3
        return v,(z+1)%3,(y+self.quotient[w]-self.quotient[0])%3

    def lower_generator(self, s: tuple[int, int, int],
                        u: int) -> tuple[int, int, int]:
        _tuple_of(s, 3, "lower-coordinate state")
        _field(u)
        v,z,y=s
        return ((v+self.gain*(u+1))%3,
                (z+BASE[self.gain][3*u+v])%3,
                (y+self.fourth[3*v+z])%3)


@lru_cache(maxsize=4096)
def _world(law: CouplingLaw) -> WindowProcess:
    return WindowProcess(law.gain,
                         (BASE[law.gain],law.fourth,law.fifth),
                         (ZERO_TABLE,))


@dataclass(frozen=True)
class CycleWitness:
    """Preserve the original branch's actual signed-edge certificate."""
    law: CouplingLaw
    original: Obstruction

    def verify(self) -> bool:
        if self.law.lower_order == 3:
            return (isinstance(self.original,order_three.CycleObstruction)
                    and self.original.verify(self.law.parameters,
                                             self.law.fifth))
        return (isinstance(self.original,order_nine.CycleObstruction)
                and self.original.validate(self.law.parameters,
                                           self.law.fifth))

    @property
    def endpoints(self):
        return self.original.start,self.original.end

    @property
    def path_voltage_difference(self) -> int:
        return (self.original.second_voltage -
                self.original.first_voltage) % 3


@dataclass(frozen=True)
class AdmissionCertificate:
    """Report independent properties, never a collapsed yes/no/order label."""
    law: CouplingLaw
    branch: str
    admitted: bool
    component_count: int
    constraint_rank: int
    admitted_tables_for_configuration: int
    possible_orders: tuple[int, ...]
    normalized_correction: tuple[int, ...] | None
    component_index: tuple[int, ...] | None
    obstruction: CycleWitness | None

    def __post_init__(self) -> None:
        if self.branch != self.law.branch:
            raise ValueError("branch tag must reflect the actual quotient trace")
        if self.component_count not in (1,3):
            raise ValueError("unexpected graph component count")
        if self.admitted_tables_for_configuration != 3**(9-self.constraint_rank):
            raise ValueError("admitted table count disagrees with exact rank")
        if self.admitted:
            if self.obstruction is not None or self.normalized_correction is None:
                raise ValueError("admitted correction cannot carry an obstruction")
            _tuple_of(self.normalized_correction,27,"normalized correction")
            if self.component_index is None:
                raise ValueError("a correction needs its component labels")
            if any(order not in (3,9) for order in self.possible_orders):
                raise ValueError("unsupported cyclic order")
        else:
            if (self.obstruction is None or self.normalized_correction is not None
                    or self.possible_orders):
                raise ValueError("obstructed cases require a literal cycle witness")
            if not self.obstruction.verify():
                raise ValueError("the retained signed-cycle witness does not replay")
        if self.component_index is not None:
            if type(self.component_index) is not tuple or len(self.component_index)!=27:
                raise ValueError("component labels must cover all 27 states")
            if set(self.component_index)!=set(range(self.component_count)):
                raise ValueError("component labels must be contiguous")


def inspect_coupling(law: CouplingLaw) -> AdmissionCertificate:
    """Dispatch by the *actual trace*, preserve original proof and 27 values."""
    if not isinstance(law,CouplingLaw):
        raise TypeError("provide a validated finite-field coupling law")
    p=law.parameters
    if law.lower_order==3:
        structure=order_three.linear_certificate(p)
        classified=order_three.classify(p,law.fifth)
        corrected,obstruction=order_three.solve(p,law.fifth)
        component_count=structure.component_count
        rank=structure.rank
        labels=structure.component_index
        orders=classified.possible_orders
    else:
        rank,component_count,_=order_nine.linear_certificate(p)
        classified=order_nine.classify(p,law.fifth)
        solved,obstruction=order_nine.solve_voltage(p,law.fifth)
        corrected=(tuple(solved[v] for v in VERTICES)
                   if solved is not None else None)
        labels=(0,)*27
        orders=(9,) if corrected is not None else ()
    if (corrected is None)!=(obstruction is not None):
        raise AssertionError("previous classification lost its proof boundary")
    if classified.rank!=rank:
        raise AssertionError("previous rank certificate diverged")
    if law.lower_order==3 and (
            orders != (() if corrected is None else classified.possible_orders)):
        raise AssertionError("previous possible-order certificate diverged")
    cycle=CycleWitness(law,obstruction) if obstruction is not None else None
    return AdmissionCertificate(
        law,law.branch,corrected is not None,component_count,rank,
        3**(9-rank),orders,corrected,labels,cycle)


def _corrected_lower_trace(law: CouplingLaw,
                           corrected: tuple[int, ...],
                           length: int) -> tuple[bool, tuple[int, ...]]:
    traces=[]
    complete=True
    for start in VERTICES:
        current=start
        total=0
        for _ in range(length):
            total=(total+corrected[INDEX[current]])%3
            current=law.lower_symmetry(current)
        if current!=start:
            complete=False
        traces.append(total)
    return complete,tuple(traces)


@dataclass(frozen=True)
class SelectedSymmetry:
    """The actual correction, component constants and exact cyclic order."""
    law: CouplingLaw
    correction: tuple[int, ...]
    component_constants: tuple[int, ...]
    order: int

    def __post_init__(self) -> None:
        _tuple_of(self.correction,27,"correction")
        if type(self.order) is not int or self.order not in (3,9):
            raise ValueError("only proved cyclic orders 3 and 9 can be selected")
        report=inspect_coupling(self.law)
        if not report.admitted or self.order not in report.possible_orders:
            raise ValueError("no admitted symmetry with the selected order")
        _tuple_of(self.component_constants,report.component_count,
                  "explicit correction-component constants")
        if any(
                self.correction[j]!=
                (report.normalized_correction[j]+
                 self.component_constants[report.component_index[j]])%3
                for j in range(27)):
            raise ValueError("chosen correction is not the exact witnessed gauge lift")
        for u,s in product(F3,VERTICES):
            after=self.law.lower_generator(s,u)
            moving=self.law.lower_symmetry(s)
            rhs=(self.law.fifth[3*moving[1]+moving[2]] -
                 self.law.fifth[3*s[1]+s[2]])%3
            if (self.correction[INDEX[after]] -
                    self.correction[INDEX[s]])%3!=rhs:
                raise ValueError("correction does not intertwine the second generator")
        three_closed,three_trace=_corrected_lower_trace(
            self.law,self.correction,3)
        nine_closed,nine_trace=_corrected_lower_trace(
            self.law,self.correction,9)
        if not nine_closed or any(nine_trace):
            raise ValueError("nine-turn closure was not established")
        actual=3 if three_closed and not any(three_trace) else 9
        if actual!=self.order:
            raise ValueError("claimed order does not equal the actual action order")

    @property
    def distinguished_law(self) -> CouplingLaw:
        return self.law

    def centralizer(self, state: tuple[int, ...]) -> tuple[int, ...]:
        if type(state) is not tuple or len(state)<3:
            raise ValueError("state must be a tuple of dimension >=3")
        for value in state:
            _field(value)
        result=list(state)
        v,z=state[1:3]
        w=(z+self.law.alpha[v])%3
        result[2]=(z+1)%3
        if len(result)>=4:
            result[3]=(state[3]+self.law.quotient[w]-
                       self.law.quotient[0])%3
        if len(result)>=5:
            result[4]=(state[4]+self.correction[INDEX[(v,z,state[3])]])%3
        return tuple(result)

    def power(self,state:tuple[int,...],exponent:int)->tuple[int,...]:
        if type(exponent) is not int or not 0<=exponent<self.order:
            raise ValueError("the exponent exceeds the selected exact cyclic order")
        for _ in range(exponent):
            state=self.centralizer(state)
        return state

    def step(self,state:tuple[int,...],generator:str)->tuple[int,...]:
        return self.law.world().step(state,generator)

    def inverse_step(self,state:tuple[int,...],generator:str)->tuple[int,...]:
        return self.law.world().inverse(state,generator)


def select_symmetry(law: CouplingLaw, order: int,
                    component_constants: tuple[int,...] | None=None
                    ) -> SelectedSymmetry:
    """Choose an admitted pointed-arrow generator with explicit gauge provenance.

    When constants are not specified, choose the FIRST valid tuple in
    lexicographic F3 order. Never alter the law or suppress a mismatch.
    """
    if type(order) is not int or order not in (3,9):
        raise ValueError("requested cyclic order must be three or nine")
    report=inspect_coupling(law)
    if not report.admitted:
        raise ValueError("signed-cycle obstruction: no additive commuting lift")
    if order not in report.possible_orders:
        raise ValueError("the desired cyclic order does not occur in this system")
    choices=(product(F3,repeat=report.component_count)
             if component_constants is None else (component_constants,))
    for candidate in choices:
        _tuple_of(candidate,report.component_count,"correction-component constants")
        corrected=tuple(
            (report.normalized_correction[j]+candidate[report.component_index[j]])%3
            for j in range(27))
        closed,trace=_corrected_lower_trace(law,corrected,3)
        actual=3 if closed and not any(trace) else 9
        if actual==order:
            return SelectedSymmetry(law,corrected,candidate,order)
    raise ValueError("the exact component constants do not realize the requested order")


@dataclass(frozen=True)
class PointedSystem:
    symmetry: SelectedSymmetry
    mark: tuple[int,...]

    def __post_init__(self) -> None:
        if not isinstance(self.symmetry,SelectedSymmetry):
            raise TypeError("a pointed system requires the chosen exact symmetry")
        _tuple_of(self.mark,5,"distinguished five-coordinate point")

    def at_dimension(self,dimension:int)->tuple[int,...]:
        if type(dimension) is not int or dimension<5:
            raise ValueError("the mark requires at least five coordinates")
        return self.mark+(0,)*(dimension-5)


@dataclass(frozen=True)
class PointedConjugacy:
    source: PointedSystem
    target: PointedSystem
    exponents: tuple[int,...]

    def __post_init__(self) -> None:
        if not self.exponents:
            raise ValueError("each arrow must preserve at least one literal factor")
        if self.source.symmetry!=self.target.symmetry:
            raise ValueError("different correction witnesses cannot silently compose")
        order=self.source.symmetry.order
        if type(self.exponents) is not tuple or any(
                type(n) is not int or not 0<=n<order
                for n in self.exponents):
            raise ValueError("unverified cyclic group factor")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("the distinguished source point is not carried to target")

    def map_state(self,state:tuple[int,...])->tuple[int,...]:
        for exponent in self.exponents:
            state=self.source.symmetry.power(state,exponent)
        return state

    def inverse(self) -> "PointedConjugacy":
        order=self.source.symmetry.order
        return PointedConjugacy(
            self.target,self.source,
            tuple((-n)%order for n in reversed(self.exponents)))

    def then(self,after:"PointedConjugacy")->"PointedConjugacy":
        if self.target!=after.source:
            raise ValueError("the intermediate distinguished point or symmetry differs")
        return PointedConjugacy(
            self.source,after.target,self.exponents+after.exponents)


def transport_point(source:PointedSystem, exponent:int=1)->PointedConjugacy:
    target=PointedSystem(source.symmetry,
                         source.symmetry.power(source.mark,exponent))
    return PointedConjugacy(source,target,(exponent,))


@dataclass(frozen=True)
class InterfaceFamilyReconciliation:
    fourth_coordinate_configurations: int
    zero_trace_configurations: int
    nonzero_trace_configurations: int
    admitted_coupling_combinations: int
    order_three_possible: int
    order_nine_possible: int
    both_orders_possible: int
    component_one_configurations: int
    component_three_configurations: int
    status: str


def reconcile_families() -> InterfaceFamilyReconciliation:
    """Composition of the TWO preexisting exact whole-family certificates.

    This does not enumerate all 486*19683 coupling candidates a second time.
    The individual certificates contain independent finite-basis proofs.
    """
    z=order_three.certify_zero_trace_family()
    n=order_nine.certify_order_nine_family()
    if (z.status!="CLOSED_ZERO_TRACE_COHOMOLOGICAL_ORDER_CLASSIFICATION" or
            n.status!="EXACT_VARIABLE_FOURTH_ORDER_NINE_CLASSIFICATION"):
        raise AssertionError("a predecessor family's mathematical proof is open")
    components=dict(z.graph_components)
    ans=InterfaceFamilyReconciliation(
        z.configurations+n.fourth_coordinate_configurations,
        z.configurations,n.fourth_coordinate_configurations,
        z.admitted_combinations+n.admitted_fifth_combinations,
        z.order_three_possible,
        z.order_nine_possible+n.admitted_fifth_combinations,
        z.both_orders_possible,
        components.get(1,0)+n.fourth_coordinate_configurations,
        components.get(3,0),
        "RECONCILED_POINTED_COHOMOLOGICAL_FAMILIES",
    )
    if ((ans.fourth_coordinate_configurations,
         ans.admitted_coupling_combinations,
         ans.order_three_possible,ans.order_nine_possible,
         ans.both_orders_possible,ans.component_one_configurations,
         ans.component_three_configurations) !=
            (486,30510,11106,20592,1188,468,18)):
        raise AssertionError("the two recorded mathematical families were conflated")
    return ans
