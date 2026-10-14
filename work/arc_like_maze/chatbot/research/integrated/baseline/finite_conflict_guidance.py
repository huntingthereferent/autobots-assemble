"""Standalone finite counterexample-guided next-trial witness.

A/B are the specified finite operators in finite_goal_priority, not universal A/B.
Complete known finite laws are used only in this standalone experiment.
"""
from collections import deque
from dataclasses import dataclass
from finite_goal_priority import Law, ROOT

@dataclass(frozen=True)
class Rejected:
    source: tuple
    action: str
    target: tuple
    new_start: tuple
    new_target: tuple
    assigned_target: tuple | None
    cause: str
    left_word: str
    right_word: str
    old_equal: bool
    new_equal: bool

@dataclass(frozen=True)
class FiniteExtension:
    words: tuple[str, ...]
    mapping: tuple
    admitted: tuple
    rejected: tuple[Rejected, ...]

def extend(old: Law, new: Law, words: tuple[str, ...]):
    if not isinstance(old,Law) or not isinstance(new,Law) or not words:
        raise ValueError('two finite laws and at least one seed word required')
    fwd, rev, edges, roots = {ROOT:ROOT},{ROOT:ROOT},{},{ROOT:''}
    for word in words:
        if not isinstance(word,str) or any(ch not in 'AB' for ch in word):
            raise ValueError('action word must use only A/B')
        s=t=ROOT
        for i,a in enumerate(word):
            ns,nt=old.step(s,a),new.step(t,a)
            if (ns in fwd and fwd[ns]!=nt) or (nt in rev and rev[nt]!=ns):
                raise ValueError('seed paths cannot share a consistent pairing')
            fwd[ns],rev[nt]=nt,ns
            key=(s,a);edge=(s,a,ns,t,nt)
            if key in edges and edges[key]!=edge:
                raise ValueError('seed paths disagree on labeled edge')
            edges[key]=edge
            prefix=word[:i+1]
            if ns not in roots or (len(prefix),prefix)<(len(roots[ns]),roots[ns]):
                roots[ns]=prefix
            s,t=ns,nt
    queue=deque((s,a) for s in sorted(fwd) for a in 'AB' if (s,a) not in edges)
    excluded=[]
    while queue:
        s,a=queue.popleft()
        if (s,a) in edges:continue
        t_old=old.step(s,a);t_new=new.step(fwd[s],a)
        if (t_old in fwd and fwd[t_old]!=t_new) or (t_new in rev and rev[t_new]!=t_old):
            if t_old in fwd and fwd[t_old]!=t_new:
                cause='SOURCE_COLLISION';other=roots[t_old]
            else:
                cause='TARGET_COLLISION';other=roots[rev[t_new]]
            attempted=roots[s]+a
            old_eq=old.follow(other)==old.follow(attempted)
            new_eq=new.follow(other)==new.follow(attempted)
            if old_eq==new_eq:raise AssertionError('no separating witness')
            excluded.append(Rejected(s,a,t_old,fwd[s],t_new,fwd.get(t_old),
                      cause,other,attempted,old_eq,new_eq))
        else:
            if t_old not in fwd:
                fwd[t_old]=t_new;rev[t_new]=t_old;roots[t_old]=roots[s]+a
                queue.extend((t_old,label) for label in 'AB')
            edges[s,a]=(s,a,t_old,fwd[s],t_new)
    assert all(fwd[s]==ns and fwd[t]==nt and old.step(s,a)==t and
               new.step(ns,a)==nt for s,a,t,ns,nt in edges.values())
    return FiniteExtension(words,tuple(sorted(fwd.items())),
                           tuple(sorted(edges.values())),tuple(excluded))

def choose_alternative(old: Law, new: Law, first_words, candidates):
    """Prioritize candidate seed admitting an actually excluded old-state edge."""
    first=extend(old,new,first_words)
    original={(r.source,r.action):r for r in first.rejected}
    ranked=[]
    for pos,words in enumerate(candidates):
        if words==first_words:continue
        # Only admitted seed transitions count as possible guidance, not
        # guesses about a candidate's unobserved closure.
        seen=set()
        for word in words:
            s=ROOT
            for a in word:
                seen.add((s,a));s=old.step(s,a)
        covered=[original[k] for k in sorted(original) if k in seen]
        if covered:
            ranked.append((len(covered),-pos,words,covered[0]))
    if not ranked:
        return first,None,None
    _,_,words,rejection=max(ranked,key=lambda x:x[:2])
    alternate=extend(old,new,words)
    edge=next((e for e in alternate.admitted if e[:2]==(rejection.source,rejection.action)),None)
    if edge is None or edge[2]!=rejection.target:
        return first,alternate,None
    # The *previous assigned state image* is the clash. The raw observed edge
    # may have identical endpoints in both descriptions.
    return first,alternate,(rejection,edge)

if __name__=='__main__':
    a,b=Law((0,0,1)),Law((1,0,1))
    seed=('AAAB','BBBB','BAABA','ABAABB')
    alt=('AAAB','ABBAA','BAABA')
    first,second,pair=choose_alternative(a,b,seed,(alt,))
    print('first:',len(first.mapping),'states',len(first.admitted),'edges',len(first.rejected),'excluded')
    print('alternate:',len(second.mapping),'states',len(second.admitted),'edges',len(second.rejected),'excluded')
    print('replayed previously excluded edge:',pair[0].source,pair[0].action,
          'previous-assigned-image',pair[0].assigned_target,
          'alternative-new-image',pair[1][4])
