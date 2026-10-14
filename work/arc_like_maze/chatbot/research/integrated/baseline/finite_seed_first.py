"""A finite, standalone witness: select compatible goal paths before extension.

A/B are only the specified 27-state generators imported from finite_goal_priority.
This program is not the integrated chatbot or a general mathematical theorem.
"""
from collections import deque
from itertools import combinations
from finite_goal_priority import Law, ROOT


def path_seeds(old, new, depth=6):
    if type(depth) is not int or not 0 <= depth <= 8:
        raise ValueError('bounded depth required')
    q=deque([('', (ROOT,), (ROOT,))])
    found=[]
    while q:
        word, op, np = q.popleft()
        found.append((word, op, np))
        if len(word)==depth:
            continue
        fwd=dict(zip(op,np)); rev=dict(zip(np,op))
        for action in 'AB':
            o=old.step(op[-1],action); n=new.step(np[-1],action)
            if (o in fwd and fwd[o]!=n) or (n in rev and rev[n]!=o):
                continue
            q.append((word+action,op+(o,),np+(n,)))
    return found


def select_and_extend(old, new, goals, *, depth=6, variants=4, limit=12):
    if not (type(goals) is tuple and goals and len(set(goals))==len(goals) and
            all(type(g) is tuple and len(g)==3 and
                all(type(x) is int and x in (0,1,2) for x in g) for g in goals)):
        raise ValueError('finite distinct goals required')
    if not (type(variants) is int and 1<=variants<=10 and
            type(limit) is int and 1<=limit<=16):
        raise ValueError('finite candidate limits required')
    histories=path_seeds(old,new,depth)
    pool=[]; seen=set()
    bygoal=[[p for p in histories if p[1][-1]==g][:variants] for g in goals]
    for index in range(variants):
        for choices in bygoal:
            if index<len(choices) and choices[index][0] not in seen:
                p=choices[index]; seen.add(p[0]); pool.append(p)
    pool=pool[:limit]
    if not pool:
        return {'status':'GOALS_OUTSIDE_DEPTH','goals':(), 'paths':(),
                'pairs':(), 'edges':(), 'excluded':(), 'candidate_paths':0}
    best=None
    for count in range(1,len(pool)+1):
        for chosen in combinations(pool,count):
            fwd={}; rev={}; edges={}; valid=True
            for word,op,np in chosen:
                for o,n in zip(op,np):
                    if o in fwd and fwd[o]!=n or n in rev and rev[n]!=o:
                        valid=False;break
                    fwd[o]=n;rev[n]=o
                if not valid:break
                for i,a in enumerate(word):
                    edges[(op[i],a)]=(op[i],a,op[i+1],np[i],np[i+1])
            if not valid:continue
            reached=tuple(g for g in goals if any(p[1][-1]==g for p in chosen))
            words=tuple(sorted((p[0] for p in chosen),key=lambda w:(len(w),w)))
            score=(len(reached),len(edges),len(fwd),-len(chosen))
            if best is None or score>best[0] or score==best[0] and words<best[1]:
                best=(score,words,dict(fwd),dict(rev),dict(edges))
    if best is None:raise AssertionError('root path must be consistent')
    _, words, fwd, rev, edges=best
    roots={ROOT:''}
    for word in words:
        p=ROOT
        for idx,a in enumerate(word):
            p=old.step(p,a)
            candidate=word[:idx+1]
            if p not in roots or (len(candidate),candidate)<(len(roots[p]),roots[p]):
                roots[p]=candidate
    assert set(roots)==set(fwd)
    q=[(s,a) for s in sorted(fwd) for a in 'AB' if (s,a) not in edges]
    excluded=[]
    for s,a in q:
        if (s,a) in edges:continue
        ns=fwd[s];t=old.step(s,a);nt=new.step(ns,a)
        if (t in fwd and fwd[t]!=nt) or (nt in rev and rev[nt]!=t):
            excluded.append((s,a,t,ns,nt));continue
        if t not in fwd:
            fwd[t]=nt;rev[nt]=t;roots[t]=roots[s]+a
            q.extend((t,action) for action in 'AB')
        edges[(s,a)]=(s,a,t,ns,nt)
    assert all((fwd[s],fwd[t])==(ns,nt) and old.step(s,a)==t and new.step(ns,a)==nt
               for s,a,t,ns,nt in edges.values())
    carried=tuple((g,fwd[g],roots[g]) for g in goals if g in roots)
    assert all((old.follow(w),new.follow(w))==(g,n) for g,n,w in carried)
    return {'status':'GOALS_CARRIED' if len(carried)==len(goals) else 'PARTIAL_GOALS',
            'goals':carried,'paths':words,'pairs':tuple(sorted(fwd.items())),
            'edges':tuple(sorted(edges.values())),'excluded':tuple(excluded),
            'candidate_paths':len(pool)}

if __name__=='__main__':
    from bounded_backtracked_goal import discover_and_extend
    from finite_extension_portfolio import compare_completed
    old,new=Law((0,0,1)),Law((0,0,0))
    goals=((0,1,1),(0,2,0))
    completed=tuple(discover_and_extend(old,new,g) for g in goals)
    prior=compare_completed(old,new,completed,goals)
    fresh=select_and_extend(old,new,goals)
    print('completed-first',prior.status,len(prior.carried))
    print('seed-first',fresh['status'],len(fresh['goals']),fresh['paths'],
          len(fresh['pairs']),len(fresh['edges']),len(fresh['excluded']))
