"""Standalone finite comparison of completed witnessed rooted extensions.

Accepts completed bounded_backtracked_goal.BacktrackResult records. This
compares results rather than running a replacement solver. All claims are for
specified complete finite laws; it cannot authenticate an external observer.
"""
from dataclasses import dataclass
from collections import deque
from itertools import combinations

ROOT=(0,0,0)

@dataclass(frozen=True)
class SeparatingWitness:
    first: int
    second: int
    cause: str
    left_word: str
    right_word: str
    old_equal: bool
    new_equal: bool

@dataclass(frozen=True)
class PortfolioResult:
    status: str
    chosen: tuple[int,...]
    carried: tuple
    paired_states: tuple
    admitted_edges: tuple
    conflicts: tuple[SeparatingWitness,...]
    compatible_subsets: int
    possible_goal_images: tuple


def _verified_candidate(old,new,record):
    if record.status!='GOAL_CARRIED_FINITE_WITNESS':
        raise ValueError('candidate is not a completed finite goal witness')
    mapping=dict(record.paired_states)
    if (not mapping or mapping.get(ROOT)!=ROOT or
            len(mapping)!=len(record.paired_states) or
            len(set(mapping.values()))!=len(mapping)):
        raise ValueError('candidate pairing invalid')
    edges={}
    for s,a,t,ns,nt in record.admitted_edges:
        if (mapping.get(s)!=ns or mapping.get(t)!=nt or
                old.step(s,a)!=t or new.step(ns,a)!=nt or
                ((s,a) in edges and edges[(s,a)]!=(s,a,t,ns,nt))):
            raise ValueError('admitted edge fails finite replay')
        edges[(s,a)]=(s,a,t,ns,nt)
    if (record.goal not in mapping or mapping[record.goal]!=record.mapped_goal or
            old.follow(record.goal_word)!=record.goal or
            new.follow(record.goal_word)!=record.mapped_goal):
        raise ValueError('goal witness fails finite replay')
    words={ROOT:''};q=deque([ROOT])
    while q:
        s=q.popleft()
        for action in 'AB':
            e=edges.get((s,action))
            if e and e[2] not in words:
                words[e[2]]=words[s]+action
                q.append(e[2])
    if set(words)!=set(mapping):
        raise ValueError('a paired state lacks a rooted admitted-edge path')
    for s,w in words.items():
        if old.follow(w)!=s or new.follow(w)!=mapping[s]:
            raise ValueError('rooted path fails finite replay')
    return mapping,edges,words


def compare_completed(old,new,candidates,goals):
    """Exact powerset comparison on 1..8 supplied candidates, no new search."""
    if not (isinstance(candidates,tuple) and 1<=len(candidates)<=8 and
            isinstance(goals,tuple) and goals and len(goals)==len(set(goals))):
        raise ValueError('finite candidate and goal lists required')
    verified=[_verified_candidate(old,new,c) for c in candidates]
    conflicts=[]
    for i,j in combinations(range(len(verified)),2):
        fi,_,wi=verified[i];fj,_,wj=verified[j]
        direct=next(((wi[s],wj[s],'SOURCE_COLLISION') for s in sorted(set(fi)&set(fj))
                     if fi[s]!=fj[s]),None)
        if direct is None:
            rev={n:s for s,n in fi.items()}
            direct=next(((wi[rev[n]],wj[s],'TARGET_COLLISION') for s,n in sorted(fj.items())
                         if n in rev and rev[n]!=s),None)
        if direct is not None:
            x,y,cause=direct
            old_eq=old.follow(x)==old.follow(y)
            new_eq=new.follow(x)==new.follow(y)
            if old_eq==new_eq:raise ValueError('conflict lacks separating equality witness')
            conflicts.append(SeparatingWitness(i,j,cause,x,y,old_eq,new_eq))
    valid=[]
    for size in range(1,len(verified)+1):
        for subset in combinations(range(len(verified)),size):
            f,rev,edges={}, {}, {}
            accepted=True
            for i in subset:
                for s,n in verified[i][0].items():
                    if (s in f and f[s]!=n) or (n in rev and rev[n]!=s):
                        accepted=False;break
                    f[s],rev[n]=n,s
                if not accepted:break
                for key,e in verified[i][1].items():
                    if key in edges and edges[key]!=e:
                        accepted=False;break
                    edges[key]=e
                if not accepted:break
            if not accepted:continue
            if any(f.get(s)!=ns or f.get(t)!=nt for s,a,t,ns,nt in edges.values()):
                continue
            carried=[]
            for goal in goals:
                if goal in f:
                    word=min((verified[i][2][goal] for i in subset if goal in verified[i][2]),
                             key=lambda w:(len(w),w))
                    carried.append((goal,f[goal],word))
            score=(len(carried),len(edges),len(f),-len(subset))
            valid.append((score,subset,tuple(carried),tuple(sorted(f.items())),
                          tuple(sorted(edges.values()))))
    if not valid:
        raise ValueError('no verified compatible candidate')
    best=max(x[0] for x in valid)
    selected=next(x for x in valid if x[0]==best)
    peak=max(x[0][0] for x in valid)
    images=tuple((goal,tuple(sorted({image for score,ss,carry,*rest in valid
                                    if score[0]==peak for g,image,w in carry if g==goal})))
                 for goal in goals)
    status='GOALS_CARRIED' if len(selected[2])==len(goals) else 'PARTIAL_GOALS'
    return PortfolioResult(status,selected[1],selected[2],selected[3],selected[4],
                           tuple(conflicts),len(valid),images)
