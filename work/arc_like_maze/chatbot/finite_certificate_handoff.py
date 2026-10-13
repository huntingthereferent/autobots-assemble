"""CP-29 pure finite witness-transfer *reference*, not authenticated ownership.

A receipt is a prior route fingerprint+pin+edge summary. At the next call,
full finite laws and pins are provided again; no previous task result is reused.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from finite_shared_route_certificate import Route, Task, _valid_route, fixture


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class FiniteReceipt:
    route: str
    fingerprint: str
    pins_digest: str
    edges_digest: str


@dataclass(frozen=True)
class FiniteAcceptance:
    status: str
    tasks: tuple[tuple[str,str], ...]
    fresh_audits: int


def issue(route, law, current):
    if not _valid_route(route,route.name) or type(law) is not tuple or type(current) is not dict:
        raise ValueError('invalid finite issuing declaration')
    if any(current.get(s)!=pin for s,pin in route.pins) or any(e not in law for e in route.admitted):
        return None
    return FiniteReceipt(route.name,route.fingerprint,digest(route.pins),digest(route.admitted))


def accept(receipt,route,tasks,law,before,after):
    if (type(receipt) is not FiniteReceipt or not _valid_route(route,route.name) or
        type(tasks) is not dict or not 1<=len(tasks)<=16 or
        any(type(n) is not str or not n or type(t) is not Task or
            type(t.required) is not tuple or not t.required or
            any(type(e) is not tuple or len(e)!=2 or e[1] not in ('A','B') for e in t.required)
            for n,t in tasks.items()) or
        type(law) is not tuple or type(before) is not dict or type(after) is not dict):
        raise ValueError('invalid finite receiving declaration')
    if receipt.route!=route.name or receipt.fingerprint!=route.fingerprint:
        return FiniteAcceptance('HANDOFF_ROUTE_MISMATCH',(),0)
    # Mandatory NEW route audit; before/after pin identity and full-law checks.
    if any(before.get(s)!=after.get(s) for s,p in route.pins):
        return FiniteAcceptance('SOURCE_MOVED_DURING_HANDOFF',(),1)
    if any(before.get(s)!=p for s,p in route.pins) or any(e not in law for e in route.admitted):
        return FiniteAcceptance('HANDOFF_REAUDIT_UNPROVED',(),1)
    if receipt.pins_digest!=digest(route.pins) or receipt.edges_digest!=digest(route.admitted):
        return FiniteAcceptance('HANDOFF_EVIDENCE_CHANGED',(),1)
    outcomes=[]
    for name,t in tasks.items():
        status=('HANDOFF_ROUTE_MISMATCH' if t.route!=route.name or t.fingerprint!=route.fingerprint
                else 'TASK_COMPLETED_ON_SELECTED_ROUTE' if all(e in route.admitted for e in t.required)
                else 'ROUTE_TASK_REQUIREMENTS_UNPROVED')
        outcomes.append((name,status))
    return FiniteAcceptance('HANDOFF_FRESHLY_REVALIDATED',tuple(outcomes),1)


def fixture_handoff():
    r,t,law,pins=fixture()
    return r['left'],{'a':t['left_a'],'b':t['left_b']},law['left'],pins


if __name__=='__main__':
    route,tasks,law,pins=fixture_handoff()
    receipt=issue(route,law,pins)
    report=accept(receipt,route,tasks,law,pins,pins)
    print(report)
    assert report.status=='HANDOFF_FRESHLY_REVALIDATED'
    assert dict(report.tasks)=={name:'TASK_COMPLETED_ON_SELECTED_ROUTE' for name in tasks}
