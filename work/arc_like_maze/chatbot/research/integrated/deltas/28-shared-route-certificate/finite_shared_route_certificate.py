"""CP-28 independent complete-law reference for sharing one audited route.

No remote ownership, transport discovery, or cryptographic authentication: the
complete finite law and source pins are declared inputs. Only a *current* audited
route can be used, and each task keeps its own exact requirements.
"""
from dataclasses import dataclass
from finite_multi_task_dependency import plan


@dataclass(frozen=True)
class Route:
    name: str
    fingerprint: str
    pins: tuple[tuple[str,str], ...]
    admitted: tuple[tuple[str,str], ...]


@dataclass(frozen=True)
class Task:
    route: str
    fingerprint: str
    required: tuple[tuple[str,str], ...]


@dataclass(frozen=True)
class SharedResult:
    audited_routes: tuple[str,...]
    replayed_tasks: tuple[str,...]
    cached_tasks: tuple[str,...]
    status: tuple[tuple[str,str],...]


def _valid_route(r, n):
    return (type(r) is Route and r.name==n and type(r.fingerprint) is str
      and bool(r.fingerprint) and type(r.pins) is tuple and len(r.pins)>=1
      and len({s for s,p in r.pins})==len(r.pins)
      and all(type(s) is str and s and type(p) is str and p for s,p in r.pins)
      and type(r.admitted) is tuple and len(set(r.admitted))==len(r.admitted)
      and all(type(e) is tuple and len(e)==2 and type(e[0]) is str
              and type(e[1]) is str and e[1] in ('A','B') for e in r.admitted))


def evaluate(routes, tasks, complete_laws, pins_before, pins_after, *, changed=(), force=()):
    """Recompute each selected route audit once, check task constraints separately."""
    if (type(routes) is not dict or not routes or len(routes)>16 or
        any(not _valid_route(r,n) for n,r in routes.items()) or
        type(tasks) is not dict or not 2<=len(tasks)<=16 or
        any(type(n) is not str or not n or type(t) is not Task or
            t.route not in routes or type(t.fingerprint) is not str or
            type(t.required) is not tuple or not t.required or
            len(set(t.required))!=len(t.required) or
            any(type(e) is not tuple or len(e)!=2 or type(e[0]) is not str
                or type(e[1]) is not str or e[1] not in ('A','B') for e in t.required)
            for n,t in tasks.items()) or
        type(complete_laws) is not dict or set(complete_laws)!=set(routes) or
        any(type(v) is not tuple or len(set(v))!=len(v) for v in complete_laws.values()) or
        type(pins_before) is not dict or type(pins_after) is not dict):
        raise ValueError('invalid finite shared-certificate declaration')
    dependencies={name:tuple(s for s,p in routes[t.route].pins)
                  for name,t in tasks.items()}
    selection=plan(dependencies,changed,force=force)
    audited={};states={}
    for name,t in tasks.items():
        if name not in selection.replay:
            states[name]='CACHED_NOT_REPLAYED'
            continue
        r=routes[t.route]
        if t.route not in audited:
            pins_ok=all(pins_before.get(s)==pin for s,pin in r.pins)
            moved=any(pins_before.get(s)!=pins_after.get(s) for s,pin in r.pins)
            law_ok=all(edge in complete_laws[t.route] for edge in r.admitted)
            audited[t.route]=('SOURCE_MOVED_DURING_AUDIT' if moved else
                'SOURCE_PIN_UNPROVED' if not pins_ok else
                'ROUTE_EDGE_UNPROVED' if not law_ok else 'ROUTE_AUDITED')
        status=audited[t.route]
        states[name]=(status if status!='ROUTE_AUDITED' else
            'ROUTE_DECLARATION_CHANGED' if t.fingerprint!=r.fingerprint else
            'TASK_COMPLETED_ON_SELECTED_ROUTE' if all(e in r.admitted for e in t.required)
            else 'ROUTE_TASK_REQUIREMENTS_UNPROVED')
    return SharedResult(tuple(audited),selection.replay,selection.cached,
                        tuple((name,states[name]) for name in tasks))


def fixture():
    routes={
      'left':Route('left','left-pinned',(('donor','v1'),('left_middle','v1'),('final','v1')),
                   (('s0','B'),('s1','A'))),
      'right':Route('right','right-pinned',(('donor','v1'),('right_middle','v1'),('final','v1')),
                    (('r0','B'),))}
    tasks={'left_a':Task('left','left-pinned',(('s0','B'),)),
           'left_b':Task('left','left-pinned',(('s1','A'),)),
           'right_a':Task('right','right-pinned',(('r0','B'),))}
    laws={r.name:r.admitted for r in routes.values()}
    pins={'donor':'v1','left_middle':'v1','right_middle':'v1','final':'v1'}
    return routes,tasks,laws,pins


if __name__=='__main__':
    r,t,l,p=fixture()
    x=evaluate(r,t,l,p,p,force=('left_a','left_b'))
    print('routes audited:',x.audited_routes)
    print('tasks:',x.status)
    assert x.audited_routes==('left',)
    assert dict(x.status)['right_a']=='CACHED_NOT_REPLAYED'
