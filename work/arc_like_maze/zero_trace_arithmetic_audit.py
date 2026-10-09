"""Independent direct 81-by-36 GF3 matrix and cyclic-order audit.

Uses NONE of the classifier, WindowProcess or graph-construction modules.
For every one of 162 zero-trace fourth-coordinate configurations it:
  - constructs the 81 compatibility equations on 36 unknown values;
  - row-reduces them directly, preserving every independent q2 direction
    and separate connected-component correction gauge;
  - computes all 27 three-turn traces on each nullspace basis vector;
  - independently counts when order 3, order 9, or BOTH are possible.

Run:
    python -m work.arc_like_maze.zero_trace_arithmetic_audit
"""
from collections import Counter
from itertools import product

F3=(0,1,2)
LOWER={
    1:(0,1,2,0,2,1,1,1,1),
    2:(0,1,2,1,0,2,1,1,1),
}
ALPHA={
    1:(0,1,1),
    2:(0,0,1),
}
NODES=tuple(product(F3,repeat=3))


def equations(gain,Q,k):
    """Actual commutation equations in 27 K-values and nine q2 entries."""
    q0=LOWER[gain]
    alpha=ALPHA[gain]
    h=tuple((q-Q[0])%3 for q in Q)
    rows=[]
    for u,v,z,y in product(F3,repeat=4):
        w=(z+alpha[v])%3
        nv=(v+gain*(u+1))%3
        nz=(z+q0[3*u+v])%3
        ny=(y+Q[w]+k[v])%3
        cy=(y+h[w])%3
        row=[0]*36
        row[9*nv+3*nz+ny]+=1
        row[9*v+3*z+y]-=1
        row[27+3*((z+1)%3)+cy]-=1
        row[27+3*z+y]+=1
        rows.append([a%3 for a in row])
    return rows


def rref(M):
    """Finite-field RREF of a matrix with arbitrary number of columns."""
    if not M:
        return 0,[]
    A=[list(row) for row in M]
    width=len(A[0])
    pivot_columns=[]
    head=0
    for col in range(width):
        pivot=next((i for i in range(head,len(A)) if A[i][col]),None)
        if pivot is None:
            continue
        A[head],A[pivot]=A[pivot],A[head]
        inv=pow(A[head][col],-1,3)
        A[head]=[(a*inv)%3 for a in A[head]]
        for i in range(len(A)):
            if i!=head and A[i][col]:
                multiple=A[i][col]
                A[i]=[(a-multiple*b)%3 for a,b in zip(A[i],A[head])]
        pivot_columns.append(col)
        head+=1
    free=[j for j in range(width) if j not in pivot_columns]
    basis=[]
    for j in free:
        v=[0]*width
        v[j]=1
        for i,col in enumerate(pivot_columns):
            v[col]=(-A[i][j])%3
        basis.append(tuple(v))
    return head,basis


def rank(vectors):
    if not vectors:return 0
    return rref(vectors)[0]


def three_turn_trace(gain,Q,correction):
    alpha=ALPHA[gain]
    h=tuple((a-Q[0])%3 for a in Q)
    result=[]
    for start in NODES:
        v,z,y=start
        t=start
        displacement=0
        for _ in F3:
            v1,z1,y1=t
            displacement=(displacement+correction[9*v1+3*z1+y1])%3
            w=(z1+alpha[v1])%3
            t=(v1,(z1+1)%3,(y1+h[w])%3)
        if t!=start:
            raise AssertionError(("the purported zero-trace lower map is not order three",
                                  gain,Q,start,t))
        result.append(displacement)
    return tuple(result)


def audit():
    histogram=Counter()
    totals=Counter()
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            if sum(Q)%3:
                continue
            for j,k in product(F3,repeat=2):
                offsets=(0,j,k)
                matrix=equations(gain,Q,offsets)
                matrix_rank,basis=rref(matrix)
                gauges=tuple(b for b in basis if not any(b[27:]))
                q2_basis=tuple(b for b in basis if any(b[27:]))
                # Every connected component contributes one independent gauge.
                components=len(gauges)
                qrank=9-len(q2_basis)
                if components not in (1,3):
                    raise AssertionError(("unexpected number of components",
                                          gain,Q,offsets,components))
                histogram[(components,qrank)]+=1
                if matrix_rank+len(basis)!=36:
                    raise AssertionError("bad nullspace calculation")
                gauge_traces=[three_turn_trace(gain,Q,v[:27]) for v in gauges]
                basis_traces=[three_turn_trace(gain,Q,v[:27]) for v in q2_basis]
                gauge_rank=rank(gauge_traces)
                non_gauge_rank=rank(gauge_traces+basis_traces)-gauge_rank
                if gauge_rank not in (0,1) or non_gauge_rank not in (0,1,2):
                    raise AssertionError("unexpected cyclic trace space")
                n=3**len(q2_basis)
                possible_three=n//3**non_gauge_rank
                totals["configurations"]+=1
                totals["admitted"]+=n
                totals["order_three_possible"]+=possible_three
                totals["order_nine_possible"]+=(n if gauge_rank else n-possible_three)
                totals["both_orders_possible"]+=possible_three if gauge_rank else 0
                totals["nontrivial_component_gauges"]+=int(gauge_rank>0)
                totals["q2_basis_vectors"]+=len(q2_basis)
                totals["all_nullspace_vectors"]+=len(basis)
                totals["three_turn_trace_checks"]+=27*len(basis)
    expected_hist=Counter({
        (1,3):12,(1,4):24,(1,5):36,(1,6):72,
        (3,3):2,(3,4):4,(3,5):4,(3,6):8,
    })
    expected={
        "configurations":162,
        "admitted":22410,
        "order_three_possible":11106,
        "order_nine_possible":12492,
        "both_orders_possible":1188,
        "nontrivial_component_gauges":12,
        "q2_basis_vectors":624,
        "all_nullspace_vectors":822,
        "three_turn_trace_checks":22194,
    }
    if histogram!=expected_hist or dict(totals)!=expected:
        raise AssertionError(("independent audit changed",dict(histogram),
                              dict(totals)))
    return {
        "status":"INDEPENDENT_ZERO_TRACE_MATRIX_AND_CYCLIC_ORDER_PASSED",
        "component_rank_histogram":dict(histogram),
        "counts":dict(totals),
    }


if __name__=="__main__":
    print(audit())
