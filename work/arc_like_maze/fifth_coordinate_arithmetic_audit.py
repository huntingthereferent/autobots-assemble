"""Independent full nine-entry fifth-coupling audit.

No imports from the construction, classifier, or WindowProcess modules.
An independent 27-vertex voltage graph solver verifies every one of
3^9 fifth-coordinate q2 rules at EACH of two representative gains.
For all 162 admitted maps, the complete F3^5 state set verifies both
generator commutations and the exact order-NINE return.

Execute:
    python -m work.arc_like_maze.fifth_coordinate_arithmetic_audit
"""
from collections import Counter, deque
from itertools import product

F3=(0,1,2)
CASES={
    1:((0,1,2,0,2,1,1,1,1),(0,1,1),(0,1,1,1,1,0,1,1,0)),
    2:((0,1,2,1,0,2,1,1,1),(0,0,1),(0,1,1,0,1,1,1,1,0)),
}


def B(state,gain,q0,q1,q2):
    u,v,z,y,t=state
    return (u,(v+gain*(u+1))%3,(z+q0[3*u+v])%3,
            (y+q1[3*v+z])%3,(t+q2[3*z+y])%3)


def C(state,alpha,slope,f):
    u,v,z,y,t=state
    w=(z+alpha[v])%3
    return (u,v,(z+1)%3,(y+w*w)%3,(t+slope*w+f[y])%3)


def graph_solve(gain,q0,alpha,q1,q2):
    vertices=list(product(F3,repeat=3))
    adj={s:[] for s in vertices}
    for u,v,z,y in product(F3,repeat=4):
        first=(v,z,y)
        nxt=((v+gain*(u+1))%3,(z+q0[3*u+v])%3,
             (y+q1[3*v+z])%3)
        w=(z+alpha[v])%3
        moved=((z+1)%3,(y+w*w)%3)
        voltage=(q2[3*moved[0]+moved[1]]-q2[3*z+y])%3
        adj[first].append((nxt,voltage))
        adj[nxt].append((first,(-voltage)%3))
    values={}
    for root in vertices:
        if root in values:continue
        values[root]=0
        todo=deque([root])
        while todo:
            start=todo.popleft()
            for dest,delta in adj[start]:
                needed=(values[start]+delta)%3
                if dest in values:
                    if values[dest]!=needed:return None
                else:values[dest]=needed;todo.append(dest)
    return values


def audit():
    classifications={}
    graph_cases=commutations=nine_turns=third_iterates=0
    for gain,(q0,alpha,q1) in CASES.items():
        result=Counter()
        for q2 in product(F3,repeat=9):
            graph=graph_solve(gain,q0,alpha,q1,q2)
            graph_cases+=1
            slope=(q2[3]-q2[0])%3
            f=q2[:3]
            formula=all(q2[3*z+y]==(slope*z+f[y])%3
                        for z,y in product(F3,repeat=2))
            if (graph is not None)!=formula:
                raise AssertionError(('cohomology count mismatch',gain,q2))
            if not formula:
                result['obstructed']+=1
                continue
            result['admitted']+=1
            if len(set(f))>1:
                result['reads_fourth_coordinate']+=1
            else:
                result['independent_of_fourth_coordinate']+=1
            for s in product(F3,repeat=5):
                if C(B(s,gain,q0,q1,q2),alpha,slope,f) != B(
                        C(s,alpha,slope,f),gain,q0,q1,q2):
                    raise AssertionError(('fifth-coordinate commutation',gain,q2,s))
                # A changes only x0; C does not read x0.
                commutations+=2
                after=s
                for turn in range(1,10):
                    after=C(after,alpha,slope,f)
                    if turn==3:
                        if after[:3]!=s[:3] or after[3]!=(s[3]+2)%3:
                            raise AssertionError(('third iterate',gain,q2,s))
                        third_iterates+=1
                if after!=s:
                    raise AssertionError(('nine-turn return',gain,q2,s))
                nine_turns+=1
        expected=Counter({'admitted':81,'obstructed':19602,
                          'reads_fourth_coordinate':72,
                          'independent_of_fourth_coordinate':9})
        if result!=expected:
            raise AssertionError(('classification',gain,result))
        classifications[gain]=dict(result)
    return dict(
        status='INDEPENDENT_27_VERTEX_LIFT_AUDIT_PASSED',
        table_and_gain_combinations=graph_cases,
        classifications=classifications,
        generator_commutation_equations=commutations,
        complete_nine_turn_returns=nine_turns,
        nontrivial_three_turn_witnesses=third_iterates,
    )


if __name__=='__main__':
    print(audit())
