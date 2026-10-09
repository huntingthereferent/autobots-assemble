"""Independent COMPLETE 486-configuration, 81x36 finite-field reconciliation.

Imports NONE of the branch classifiers, unified adapter or existing
transition engine. Directly constructs all 81 cohomology equations,
computes their F3 nullspaces, separates the q2 kernel from correction
gauge, and checks the exact 3/9 turn trace on all 27 lower states.

This auditor checks the global mathematical partition without claiming
that every one of the 486*19683 possible fifth coupling tables is
individually enumerated. Linear subspace dimensions prove their totals.

Execute:
  python -m work.arc_like_maze.pointed_coupling_independent_audit
"""
from collections import Counter
from itertools import product

F3=(0,1,2)
LOWER={
    1:(0,1,2,0,2,1,1,1,1),
    2:(0,1,2,1,0,2,1,1,1),
}
ALPHA={1:(0,1,1),2:(0,0,1)}
NODES=tuple(product(F3,repeat=3))


def equations(g,Q,k):
    lower=LOWER[g]
    alpha=ALPHA[g]
    result=[]
    for u,v,z,y in product(F3,repeat=4):
        w=(z+alpha[v])%3
        nv=(v+g*(u+1))%3
        nz=(z+lower[3*u+v])%3
        ny=(y+Q[w]+k[v])%3
        cy=(y+Q[w]-Q[0])%3
        row=[0]*36
        row[9*nv+3*nz+ny]+=1
        row[9*v+3*z+y]-=1
        row[27+3*((z+1)%3)+cy]-=1
        row[27+3*z+y]+=1
        result.append([x%3 for x in row])
    return result


def nullspace(matrix):
    rows=[list(r) for r in matrix]
    pivots=[]
    pivot_row=0
    width=36
    for j in range(width):
        pivot=next((i for i in range(pivot_row,len(rows)) if rows[i][j]),None)
        if pivot is None:continue
        rows[pivot_row],rows[pivot]=rows[pivot],rows[pivot_row]
        inverse=pow(rows[pivot_row][j],-1,3)
        rows[pivot_row]=[(x*inverse)%3 for x in rows[pivot_row]]
        for i in range(len(rows)):
            if i!=pivot_row and rows[i][j]:
                multiple=rows[i][j]
                rows[i]=[(a-multiple*b)%3 for a,b in zip(rows[i],rows[pivot_row])]
        pivots.append(j)
        pivot_row+=1
    free=[j for j in range(width) if j not in pivots]
    basis=[]
    for j in free:
        b=[0]*width
        b[j]=1
        for i,k in enumerate(pivots):
            b[k]=(-rows[i][j])%3
        basis.append(tuple(b))
    return tuple(basis)


def rank(vectors):
    if not vectors:return 0
    rows=[list(v) for v in vectors]
    piv=0
    width=len(rows[0])
    for j in range(width):
        found=next((i for i in range(piv,len(rows)) if rows[i][j]),None)
        if found is None:continue
        rows[piv],rows[found]=rows[found],rows[piv]
        inverse=pow(rows[piv][j],-1,3)
        rows[piv]=[(x*inverse)%3 for x in rows[piv]]
        for i in range(len(rows)):
            if i!=piv and rows[i][j]:
                c=rows[i][j]
                rows[i]=[(a-c*b)%3 for a,b in zip(rows[i],rows[piv])]
        piv+=1
    return piv


def trace(g,Q,correction,turns):
    alpha=ALPHA[g]
    values=[]
    for root in NODES:
        current=root
        total=0
        for _ in range(turns):
            v,z,y=current
            total=(total+correction[9*v+3*z+y])%3
            w=(z+alpha[v])%3
            current=(v,(z+1)%3,(y+Q[w]-Q[0])%3)
        if current!=root:
            raise AssertionError(("lower orbit did not close",g,Q,turns,root))
        values.append(total)
    return tuple(values)


def audit():
    rank_hist=Counter()
    components=Counter()
    counts=Counter()
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            lower_order=3 if sum(Q)%3==0 else 9
            for j,k in product(F3,repeat=2):
                basis=nullspace(equations(gain,Q,(0,j,k)))
                gauges=[v for v in basis if not any(v[27:])]
                q2_vectors=[v for v in basis if any(v[27:])]
                component_count=len(gauges)
                if component_count not in (1,3):
                    raise AssertionError("component gauge dimension changed")
                # Original 36x matrix has a full linear nullspace basis.
                if len(basis)!=len(gauges)+len(q2_vectors):
                    raise AssertionError("non-disjoint gauge and coupling witnesses")
                independent_q2=rank([v[27:] for v in q2_vectors])
                if independent_q2!=len(q2_vectors):
                    raise AssertionError("fifth coupling basis lost injectivity")
                constraint_rank=9-independent_q2
                rank_hist[constraint_rank]+=1
                components[component_count]+=1
                count=3**independent_q2
                counts["configurations"]+=1
                counts["admitted"]+=count
                counts["coupling_basis"]+=independent_q2
                counts["component_gauge_basis"]+=component_count
                counts["all_basis"]+=len(basis)
                counts["trace_checks"]+=27*len(basis)
                if lower_order==9:
                    counts["nonzero_trace_configs"]+=1
                    for b in basis:
                        if any(trace(gain,Q,b[:27],9)):
                            raise AssertionError("unexpected order-27 fifth lift")
                    counts["order9"]+=count
                else:
                    counts["zero_trace_configs"]+=1
                    gt=[trace(gain,Q,b[:27],3) for b in gauges]
                    lt=[trace(gain,Q,b[:27],3) for b in q2_vectors]
                    gauge_rank=rank(gt)
                    relative_rank=rank(gt+lt)-gauge_rank
                    if gauge_rank not in (0,1):
                        raise AssertionError("component gauge trace rank changed")
                    can_three=count//3**relative_rank
                    counts["order3"]+=can_three
                    counts["order9"]+=count if gauge_rank else count-can_three
                    counts["both"]+=can_three if gauge_rank else 0
    expected={
        "configurations":486,
        "admitted":30510,
        "coupling_basis":1440,
        "component_gauge_basis":522,
        "all_basis":1962,
        "trace_checks":52974,
        "nonzero_trace_configs":324,
        "zero_trace_configs":162,
        "order3":11106,
        "order9":20592,
        "both":1188,
    }
    if dict(counts)!=expected or rank_hist!=Counter({
            3:14,4:28,5:100,6:128,7:216}) or components!=Counter({1:468,3:18}):
        raise AssertionError(("reconciliation mismatch",dict(counts),
                             dict(rank_hist),dict(components)))
    return {
        "status":"INDEPENDENT_COMPLETE_POINTED_BRANCH_RECONCILIATION",
        "counts":dict(counts),
        "rank_histogram":dict(rank_hist),
        "graph_components":dict(components),
        "scope":"two admitted q0 systems; prescribed additive fifth-coordinate lifts",
    }


if __name__=="__main__":
    print(audit())
