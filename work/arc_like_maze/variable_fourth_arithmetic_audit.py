"""Independent 81-by-36 finite-field matrix audit for variable fourth rules.

Imports NO repo construction, classifier, or graph functions.
Each of 324 order-nine fourth-coordinate configurations yields 81
linear equations in 27 additive correction values and nine q2 values.
Direct RREF computes the full nullspace. Since the lower B action on the
27 vertices is connected, one null vector is the constant gauge for L;
the other 2/3/4 vectors form a complete q2 basis.

Checks the nine-turn correction trace on every lower vertex for every
null vector, proving that no order-27 extension exists in this schema.

Run:
    python -m work.arc_like_maze.variable_fourth_arithmetic_audit
"""
from collections import Counter
from itertools import product

F3=(0,1,2)
Q0={
    1:(0,1,2,0,2,1,1,1,1),
    2:(0,1,2,1,0,2,1,1,1),
}
ALPHA={1:(0,1,1),2:(0,0,1)}


def equations(g,Q,k):
    """Build directly from the 81 commutation equalities, not a graph tree."""
    lower=Q0[g]
    a=ALPHA[g]
    h=[(t-Q[0])%3 for t in Q]
    result=[]
    for u,v,z,y in product(F3,repeat=4):
        w=(z+a[v])%3
        nv=(v+g*(u+1))%3
        nz=(z+lower[3*u+v])%3
        ny=(y+Q[w]+k[v])%3
        cy=(y+h[w])%3
        row=[0]*36
        row[9*nv+3*nz+ny]+=1
        row[9*v+3*z+y]-=1
        row[27+3*((z+1)%3)+cy]-=1
        row[27+3*z+y]+=1
        result.append([t%3 for t in row])
    return result


def nullspace(matrix):
    """Complete RREF over F3 in 36 unknowns, without external packages."""
    rows=[row[:] for row in matrix]
    pivots=[]
    pivot_row=0
    for col in range(36):
        first=next((i for i in range(pivot_row,len(rows)) if rows[i][col]),None)
        if first is None:continue
        rows[pivot_row],rows[first]=rows[first],rows[pivot_row]
        inverse=pow(rows[pivot_row][col],-1,3)
        rows[pivot_row]=[(v*inverse)%3 for v in rows[pivot_row]]
        for j in range(len(rows)):
            if j!=pivot_row and rows[j][col]:
                factor=rows[j][col]
                rows[j]=[(v-factor*w)%3 for v,w in
                         zip(rows[j],rows[pivot_row])]
        pivots.append(col)
        pivot_row+=1
    independent=[j for j in range(36) if j not in pivots]
    basis=[]
    for free in independent:
        vec=[0]*36
        vec[free]=1
        for i,p in enumerate(pivots):
            vec[p]=(-rows[i][free])%3
        basis.append(vec)
    return len(pivots),basis


def nine_turn_trace(g,Q,correction,initial):
    """Return the final lower vertex and fifth-coordinate displacement."""
    v,z,y=initial
    total=0
    a=ALPHA[g]
    for _ in range(9):
        total=(total+correction[9*v+3*z+y])%3
        w=(z+a[v])%3
        z=(z+1)%3
        y=(y+Q[w]-Q[0])%3
    return (v,z,y),total


def audit():
    ranks=Counter()
    configurations=admitted_combinations=0
    basis_witnesses=trace_checks=0
    fourth_dependent_rank7=0
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            if sum(Q)%3==0:
                continue
            for r,s in product(F3,repeat=2):
                k=(0,r,s)
                mat=equations(gain,Q,k)
                rank,basis=nullspace(mat)
                # Full 36-vector nullspace contains exactly one gauge
                # with q2=0; all other basis vectors parameterize q2.
                admissible=[b for b in basis if any(b[27:])]
                dim=len(admissible)
                if dim != 9-(rank-26):
                    raise AssertionError("elimination or gauge count changed")
                q2_projection={tuple(b[27:]) for b in admissible}
                if len(q2_projection)!=dim:
                    raise AssertionError("q2 basis vectors are dependent")
                rank_q2=9-dim
                ranks[rank_q2]+=1
                admitted_combinations+=3**dim
                configurations+=1
                basis_witnesses+=dim
                for b in basis:
                    if any(b[27:]) and rank_q2==7:
                        fifth=b[27:]
                        if any(fifth[3*z+y]!=fifth[3*z]
                               for z,y in product(F3,repeat=2)):
                            fourth_dependent_rank7+=1
                    for vertex in product(F3,repeat=3):
                        end,trace=nine_turn_trace(gain,Q,b[:27],vertex)
                        trace_checks+=1
                        if end!=vertex or trace!=0:
                            raise AssertionError(
                                ("possible order-27 extension",
                                 gain,Q,k,vertex,trace))
    expected=Counter({5:60,6:48,7:216})
    if (configurations,admitted_combinations,basis_witnesses,
            trace_checks,fourth_dependent_rank7)!=(
            324,8100,816,(816+324)*27,0) or ranks!=expected:
        raise AssertionError(("unexpected independent counts",dict(ranks),
              configurations,admitted_combinations,basis_witnesses,trace_checks))
    return {
        "status":"INDEPENDENT_FULL_MATRIX_AND_CYCLIC_ORDER_PROOF_PASSED",
        "configurations":configurations,
        "rank_counts":dict(ranks),
        "admitted_fifth_combinations":admitted_combinations,
        "nontrivial_q2_basis_vectors":basis_witnesses,
        "complete_nine_turn_trace_checks":trace_checks,
        "rank7_fourth_coordinate_dependences":fourth_dependent_rank7,
        "order27_obstructions_found":0,
    }


if __name__=="__main__":
    print(audit())
