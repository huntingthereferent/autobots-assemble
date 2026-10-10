"""Engine 2 native WATCHes for the repo's 48 two-predecessor window laws.

The classified grammar is finite; rooted equivalence, unpointed full-state
conjugacy, and fixed-word obstructions remain distinct. No automatic bridge
to the independent one-input coupling grammar or the zero-trace lift.
"""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass, field
from itertools import product

F3=(0,1,2)
ORIGIN=(0,0,0)


def _shear(state,c):
    result=list(state)
    result[2]=(state[2]+c*state[1]*state[1])%3
    return tuple(result)


def _fiber(state,forward):
    u,v,z,*tail=state
    if forward:
        return (u,(v+2)%3,(z+(2 if v==1 else 0))%3,*tail)
    prior=(v+1)%3
    return (u,prior,(z-(2 if prior==1 else 0))%3,*tail)


@dataclass(frozen=True,order=True)
class Window48:
    support:int
    coefficient:int
    pulse:int
    balanced:int

    def __post_init__(self):
        if any(type(v) is not int for v in (self.support,self.coefficient,self.pulse,self.balanced)) or (
            self.support not in range(4) or self.coefficient not in F3 or
            self.pulse not in (0,1) or self.balanced not in (0,1)):
            raise ValueError("invalid 48-law window parameter")

    def rule(self)->tuple[int,...]:
        k,c,e,t=self.support,self.coefficient,self.pulse,self.balanced
        return tuple((int(u==2 and v<k)+e*int(u==0 and v==0)
            +t*(int(u==1 and v==0)-int(u==1 and v==1))
            +c*((v+u+1)**2-v**2))%3 for u,v in product(F3,repeat=2))

    def step(self,state,gen):
        if len(state)<3 or any(type(v) is not int or v not in F3 for v in state):
            raise ValueError("requires F3^d with d>=3")
        out=list(state)
        if gen=='A':out[0]=(state[0]+1)%3
        elif gen=='B':
            out[1]=(state[1]+state[0]+1)%3
            out[2]=(state[2]+self.rule()[3*state[0]+state[1]])%3
        else:raise ValueError("unknown generator")
        return tuple(out)

    def inverse(self,state,gen):
        if len(state)<3 or any(type(v) is not int or v not in F3 for v in state):
            raise ValueError("requires F3^d with d>=3")
        out=list(state)
        if gen=='A':out[0]=(state[0]-1)%3
        elif gen=='B':
            out[1]=(state[1]-state[0]-1)%3
            out[2]=(state[2]-self.rule()[3*state[0]+out[1]])%3
        else:raise ValueError("unknown generator")
        return tuple(out)

    def apply(self,state,word):
        for gen in word:state=self.step(state,gen)
        return state


def family48():
    return tuple(Window48(k,c,e,t) for k,e,t,c in product(range(4),range(2),range(2),F3))


def count_word(w,word,depth=3):
    return sum(w.apply(state,word)==state for state in product(F3,repeat=depth))


def classify(a:Window48,b:Window48):
    """Return (kind, exact map or separating word)."""
    if a.support!=b.support:return 'FULL_OBSTRUCTED','B'
    if a.pulse!=b.pulse:return 'FULL_OBSTRUCTED','BBB'
    if a.balanced!=b.balanced:
        if a.pulse==0:return 'FULL_OBSTRUCTED','AABAB'
        if a.support in (1,2):return 'FULL_OBSTRUCTED','ABABAB'
        direction=a.balanced==0
        def map_state(s):
            return _shear(_fiber(_shear(s,(-a.coefficient)%3),direction),b.coefficient)
        return 'FULL_UNROOTED',map_state
    return 'ROOTED_FULL',lambda s:_shear(s,(b.coefficient-a.coefficient)%3)


def _root_collision(a,b):
    # A source collision must become different under the canonical target root.
    known={ORIGIN:(ORIGIN,'')}
    q=deque([(ORIGIN,ORIGIN,'')])
    while q:
        x,y,prefix=q.popleft()
        for gen in 'AB':
            nx,ny=a.step(x,gen),b.step(y,gen)
            next_word=prefix+gen
            if nx in known:
                old_y,old_word=known[nx]
                if old_y!=ny:
                    assert a.apply(ORIGIN,old_word)==nx==a.apply(ORIGIN,next_word)
                    assert b.apply(ORIGIN,old_word)==old_y!=ny==b.apply(ORIGIN,next_word)
                    return (old_word,next_word,nx,old_y,ny)
            else:
                known[nx]=(ny,next_word)
                q.append((nx,ny,next_word))
    raise AssertionError("missing root collision for known nonroot pair")


@dataclass(frozen=True)
class WindowWitness:
    source:Window48
    target:Window48
    watch:str
    status:str
    classification:str
    native_rule:str
    mapped_origin:tuple[int,...]|None
    obstruction_word:str|None
    obstruction_counts:tuple[int,int]|None
    collision:tuple|None
    checked_edges:int
    parent_id:int|None
    omissions:tuple[str,...]

    def summary(self):
        return {'source':vars(self.source),'target':vars(self.target),
            'watch':self.watch,'status':self.status,'classification':self.classification,
            'native_rule':self.native_rule,'mapped_origin':self.mapped_origin,
            'obstruction_word':self.obstruction_word,'obstruction_counts':self.obstruction_counts,
            'collision':self.collision,'checked_edges':self.checked_edges,
            'parent_id':self.parent_id,'omissions':self.omissions}


@dataclass
class Engine2WindowResearch:
    findings:list[WindowWitness]=field(default_factory=list)

    def investigate(self,a:Window48,b:Window48,*,watch:str='FULL_STATE',parent_id:int|None=None)->WindowWitness:
        if watch not in ('FULL_STATE','ROOTED'):
            raise ValueError("declared window WATCH must be ROOTED or FULL_STATE")
        if parent_id is not None and (not 0<=parent_id<len(self.findings) or self.findings[parent_id].target!=a):
            raise ValueError("research continuation lost its witnessed parent referent")
        kind,witness=classify(a,b)
        edges=0
        if kind=='FULL_OBSTRUCTED':
            src,dst=count_word(a,witness),count_word(b,witness)
            if src==dst:raise AssertionError("fixed-word obstruction failed native enumeration")
            status='FULL_STATE_OBSTRUCTED' if watch=='FULL_STATE' else 'ROOTED_OBSTRUCTED_BY_FULL_STATE_INVARIANT'
            result=WindowWitness(a,b,watch,status,kind,'native fixed action-word state counts',None,
                                 witness,(src,dst),None,0,parent_id,
                                 ('fixed-word counts prove full-state nonconjugacy for this family',))
        else:
            for state in product(F3,repeat=3):
                mapped=witness(state)
                for gen in 'AB':
                    if witness(a.step(state,gen))!=b.step(mapped,gen):
                        raise AssertionError("proposed state conjugacy fails a generator square")
                    edges+=1
            mapped_root=witness(ORIGIN)
            if kind=='ROOTED_FULL':
                assert mapped_root==ORIGIN
                status='ROOTED_FULL_EQUIVALENT' if watch=='ROOTED' else 'FULL_STATE_EQUIVALENT'
                collision=None
            else:
                assert mapped_root!=ORIGIN
                collision=_root_collision(a,b)
                status='ROOTED_OBSTRUCTED_BY_WORD_COLLISION' if watch=='ROOTED' else 'FULL_STATE_NONROOT_EQUIVALENT'
            result=WindowWitness(a,b,watch,status,kind,'exact labeled conjugacy checked on full F3^3',
                                 mapped_root,None,None,collision,edges,parent_id,
                                 ('unrooted state bijection does not preserve canonical marked origin',)
                                 if kind=='FULL_UNROOTED' else
                                 ('full-state correspondence witnessed in the stated 48-law family only',))
        self.findings.append(result)
        return result

    def reenter(self,previous:int,b:Window48,watch='FULL_STATE'):
        if not 0<=previous<len(self.findings):raise ValueError('unknown witness')
        return self.investigate(self.findings[previous].target,b,watch=watch,parent_id=previous)


def audit48():
    # Independently compute the classified pair distribution in this adapter.
    laws=family48();count=Counter();signatures=set()
    lab=Engine2WindowResearch()
    for a in laws:
        signatures.add(tuple(a.step(s,'B') for s in product(F3,repeat=3)))
        for b in laws:
            w=lab.investigate(a,b)
            count[(w.classification,w.obstruction_word)] += 1
    return {'laws':len(laws),'unique_tables':len(signatures),
            'pair_witnesses':len(lab.findings),'distribution':{str(k):v for k,v in count.items()},
            'rooted_pairs':count[('ROOTED_FULL',None)],'nonroot_pairs':count[('FULL_UNROOTED',None)]}

if __name__=='__main__':
    import json
    print(json.dumps(audit48(),indent=2))