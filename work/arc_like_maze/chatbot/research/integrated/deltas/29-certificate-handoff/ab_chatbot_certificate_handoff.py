"""CP-29: cross-invocation route-certificate *reference*, never cached proof.

The portable receipt carries route and witness identities only. The receiver
MUST execute a NEW two-pass selected-route owner/pin audit and independently
check each receiving task's admitted obligations. A hash detects accidental
corruption but does not authenticate a sender or replace owner pin checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from ab_chatbot_shared_route_certificate import RouteAudit, audit_route, consume
from ab_chatbot_route_bound_task import RouteBoundTask, _route_evidence, _route_structure

_KIND = 'selected-route-handoff/v1'
_KEYS = frozenset({'kind', 'route', 'route_fingerprint', 'witness_sha256',
                   'source_sha256', 'receipt_sha256'})


def _digest(value):
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
    return sha256(raw.encode('utf-8')).hexdigest()


def _hex(x):
    return type(x) is str and len(x)==64 and all(c in '0123456789abcdef' for c in x)


def _witness(report):
    # Include full admitted relationships, not merely the route fingerprint.
    return _digest({'fingerprint':report.fingerprint,
                    'base_fingerprints':report.base_fingerprints,
                    'links':report.links,'state_pairs':report.state_pairs,
                    'admitted_edges':report.admitted_edges})


def _task_declared(t):
    if type(t) is not RouteBoundTask or t.status!='TASK_ACCEPTED' or t.task is None:
        return False
    q=t.task
    try:
        contract={'kind':'one-route-task/v1','chain':t.expected,'side':t.route_name,
                  'goals':q.goals,'edges':q.edges,'paths':q.paths,
                  'destinations':q.destinations}
        return q.status=='TASK_ACCEPTED' and _digest(contract)==t.task_fingerprint
    except (TypeError,AttributeError,ValueError):
        return False


def _bound(t):
    if not _task_declared(t):return False
    try:
        ix=0 if t.route_name=='left' else 1
        return (t._route is not None and t._comparison is t.refresh.comparison and
            getattr(t._comparison,t.route_name,None) is t._route and
            t._comparison.expected[ix]==t.expected and
            _route_structure(t._route)==t._structure)
    except (TypeError,AttributeError,ValueError,IndexError):
        return False


@dataclass(frozen=True)
class HandoffIssue:
    status: str
    receipt: str | None
    replay_calls: int
    detail: str


@dataclass(frozen=True)
class HandoffResult:
    status: str
    task_status: tuple[tuple[str,str], ...]
    usable: tuple[str, ...]
    replay_calls: int
    certificate: object | None
    detail: str

    @property
    def proof_for_use(self):
        return (bool(self.task_status) and self.status=='HANDOFF_FRESHLY_REVALIDATED'
                and len(self.usable)==len(self.task_status))


def _unpack(receipt):
    if type(receipt) is not str or len(receipt)>4096:return None
    try:
        obj=json.loads(receipt)
        if (type(obj) is not dict or set(obj)!=_KEYS or obj['kind']!=_KIND or
            obj['route'] not in ('left','right') or
            any(not _hex(obj[k]) for k in ('route_fingerprint','witness_sha256',
                                             'source_sha256','receipt_sha256'))):
            return None
        body={k:v for k,v in obj.items() if k!='receipt_sha256'}
        if _digest(body)!=obj['receipt_sha256']:return None
        return obj
    except (ValueError,TypeError,KeyError):
        return None


def issue_handoff(task):
    """Sender audits NOW and exports only an evidentiary *reference*."""
    if not _bound(task):
        return HandoffIssue('TASK_DECLARATION_CHANGED',None,0,'Task or selected source declaration changed.')
    try:
        before=_route_evidence(task._route)
        audit=audit_route(task)
        after=_route_evidence(task._route)
        if before!=after or not _bound(task):
            return HandoffIssue('SOURCE_MOVED_DURING_AUDIT',None,2,'Source moved while preparing handoff.')
        if audit.status!='TWO_HOP_CHAIN_WITNESSED' or audit.certificate is None:
            return HandoffIssue(audit.status,None,2,'Route could not issue a current witness.')
        body={'kind':_KIND,'route':task.route_name,
              'route_fingerprint':task.expected,
              'witness_sha256':_witness(audit.certificate),
              'source_sha256':_digest(after)}
        body['receipt_sha256']=_digest(body)
        return HandoffIssue('HANDOFF_REFERENCE_ISSUED',
            json.dumps(body,sort_keys=True,separators=(',',':')),2,
            'This is an untrusted portable reference, not proof-for-use in a later invocation.')
    except (TypeError,ValueError,AttributeError,KeyError,IndexError):
        return HandoffIssue('HANDOFF_ISSUE_EXCEPTION',None,0,'Malformed or moving sender evidence.')


def accept_handoff(receipt, named):
    """NEW invocation: re-audit one selected route, apply independent tasks.

    All tasks must select the exact same route object; no donor/final union and
    no borrowing from the neighboring route. No old task status is imported.
    """
    def fail(status,reason,replays=0,task_status=()):
        return HandoffResult(status,tuple(task_status),(),replays,None,reason)
    if (type(named) is not dict or not 1<=len(named)<=16 or
        any(type(k) is not str or not k.strip() or len(k)>80 or
            type(v) is not RouteBoundTask for k,v in named.items()) or
        len({id(v) for v in named.values()})!=len(named)):
        return fail('HANDOFF_INVALID_TASK_SET','Distinct named bound tasks required.')
    record=_unpack(receipt)
    if record is None:return fail('HANDOFF_INVALID_RECEIPT','Receipt malformed or checksum changed.')
    tasks=list(named.items()); first=tasks[0][1]
    if any(not _bound(t) for _,t in tasks):
        return fail('TASK_DECLARATION_CHANGED','Task admission or pinned relation has changed.')
    if (record['route']!=first.route_name or record['route_fingerprint']!=first.expected or
        any(t._route is not first._route or t.expected!=first.expected or
            t.route_name!=first.route_name for _,t in tasks)):
        return fail('HANDOFF_ROUTE_MISMATCH','Exact selected route and pin declaration required.')
    try:
        before=_route_evidence(first._route)
        audit=audit_route(first)   # Mandatory fresh two-pass owner-backed check.
        after=_route_evidence(first._route)
        if before!=after or any(not _bound(t) for _,t in tasks):
            return fail('SOURCE_MOVED_DURING_HANDOFF','Source or declaration moved in receiver.',2)
        if audit.status!='TWO_HOP_CHAIN_WITNESSED' or audit.certificate is None:
            return fail('HANDOFF_REAUDIT_UNPROVED',audit.status,2)
        if (record['source_sha256']!=_digest(after) or
            record['witness_sha256']!=_witness(audit.certificate)):
            return fail('HANDOFF_EVIDENCE_CHANGED','Previous receipt differs from fresh owner-backed evidence.',2)
        results=[]
        for name,t in tasks:
            q=consume(t,audit)
            if not _bound(t):
                return fail('SOURCE_MOVED_DURING_HANDOFF','Task mutated during obligation check.',2)
            results.append((name,q.status))
        if _route_evidence(first._route)!=after:
            return fail('SOURCE_MOVED_DURING_HANDOFF','Source moved during obligation checks.',2)
        usable=tuple(n for n,status in results if status=='TASK_COMPLETED_ON_SELECTED_ROUTE')
        return HandoffResult('HANDOFF_FRESHLY_REVALIDATED',tuple(results),usable,2,
                             audit.certificate,
                             'Only independently satisfied tasks are fresh; former tasks and claims are not imported.')
    except (TypeError,ValueError,AttributeError,KeyError,IndexError):
        return fail('HANDOFF_REVALIDATION_EXCEPTION','Malformed or moving receiver evidence.')
