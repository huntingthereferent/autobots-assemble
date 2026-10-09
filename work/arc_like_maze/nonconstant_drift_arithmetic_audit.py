"""Independent enumeration of all nine-entry F3 lower couplings.

Imports NO implementation/classifier from work.arc_like_maze. It checks
the algebraic cohomological criterion against a separate signed voltage
graph solver for every q0 table and both gains, then exhaustively
validates the admitted corrected action on finite states.

Run:
 python -m work.arc_like_maze.nonconstant_drift_arithmetic_audit

Finite enumeration exhausts the DECLARED q0 grammar (3^9 tables),
not unrestricted nonlinear/higher-coordinate state automorphisms.
"""
from __future__ import annotations

from collections import Counter
from itertools import product

F3=(0,1,2)


def algebraic_admission(q,g):
    if q[6:] not in ((1,1,1),(2,2,2)):
        return False
    a=q[6]
    return (sum(q[:3])%3==0 and all(
        (q[3+v]+q[(v-g)%3]-2*a)%3==0 for v in F3))


def graph_potential(q,g):
    """Solve all 27 induced generator edges on the nine (v,z) vertices.

    The adjacency list also includes reverse edges, with negative voltage;
    cycle inconsistencies rule out a potential regardless of its form.
    """
    adj={(v,z):[] for v,z in product(F3, repeat=2)}
    for u,v,z in product(F3,repeat=3):
        a=(v,z)
        b=((v+g*(u+1))%3,(z+q[3*u+v])%3)
        adj[a].append((b,1))
        adj[b].append((a,2))
    assigned={}
    for root in adj:
        if root in assigned:
            continue
        assigned[root]=0
        waiting=[root]
        while waiting:
            source=waiting.pop()
            for target,increment in adj[source]:
                needed=(assigned[source]+increment)%3
                if target in assigned:
                    if assigned[target]!=needed:
                        return None
                else:
                    assigned[target]=needed
                    waiting.append(target)
    return assigned


def symbolic_alpha(q,g):
    a=q[6]
    inv=pow(a,-1,3)
    alpha=[0,0,0]
    for i in range(2):
        v=(i*g)%3
        alpha[(v+g)%3]=(alpha[v]+1-inv*q[v])%3
    return tuple(alpha)


def action(state,q,g,b,c,letter):
    values=list(state)
    if letter=="A":
        values[0]=(state[0]+1)%3
    else:
        u,v,z=state[:3]
        values[1]=(v+g*(u+1))%3
        values[2]=(z+q[3*u+v])%3
        if len(state)>3:values[3]=(state[3]+b*z)%3
        if len(state)>4:values[4]=(state[4]+c*z)%3
    return tuple(values)


def corrected(state,r,q,g,b,c,alpha):
    out=list(state)
    u,v,z=state[:3]
    a=q[6]
    inverse=pow(a,-1,3)
    phase=(r*(inverse*z+alpha[v])+inverse*(r*(r-1)//2))%3
    out[2]=(z+r)%3
    if len(state)>3:out[3]=(state[3]+b*phase)%3
    if len(state)>4:out[4]=(state[4]+c*phase)%3
    return tuple(out)


def audit():
    totals=Counter()
    admitted={}
    for g in (1,2):
        for q in product(F3,repeat=9):
            algebraic=algebraic_admission(q,g)
            graph=graph_potential(q,g)
            if algebraic != (graph is not None):
                raise AssertionError(('graph contradicts algebra',g,q,algebraic))
            totals['total_tables']+=1
            if algebraic:
                totals['admitted']+=1
                admitted.setdefault(g,[]).append(q)
            else:
                totals['obstructed']+=1
        if len(admitted.get(g,[]))!=18:
            raise AssertionError(('admission cardinality is not 18',g,len(admitted.get(g,[]))))
    # Exhaustively validate an actual nonconstant family: BOTH gains,
    # every admitted q0 table, all 8 nonzero (b,c) pairs, dimensions 3..6,
    # all states, two generator labels, plus correction group law.
    for g in (1,2):
        for q in admitted[g]:
            alpha=symbolic_alpha(q,g)
            for u,v,z in product(F3,repeat=3):
                new_v=(v+g*(u+1))%3
                new_z=(z+q[3*u+v])%3
                old_phi=(pow(q[6],-1,3)*z+alpha[v])%3
                new_phi=(pow(q[6],-1,3)*new_z+alpha[new_v])%3
                if (new_phi-old_phi)%3!=1:
                    raise AssertionError(('invalid potential',g,q,u,v,z))
                totals['potential_equations']+=1
            for b,c in product(F3,repeat=2):
                if (b,c)==(0,0):continue
                for d in range(3,7):
                    for state in product(F3,repeat=d):
                        for r in F3:
                            for letter in 'AB':
                                lhs=corrected(action(state,q,g,b,c,letter),r,q,g,b,c,alpha)
                                rhs=action(corrected(state,r,q,g,b,c,alpha),q,g,b,c,letter)
                                if lhs!=rhs:
                                    raise AssertionError(('commutation',g,q,b,c,d,state,r,letter))
                                totals['commutation_equations']+=1
                            for s in F3:
                                lhs=corrected(corrected(state,r,q,g,b,c,alpha),s,q,g,b,c,alpha)
                                rhs=corrected(state,(r+s)%3,q,g,b,c,alpha)
                                if lhs!=rhs:
                                    raise AssertionError(('group law',g,q,b,c,d,state,r,s))
                                totals['group_equations']+=1
    expected={'total_tables':2*(3**9),'admitted':36,'obstructed':2*((3**9)-18),
              'potential_equations':36*27,
              'commutation_equations':36*8*(3+9+27+81)*3*2,
              'group_equations':36*8*(3+9+27+81)*3*3}
    # 3+9+27+81 are F3^(d-2) for d=3..6 times a universal F3^2
    # lower-state factor. Use explicit 3^d as the count.
    states=sum(3**d for d in range(3,7))
    expected['commutation_equations']=36*8*states*3*2
    expected['group_equations']=36*8*states*3*3
    if dict(totals)!=expected:
        raise AssertionError(('unexpected independent audit counts',dict(totals),expected))
    return {'status':'COMPLETE_DECLARED_TABLE_AUDIT',
            'counts':dict(totals),
            'admitted_per_gain':18,
            'obstruction_method':'signed lower-state cycle voltage'}


if __name__=='__main__':
    print(audit())
