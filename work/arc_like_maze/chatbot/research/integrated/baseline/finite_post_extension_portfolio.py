"""Independent finite owner-law witness for ranking seed unions AFTER extension.

Unlike the integrated chatbot, this module sees the complete specified laws.
No remote provenance, physical claim or exhaustive universal correspondence.
"""
from itertools import combinations
from finite_goal_priority import Law, ROOT
from finite_seed_first import path_seeds


def compare(old, new, goals, *, depth=6, variants=3, pool_limit=5, trial_limit=6):
    if not (isinstance(old, Law) and isinstance(new, Law)):
        raise TypeError('finite laws required')
    if (type(goals) is not tuple or not goals or len(set(goals)) != len(goals)
            or any(type(g) is not tuple or len(g)!=3 or
                   any(type(x) is not int or x not in (0,1,2) for x in g) for g in goals)):
        raise ValueError('distinct finite goals required')
    if not (type(depth) is int and 0<=depth<=8 and type(variants) is int and 1<=variants<=10
            and type(pool_limit) is int and 1<=pool_limit<=8 and
            type(trial_limit) is int and 1<=trial_limit<=24):
        raise ValueError('bounded candidate limits required')
    prefixes=path_seeds(old,new,depth)
    per_goal=[[p for p in prefixes if p[1][-1]==g][:variants] for g in goals]
    pool=[];used=set()
    for i in range(variants):
        for goal_candidates in per_goal:
            if i<len(goal_candidates) and goal_candidates[i][0] not in used:
                p=goal_candidates[i];pool.append(p);used.add(p[0])
    pool=pool[:pool_limit]
    selections=[]
    for size in range(1,len(pool)+1):
        for group in combinations(pool,size):
            fwd,rev,edges={}, {}, {}
            good=True
            for word,op,np in group:
                for o,n in zip(op,np):
                    if o in fwd and fwd[o]!=n or n in rev and rev[n]!=o:
                        good=False;break
                    fwd[o]=n;rev[n]=o
                if not good:break
                for i,action in enumerate(word):
                    key=(op[i],action)
                    edge=(op[i],action,op[i+1],np[i],np[i+1])
                    if key in edges and edges[key]!=edge:
                        good=False;break
                    edges[key]=edge
                if not good:break
            if not good:continue
            words=tuple(sorted((w for w,_,_ in group),key=lambda w:(len(w),w)))
            seeds=tuple(g for g in goals if any(p[1][-1]==g for p in group))
            score=(len(seeds),len(edges),len(fwd),-len(words))
            selections.append((score,words,dict(fwd),dict(rev),dict(edges)))
    selections.sort(key=lambda x:(tuple(-n for n in x[0]),x[1]))
    distinct=[];seen=set()
    for item in selections:
        identity=tuple(sorted(item[2].items()))
        if identity in seen:continue
        distinct.append(item);seen.add(identity)
        if len(distinct)==trial_limit:break
    trials=[]
    for _,words,fwd,rev,edges in distinct:
        paths={ROOT:''}
        for word in words:
            s=ROOT
            for i,a in enumerate(word):
                s=old.step(s,a)
                if s not in paths or (i+1,word[:i+1])<(len(paths[s]),paths[s]):
                    paths[s]=word[:i+1]
        q=[(s,a) for s in sorted(fwd) for a in 'AB' if (s,a) not in edges]
        excluded=[]
        for s,a in q:
            if (s,a) in edges:continue
            ns=fwd[s];t=old.step(s,a);nt=new.step(ns,a)
            if t in fwd and fwd[t]!=nt or nt in rev and rev[nt]!=t:
                excluded.append((s,a,t,ns,nt));continue
            if t not in fwd:
                fwd[t]=nt;rev[nt]=t;paths[t]=paths[s]+a
                q.extend((t,c) for c in 'AB')
            edges[(s,a)]=(s,a,t,ns,nt)
        assert all(fwd[s]==ns and fwd[t]==nt and old.step(s,a)==t and
                   new.step(ns,a)==nt for s,a,t,ns,nt in edges.values())
        carried=tuple((g,fwd[g],paths[g]) for g in goals if g in paths)
        assert all((old.follow(w),new.follow(w))==(g,n) for g,n,w in carried)
        trials.append((words,carried,len(fwd),len(edges),len(excluded)))
    if not trials:
        return {'status':'GOALS_OUTSIDE_SEARCH_BOUND','trials':(), 'best':None,
                'candidate_cap_reached':len(selections)>0}
    winner=max(trials,key=lambda t:(len(t[1]),t[3],t[2],-t[4],
                                    tuple((-len(w),w) for w in t[0])))
    return {'status':'GOALS_CARRIED' if len(winner[1])==len(goals) else 'PARTIAL_GOALS',
            'trials':tuple(trials),'best':winner,
            'candidate_cap_reached':len(selections)>len(trials)}


if __name__ == '__main__':
    from finite_seed_first import select_and_extend
    a,b=Law((0,0,1)),Law((1,0,1))
    goals=((0,1,0),(0,1,1))
    before=select_and_extend(a,b,goals,variants=3,limit=5)
    after=compare(a,b,goals)
    print('seed-first:',before['status'],'admitted',len(before['edges']),
          'words',before['paths'])
    print('post-extension:',after['status'],'admitted',after['best'][3],
          'words',after['best'][0], 'trials',len(after['trials']))
