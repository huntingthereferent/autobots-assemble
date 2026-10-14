"""A/B root transport: certified marked-boundary process alignment.

This extends the comparison of eventually periodic F3 coupling-rule streams.
The carried gauge is a boundary datum: it is not, by itself, a conjugacy of
newly re-rooted ordinary A/B worlds whose x1 remains fixed.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import lcm

from .process_alignment import (
    Rule, PeriodicProcess as Process, next_scales,
    IDENTITY, NEGATIVE, NONLINEAR, ZERO,
)

@dataclass(frozen=True)
class Witness:
    status:str
    incoming:int
    head:tuple[int,...]=()
    period:tuple[int,...]=()
    first_failure_depth:int|None=None
    checked_phase_states:int=0
    def scale(self,index:int)->int:
        if self.status!='ALIGNED' or index<0:raise ValueError('no scale')
        if index<len(self.head):return self.head[index]
        return self.period[(index-len(self.head))%len(self.period)]

def verify(p:Process,q:Process,w:Witness)->bool:
    if w.status!='ALIGNED' or not w.period or w.incoming not in (1,2):return False
    start=max(len(p.stem),len(q.stem),len(w.head)+1)
    period=lcm(len(p.period),len(q.period),len(w.period))
    for i in range(start+period):
        prev=w.incoming if i==0 else w.scale(i-1)
        if w.scale(i) not in next_scales(p.rule(i),q.rule(i),prev):return False
    return (p.rule(start)==p.rule(start+period) and q.rule(start)==q.rule(start+period)
            and w.scale(start-1)==w.scale(start+period-1)
            and w.scale(start)==w.scale(start+period))

def find(p:Process,q:Process,incoming:int=1)->Witness:
    if type(incoming)!=int or incoming not in (1,2):raise ValueError('invalid root mark')
    stem=max(len(p.stem),len(q.stem))
    period=lcm(len(p.period),len(q.period))
    nodes={(phase,prior) for phase in range(period) for prior in (1,2)}
    def outgoing(node):
        phase,prior=node
        return tuple((((phase+1)%period,s),s) for s in next_scales(
                p.rule(stem+phase),q.rule(stem+phase),prior))
    safe=set(nodes)
    while True:
        nxt={x for x in safe if any(y in safe for y,_ in outgoing(x))}
        if nxt==safe:break
        safe=nxt
    paths={incoming:()}
    for i in range(stem):
        new={}
        for prior,head in sorted(paths.items()):
            for s in next_scales(p.rule(i),q.rule(i),prior):new.setdefault(s,head+(s,))
        paths=new
        if not paths:return Witness('OPEN',incoming,first_failure_depth=i+3,checked_phase_states=len(nodes))
    viable=[(prior,head) for prior,head in sorted(paths.items()) if (0,prior) in safe]
    if not viable:
        fronts={incoming}
        for i in range(stem+2*len(nodes)+2):
            nxt={s for prior in fronts for s in next_scales(p.rule(i),q.rule(i),prior)}
            if not nxt:return Witness('OPEN',incoming,first_failure_depth=i+3,checked_phase_states=len(nodes))
            fronts=nxt
        raise AssertionError('coinductive argument inconsistent')
    prior,head=viable[0];cur=(0,prior);seen={};tail=[]
    while cur not in seen:
        seen[cur]=len(tail)
        successor,scale=next((n,s) for n,s in outgoing(cur) if n in safe)
        tail.append(scale);cur=successor
    start=seen[cur]
    result=Witness('ALIGNED',incoming,head+tuple(tail[:start]),tuple(tail[start:]),checked_phase_states=len(nodes))
    assert verify(p,q,result)
    return result

def transport(p:Process,q:Process,w:Witness,turns:int=1)->Witness:
    """Carry the scalar on the removed input boundary, never reset to 1."""
    if type(turns)!=int or turns<0 or not verify(p,q,w):
        raise ValueError('transport requires a verified alignment and nonnegative turn count')
    incoming=w.incoming if turns==0 else w.scale(turns-1)
    t=find(p.shift(turns),q.shift(turns),incoming)
    if t.status!='ALIGNED':raise AssertionError('transport must preserve the recurrence')
    # Coinductive transport is exact: the tail of a verified witness satisfies
    # the same coupling equations, but with its previous scalar carried to
    # the new boundary. This rechecks the shifted lasso, not a finite prefix.
    if not verify(p.shift(turns),q.shift(turns),t):
        raise AssertionError('transported lasso could not be independently verified')
    return t

def classify(period:int=2,mark_free:bool=False):
    rules=tuple((0,a,b) for a,b in product(range(3),repeat=2))
    streams=tuple(Process.repeat(*rr) for rr in product(rules,repeat=period))
    groups=[];remain=list(streams)
    while remain:
        leader=remain.pop(0);part=[leader];later=[]
        for other in remain:
            yes=any(find(leader,other,inc).status=='ALIGNED'
                    for inc in ((1,2) if mark_free else (1,)))
            (part if yes else later).append(other)
        groups.append(tuple(part));remain=later
    return streams,tuple(groups)

@dataclass(frozen=True)
class MarkedWorld:
    """A rooted A/B system with a movable, explicit boundary input unit.

    B x1 = x1 + gain*(x0+1). This is a NEW marked-root system:
    when gain != 1 it is not the old ordinary rooted process.
    """
    process:Process
    gain:int=1
    def __post_init__(self):
        if type(self.gain)!=int or self.gain not in (1,2):
            raise ValueError('invalid boundary unit')
    def step(self,state:tuple[int,...],action:str)->tuple[int,...]:
        if len(state)<3 or any(type(v)!=int or v not in (0,1,2) for v in state):
            raise ValueError('invalid full state')
        y=list(state)
        if action=='A':y[0]=(state[0]+1)%3
        elif action=='B':
            y[1]=(state[1]+self.gain*(state[0]+1))%3
            for i in range(2,len(state)):
                y[i]=(state[i]+self.process.rule(i-2)[state[i-1]])%3
        else:raise ValueError('only A/B')
        return tuple(y)

def marked_map(state:tuple[int,...],cert:Witness)->tuple[int,...]:
    """F(x)=(x0,b*x1,s0*x2,...), where b is incoming gauge."""
    if cert.status!='ALIGNED' or len(state)<3:raise ValueError('alignment required')
    return (state[0],cert.incoming*state[1]%3)+tuple(
        cert.scale(i)*state[i+2]%3 for i in range(len(state)-2))

def verify_marked_pair(source:MarkedWorld,target:MarkedWorld,cert:Witness,
                       depth:int)->bool:
    """Exhaust all states for a chosen finite depth (not the all-depth theorem)."""
    if (target.gain*source.gain)%3!=cert.incoming:return False
    for state in product(range(3),repeat=depth):
        mapped=marked_map(state,cert)
        for action in 'AB':
            if marked_map(source.step(state,action),cert)!=target.step(mapped,action):
                return False
    return True

def transported_marked_worlds(p:Process,q:Process,cert:Witness,turns:int=1):
    """A coherent *new* marked-root pair after removing coupling-rule prefix.

    The source and target are re-rooted process TEMPLATES. Target's incoming
    unit is s_(turns-1), source's is 1. This transports an interface, not
    literal restriction of the original unmarked A/B state action.
    """
    if not verify(p,q,cert):raise ValueError('uncertified original relation')
    witness=transport(p,q,cert,turns)
    source=MarkedWorld(p.shift(turns),1)
    target=MarkedWorld(q.shift(turns),witness.incoming)
    return source,target,witness


def compose_witness(p:Process,q:Process,r:Process,first:Witness,second:Witness)->Witness:
    """Compose marked morphisms P->Q->R coordinatewise, including incoming mark."""
    if not verify(p,q,first) or not verify(q,r,second):
        raise ValueError('both edges need exact coinductive certificates')
    h=max(len(first.head),len(second.head))
    period=lcm(len(first.period),len(second.period))
    out=Witness('ALIGNED',first.incoming*second.incoming%3,
        tuple(first.scale(i)*second.scale(i)%3 for i in range(h)),
        tuple(first.scale(i)*second.scale(i)%3 for i in range(h,h+period)))
    if not verify(p,r,out):raise AssertionError('alignment composition violated')
    return out

def invert_witness(p:Process,q:Process,w:Witness)->Witness:
    """Reverse a marked morphism using inverse scalars (1 and 2 in F3)."""
    if not verify(p,q,w):raise ValueError('uncertified witness')
    out=Witness('ALIGNED',w.incoming,w.head,w.period)
    if not verify(q,p,out):raise AssertionError('inverse failed')
    return out
