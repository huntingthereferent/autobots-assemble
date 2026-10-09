"""Independent complete composition audit for the 486 declared fourth laws.

Does NOT import the pointed adapter, symmetry classifiers, or interpreter.
It explicitly builds the undirected B-orbit graph on 27 states, obtains
the component permutation induced by the lower selected symmetry, and
compares the two actual fifth-coordinate compositions on every lower
state for all 17,334 ordered pairs of component-constant corrections.

Zero fifth coupling q2=0 is admitted for every fourth law. The count
is per ONE chosen underlying law per fourth configuration; NOT an
unqualified count of all law/table orbits or conjugacy classes.

Run:
  python -m work.arc_like_maze.mixed_centralizer_independent_audit
"""
from collections import Counter
from itertools import product

FIELD=(0,1,2)
LOWER={1:(0,1,2,0,2,1,1,1,1),
       2:(0,1,2,1,0,2,1,1,1)}
ALPHA={1:(0,1,1),2:(0,0,1)}
STATES=tuple(product(FIELD,repeat=3))


def lower_b(g,Q,k,s,u):
    v,z,y=s
    w=(z+ALPHA[g][v])%3
    return ((v+g*(u+1))%3,
            (z+LOWER[g][3*u+v])%3,
            (y+Q[w]+k[v])%3)


def lower_c(g,Q,s):
    v,z,y=s
    w=(z+ALPHA[g][v])%3
    return (v,(z+1)%3,(y+Q[w]-Q[0])%3)


def orbits(g,Q,k):
    adj={v:set() for v in STATES}
    for s in STATES:
        for u in FIELD:
            t=lower_b(g,Q,k,s,u)
            adj[s].add(t)
            adj[t].add(s)
    labels={}
    for start in STATES:
        if start in labels: continue
        idx=len(set(labels.values())) if labels else 0
        labels[start]=idx
        stack=[start]
        while stack:
            point=stack.pop()
            for neighbor in adj[point]:
                if neighbor not in labels:
                    labels[neighbor]=idx
                    stack.append(neighbor)
    return labels


def actual_composition(g,Q,labels,first,second,start):
    """Apply C_second first and C_first second (q2=0, potentials = gauges)."""
    s=start
    fifth=0
    for constants in (second,first):
        fifth=(fifth+constants[labels[s]])%3
        s=lower_c(g,Q,s)
    return s,fifth


def audit():
    counts=Counter()
    example=None
    for gain in (1,2):
        for Q in product(FIELD,repeat=3):
            for j,k in product(FIELD,repeat=2):
                labels=orbits(gain,Q,(0,j,k))
                m=len(set(labels.values()))
                if m not in (1,3):raise AssertionError("new component count")
                mapping={}
                for s in STATES:
                    i=labels[s]
                    target=labels[lower_c(gain,Q,s)]
                    if i in mapping and mapping[i]!=target:
                        raise AssertionError("lower symmetry fails to permute components")
                    mapping[i]=target
                perm=tuple(mapping[i] for i in range(m))
                if len(set(perm))!=m:raise AssertionError("not a permutation")
                group=("CONNECTED" if m==1 else
                       "COMPONENTWISE_FIXED" if perm==tuple(range(m)) else
                       "COMPONENT_CYCLE")
                counts[group]+=1
                gauges=list(product(FIELD,repeat=m))
                for first in gauges:
                    for second in gauges:
                        matches=True
                        for s in STATES:
                            lhs=actual_composition(gain,Q,labels,first,second,s)
                            rhs=actual_composition(gain,Q,labels,second,first,s)
                            if lhs!=rhs:
                                matches=False
                                if example is None:
                                    example=dict(gain=gain,Q=Q,offsets=(0,j,k),
                                                 first=first,second=second,
                                                 start=s,
                                                 first_after_second=lhs,
                                                 second_after_first=rhs)
                                break
                        counts["commuting" if matches else "noncommuting"]+=1
                        counts["ordered_pairs"]+=1
    expected=Counter({
        "CONNECTED":468,
        "COMPONENTWISE_FIXED":6,
        "COMPONENT_CYCLE":12,
        "commuting":9558,
        "noncommuting":7776,
        "ordered_pairs":17334,
    })
    if counts!=expected:
        raise AssertionError(("composition audit mismatch",dict(counts)))
    return {
        "status":"INDEPENDENT_COMPONENT_PERMUTATION_AND_EXACT_COMMUTATOR_AUDIT",
        "counts":dict(counts),
        "first_noncommuting_example":example,
    }


if __name__=="__main__":
    print(audit())
