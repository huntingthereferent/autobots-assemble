"""Engine 2: native B^n continuation in an explicitly bounded 2-input F3 window.

This is a local research experiment and is not a general ARC solver.
The WATCH carrier is the B-invariant fiber x0=0 inside F3^5. The full
space F3^5 has a different earliest distinguishing power (3, not 9).

Worlds use the declared triangular window law:
    B1 += (x0 + 1)
    B2 += q0(x0,x1)
    B3 += q1(x1,x2)
    B4 += 0
All increments read PRE-MOVE coordinates. Inverse is triangular.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from itertools import product
from collections import Counter
from typing import Literal

F3 = (0,1,2)
State = tuple[int,int,int,int,int]
Table = tuple[int, ...]
FIBER = tuple((0, *coords) for coords in product(F3, repeat=4))
FULL = tuple(product(F3, repeat=5))
CARRY_2: Table = tuple(int(right==2) for left,right in product(F3,repeat=2))
CARRY_3: Table = tuple(int(left==2 and right==2) for left,right in product(F3,repeat=2))
ZERO: Table = (0,)*9
DOUBLE_CARRY_3: Table = tuple((2*v)%3 for v in CARRY_3)


@dataclass(frozen=True)
class WindowLaw:
    q0: Table
    q1: Table
    name: str

    def __post_init__(self) -> None:
        for table in (self.q0,self.q1):
            if len(table)!=9 or any(type(v) is not int or v not in F3 for v in table):
                raise ValueError('a two-input F3 window has exactly nine F3 entries')

    def step(self, state: State, action: Literal['A','B']) -> State:
        if len(state)!=5 or any(type(v) is not int or v not in F3 for v in state):
            raise ValueError('state must be F3^5')
        u,v,z,y,t=state
        if action=='A': return ((u+1)%3,v,z,y,t)
        if action!='B': raise ValueError('only A and B')
        return (u,(v+u+1)%3,(z+self.q0[3*u+v])%3,
                (y+self.q1[3*v+z])%3,t)

    def inverse(self, state: State, action: Literal['A','B']) -> State:
        if len(state)!=5 or any(type(v) is not int or v not in F3 for v in state):
            raise ValueError('state must be F3^5')
        u,v,z,y,t=state
        if action=='A': return ((u-1)%3,v,z,y,t)
        if action!='B': raise ValueError('only A and B')
        before_v=(v-u-1)%3
        before_z=(z-self.q0[3*u+before_v])%3
        before_y=(y-self.q1[3*before_v+before_z])%3
        return (u,before_v,before_z,before_y,t)

    def power(self, state: State, n: int) -> State:
        if type(n) is not int or n<0: raise ValueError('nonnegative integer power required')
        for _ in range(n): state=self.step(state,'B')
        return state


WORLD_9 = WindowLaw(CARRY_2, ZERO, 'nine-turn lower carry; no third carry')
WORLD_27 = WindowLaw(CARRY_2, CARRY_3, 'nine-turn lower carry; nonzero third carry')
WORLD_27_SCALED = WindowLaw(CARRY_2, DOUBLE_CARRY_3, 'scaled third carry')


def verified_b_fiber(law: WindowLaw, fiber: tuple[State, ...]) -> bool:
    return all(law.step(x,'B') in fiber for x in fiber)


def cycles(law: WindowLaw, fiber: tuple[State, ...] = FIBER):
    remaining=set(fiber)
    result=[]
    while remaining:
        root=min(remaining)
        path=[]
        current=root
        while current not in path:
            if current not in remaining:
                raise AssertionError('cycle left the remaining invariant permutation carrier')
            path.append(current)
            current=law.step(current,'B')
        if current!=root:
            raise AssertionError('finite invertible map cycle must return to root')
        remaining.difference_update(path)
        result.append(tuple(path))
    return tuple(result)


def build_b_conjugacy(left: WindowLaw, right: WindowLaw, fiber=FIBER):
    """Only when the full B-cycle inventories agree. Verify literal all-edge square."""
    left_cycles=sorted(cycles(left,fiber),key=lambda c:(len(c),c[0]))
    right_cycles=sorted(cycles(right,fiber),key=lambda c:(len(c),c[0]))
    if tuple(map(len,left_cycles))!=tuple(map(len,right_cycles)):
        return None
    map_={}
    for lcycle,rcycle in zip(left_cycles,right_cycles):
        map_.update(zip(lcycle,rcycle))
    if len(set(map_.values()))!=len(fiber):
        raise AssertionError('cycle map is not a bijection')
    if not all(map_[left.step(x,'B')]==right.step(map_[x],'B') for x in fiber):
        raise AssertionError('the constructed B-conjugacy does not intertwine B')
    return map_


@dataclass(frozen=True)
class Observation:
    n: int
    left_fixed: int
    right_fixed: int
    left_origin: State
    right_origin: State
    left_fixed_states: tuple[State,...]
    right_fixed_states: tuple[State,...]
    native_relation: str = 'Fix(B^n) on the declared B-invariant fiber'

    @property
    def differs(self):
        return self.left_fixed != self.right_fixed


@dataclass(frozen=True)
class ResearchLedger:
    source: WindowLaw
    target: WindowLaw
    carrier: tuple[State,...]
    native_operation: str
    observations: tuple[Observation,...]
    status: str
    conclusion: str
    budget: int
    simultaneous_A_B: str = 'UNKNOWN: fiber is not A-invariant; B-only investigation'

    def compact(self):
        return {
            'status': self.status,
            'conclusion': self.conclusion,
            'carrier_size':len(self.carrier),
            'carrier_constraint':'x0=0, preserved by B; not by A',
            'source':{'name':self.source.name,'q0':self.source.q0,'q1':self.source.q1},
            'target':{'name':self.target.name,'q0':self.target.q0,'q1':self.target.q1},
            'operation':self.native_operation,
            'budget':self.budget,
            'witnesses':[{'power':o.n,'left_fixed':o.left_fixed,'right_fixed':o.right_fixed,
                          'root_left':o.left_origin,'root_right':o.right_origin,
                          'is_distinguishing':o.differs} for o in self.observations],
            'simultaneous_A_B':self.simultaneous_A_B,
        }


def continue_native(left:WindowLaw,right:WindowLaw,
                    max_n:int,carrier=FIBER)->ResearchLedger:
    if type(max_n) is not int or max_n<1:
        raise ValueError('positive observation budget required')
    if not carrier or len(set(carrier))!=len(carrier):
        raise ValueError('nonempty distinct carrier states required')
    if not all(verified_b_fiber(law,carrier) for law in (left,right)):
        raise ValueError('the WATCH space must be B-invariant for BOTH worlds')
    observations=[]
    left_states=list(carrier)
    right_states=list(carrier)
    idx=carrier.index((0,0,0,0,0)) if (0,0,0,0,0) in carrier else 0
    for n in range(1,max_n+1):
        # Each pass applies the same B to the previous pass's actual states.
        left_states=[left.step(x,'B') for x in left_states]
        right_states=[right.step(x,'B') for x in right_states]
        lf=tuple(s for s,a in zip(carrier,left_states) if s==a)
        rf=tuple(s for s,a in zip(carrier,right_states) if s==a)
        obs=Observation(n,len(lf),len(rf),left_states[idx],right_states[idx],lf,rf)
        observations.append(obs)
        if obs.differs:
            return ResearchLedger(left,right,carrier,'B successive composition',
                         tuple(observations),'DISTINGUISHED_B_ACTIONS',
                         f'Fix(B^{n}) cardinalities differ: no B-preserving bijection',max_n)
        # Positive stopping condition: the complete B action has returned in
        # both worlds, and every previous fixed-point observation agrees.
        if len(lf)==len(carrier) and len(rf)==len(carrier):
            conjugacy=build_b_conjugacy(left,right,carrier)
            if conjugacy is None: raise AssertionError('cycle inventory mismatch after identical Fix counts')
            return ResearchLedger(left,right,carrier,'B successive composition',
                         tuple(observations),'B_ONLY_CONJUGACY_WITNESSED',
                         f'both B^{n} are identity; explicit {len(conjugacy)}-state bijection intertwines B',max_n)
    return ResearchLedger(left,right,carrier,'B successive composition',
                         tuple(observations),'UNKNOWN_BUDGET',
                         'no invariant distinction yet; no full-cycle witness; must not infer equivalence',max_n)


def record_experiment():
    left,right=WORLD_9,WORLD_27
    for world in (left,right,WORLD_27_SCALED):
        for s in FULL:
            for a in 'AB':
                assert world.inverse(world.step(s,a),a)==s
        assert verified_b_fiber(world,FIBER)
    early=continue_native(left,right,8)
    decisive=continue_native(left,right,9)
    final=continue_native(left,right,27)
    positive=continue_native(right,WORLD_27_SCALED,27)
    assert early.status=='UNKNOWN_BUDGET'
    assert decisive.status=='DISTINGUISHED_B_ACTIONS'
    assert final.status=='DISTINGUISHED_B_ACTIONS'
    assert positive.status=='B_ONLY_CONJUGACY_WITNESSED'
    return {
        'scope':'two-input triangular window law on F3^5; B-invariant x0=0 fiber',
        'fiber':{'cardinality':len(FIBER),
                 'B_cycles_world_9':dict(Counter(map(len,cycles(left)))),
                 'B_cycles_world_27':dict(Counter(map(len,cycles(right))))},
        'prefix_budget_eight':early.compact(),
        'first_distinction':decisive.compact(),
        'positive_control':positive.compact(),
        'full_carrier_qualification':{
            'full_states':len(FULL),
            'first_divergence':next(n for n in range(1,28)
                if sum(left.power(s,n)==s for s in FULL)!=
                   sum(right.power(s,n)==s for s in FULL)),
            'warning':'Do not promote the fiber n=9 first distinction to full F3^5; full carrier distinguishes at n=3.'
        },
        'report':'a native B-continuation; not an autonomous grammar selector or universal ARC result',
    }

if __name__=='__main__':
    import json
    print(json.dumps(record_experiment(),indent=2))