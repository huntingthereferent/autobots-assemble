"""Complete-law reference: task consumes ONE finite route's already admitted edges.

No owner verification here. The integrated route-bound task replays local owner
snapshots and preserves its separately pinned evidence checks.
"""
from dataclasses import dataclass
from finite_goal_priority import ROOT
from finite_two_hop_transport import chain

@dataclass(frozen=True)
class OneRouteFiniteResult:
    status: str
    route_status: str
    satisfied: tuple
    pairs: tuple
    edges: tuple


def evaluate(route, *, goals=(), edges=(), paths=(), destinations=()):
    """Strict declared objective; route is one independently replayed Chain."""
    if not (goals or edges or paths or destinations):
        raise ValueError('nonempty task required')
    if route.status!='TWO_HOP_CHAIN_WITNESSED':
        return OneRouteFiniteResult('ROUTE_UNPROVED',route.status,(),(),())
    f=dict(route.state_pairs)
    admitted={(s,a):(target,ns,nt) for s,a,target,ns,nt in route.admitted_edges}
    outcomes=[]
    for s in goals:outcomes.append(('GOAL',s,s in f))
    for s,a in edges:outcomes.append(('EDGE',(s,a),(s,a) in admitted))
    for word,old_end,new_end in paths:
        s=ns=ROOT;ok=True
        if type(word) is not str or not word or len(word)>12 or any(a not in 'AB' for a in word):
            raise ValueError('explicit bounded A/B word required')
        for a in word:
            edge=admitted.get((s,a))
            if edge is None or f.get(s)!=ns or edge[1]!=ns:
                ok=False;break
            s,ns=edge[0],edge[2]
        outcomes.append(('PATH',word,ok and (s,ns)==(old_end,new_end)))
    for s,t in destinations:outcomes.append(('DESTINATION',(s,t),f.get(s)==t))
    return OneRouteFiniteResult('TASK_COMPLETED_ON_SELECTED_ROUTE'
        if all(x[2] for x in outcomes) else 'ROUTE_TASK_REQUIREMENTS_UNPROVED',
        route.status,tuple(outcomes),route.state_pairs,route.admitted_edges)


def fixture(side='left'):
    from test_finite_two_route_comparison import setup
    d=setup()
    if side not in ('left','right'):raise ValueError('explicit route selection required')
    middle=d['middle_left' if side=='left' else 'middle_right']
    words=d['middle_words_left' if side=='left' else 'middle_words_right']
    maps=d['maps_left' if side=='left' else 'maps_right']
    return chain(d['donor'],middle,d['final'],d['donor_words'],words,
                 d['final_words'],d['selected'],*maps)

if __name__=='__main__':
    for side in ('left','right'):
        report=fixture(side)
        selected=((1,0,0),'B') if side=='left' else ((0,1,2),'B')
        result=evaluate(report,edges=(selected,))
        print(side,report.status,result.status,len(report.state_pairs),len(report.admitted_edges))
