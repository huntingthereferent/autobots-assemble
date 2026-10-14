"""Explicit selected-edge intertwining between DIFFERENT pinned join source scopes.

No donor observation is copied as a recipient observation. A selected donor edge
must be independently observed under BOTH recipient sources and its explicitly
provided old-state and new-state maps must commute with those two actions.
This is a scoped local mathematical/evidential comparison, not remote auth.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import canonical_digest
from ab_chatbot_language_bridge import ObservationWall, EdgeBudgetReached

READY = 'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED'
ROOT = (0,0,0)

@dataclass(frozen=True)
class CrossScopeTransportReport:
    status: str
    recipient_fingerprint: str | None
    donor_fingerprint: str | None
    derived_fingerprint: str | None
    state_pairs: tuple
    admitted_edges: tuple
    selected_square: tuple
    obstruction: tuple | None
    recipient_old_observed: int
    recipient_new_observed: int
    donor_old_observed: int
    donor_new_observed: int
    detail: str


def _state(value):
    return (type(value) is list and len(value)==3 and
            all(type(n) is int and n in (0,1,2) for n in value))


def _explicit_map(data):
    if type(data) is not list or not 2<=len(data)<=16:return None
    result={}
    reverse={}
    for entry in data:
        if not (type(entry) is dict and set(entry)=={'donor','recipient'} and
                _state(entry['donor']) and _state(entry['recipient'])):return None
        s,t=tuple(entry['donor']),tuple(entry['recipient'])
        if s in result or t in reverse:return None
        result[s]=t;reverse[t]=s
    return result


class CrossScopeIntertwiningTransfer:
    """Single-edge transfer certificate with explicitly declared TWO state maps."""
    def __init__(self, recipient:CrossPinJoin,donor:CrossPinJoin,declaration:Any):
        self.recipient,self.donor=recipient,donor
        self.status='INVALID_TRANSPORT'
        self.expected=()
        self.edge=None
        self.old_map={}
        self.new_map={}
        if not (isinstance(recipient,CrossPinJoin) and isinstance(donor,CrossPinJoin)
                and recipient is not donor and type(declaration) is dict and
                set(declaration)=={'recipient_fingerprint','donor_fingerprint',
                                   'selected_donor_edge','old_state_transport','new_state_transport'}):return
        x,y=declaration['recipient_fingerprint'],declaration['donor_fingerprint']
        k=declaration['selected_donor_edge']
        fo=_explicit_map(declaration['old_state_transport'])
        gn=_explicit_map(declaration['new_state_transport'])
        if not (type(x) is str and type(y) is str and len(x)==len(y)==64 and
                all(c in '0123456789abcdef' for c in x+y) and type(k) is dict and
                set(k)=={'state','action'} and _state(k['state']) and
                type(k['action']) is str and k['action'] in ('A','B') and
                fo is not None and gn is not None):return
        self.expected=x,y
        self.edge=tuple(k['state']),k['action']
        self.old_map=fo;self.new_map=gn
        self.status='TRANSPORT_DECLARED'

    def advance(self):
        empty=()
        def report(status,rx=None,dy=None,digest=None,pairs=(),edges=(),square=(),ob=None,
                   counts=(0,0,0,0),detail=''):
            return CrossScopeTransportReport(status,rx,dy,digest,tuple(pairs),tuple(edges),
                                             tuple(square),ob,*counts,detail)
        if self.status!='TRANSPORT_DECLARED':
            return report(self.status,detail='Invalid explicit cross-scope transport declaration.')
        # No implicit transfer for same original and changed owner/snapshot pair;
        # earlier same-pin transfer contract handles that separate case.
        if (self.recipient.old is self.donor.old and self.recipient.new is self.donor.new):
            return report('TRANSPORT_SCOPE_UNCHANGED',*self.expected,
                          detail='Use same-pin transfer for identical source objects.')
        recipient=self.recipient.advance(max_new_edges=0)
        donor=self.donor.advance(max_new_edges=0)
        def counts():
            return (len(self.recipient.old.snapshot.edges),len(self.recipient.new.snapshot.edges),
                    len(self.donor.old.snapshot.edges),len(self.donor.new.snapshot.edges))
        if recipient.status!=READY or donor.status!=READY:
            invalid=recipient if recipient.status!=READY else donor
            return report(invalid.status,*self.expected,counts=counts(),
                          detail='One pinned source join failed the current zero-read replay.')
        rx,dy=canonical_digest(recipient),canonical_digest(donor)
        if (rx,dy)!=self.expected:
            return report('WITNESS_FINGERPRINT_MISMATCH',rx,dy,counts=counts(),
                          detail='The current joins differ from the named fingerprints.')
        donor_edges={(s,a):(s,a,t,ns,nt) for s,a,t,ns,nt in donor.admitted_edges}
        if self.edge not in donor_edges:
            return report('TRANSPORT_DONOR_EDGE_UNPROVED',rx,dy,counts=counts(),
                          detail='Selected donor edge was not witnessed.')
        ds,a,dt,dns,dnt=donor_edges[self.edge]
        fo,gn=self.old_map,self.new_map
        if set(fo)!={ds,dt} or set(gn)!={dns,dnt}:
            return report('TRANSPORT_MAPPING_INCOMPLETE',rx,dy,counts=counts(),
                          detail='Selected donor edge endpoints require exactly their own explicit maps; unrelated mappings are not witnessed.')
        rs,rt,rns,rnt=fo[ds],fo[dt],gn[dns],gn[dnt]
        forward=dict(recipient.state_pairs)
        reverse={v:k for k,v in forward.items()}
        if forward.get(rs)!=rns:
            return report('TRANSPORT_PREFIX_UNPROVED',rx,dy,counts=counts(),
                          detail='Mapped old/new source states are not a rooted recipient state pair.')
        old_bridge,new_bridge=self.recipient.old,self.recipient.new
        try:
            actual_old=old_bridge.snapshot.step(rs,a)
            actual_new=new_bridge.snapshot.step(rns,a)
        except EdgeBudgetReached:
            return report('UNKNOWN_BUDGET',rx,dy,counts=counts(),
                          detail='Recipient cannot independently observe both required edges within budget.')
        except (ObservationWall,ValueError,OSError,KeyError) as e:
            return report('WALL_OBSERVATION',rx,dy,counts=counts(),
                          detail='Recipient transition observation failed: '+str(e))
        square=((ds,a,dt,dns,dnt),(rs,a,actual_old,rns,actual_new),
                (rs,rt,rns,rnt))
        # Audit the exact two new observations, even if they already appeared in
        # a cache, not merely if they were fetched for the first time.
        try:
            verified=(old_bridge._scope(old_bridge.snapshot)=='LOCAL_OWNER_VERIFIED' and
                      new_bridge._scope(new_bridge.snapshot)=='LOCAL_OWNER_VERIFIED' and
                      old_bridge.snapshot.owner_view is not None and
                      new_bridge.snapshot.owner_view is not None and
                      actual_old==old_bridge.snapshot.owner_view.step(rs,a) and
                      actual_new==new_bridge.snapshot.owner_view.step(rns,a))
        except (ObservationWall,ValueError,AttributeError,KeyError):verified=False
        if not verified:
            return report('WALL_OBSERVATION',rx,dy,square=square,counts=counts(),
                          detail='Recipient cached transition failed local owner replay.')
        if (actual_old,actual_new)!=(rt,rnt):
            return report('TRANSPORT_INTERTWINING_CONFLICT',rx,dy,square=square,
                          ob=((rt,actual_old),(rnt,actual_new)),counts=counts(),
                          detail='Explicit state maps do not intertwine the selected action on both sources.')
        if (rt in forward and forward[rt]!=rnt) or (rnt in reverse and reverse[rnt]!=rt):
            return report('TRANSPORT_PAIR_CONFLICT',rx,dy,square=square,
                          ob=(rt,rnt,forward.get(rt),reverse.get(rnt)),counts=counts(),
                          detail='Mapped target violates recipient partial-bijection assignments.')
        forward[rt]=rnt
        edges={(s,k):(s,k,t,ns,nt) for s,k,t,ns,nt in recipient.admitted_edges}
        edge=(rs,a,rt,rns,rnt)
        if (rs,a) in edges and edges[(rs,a)]!=edge:
            return report('TRANSPORT_EDGE_CONFLICT',rx,dy,square=square,counts=counts())
        edges[rs,a]=edge
        pairs=tuple(sorted(forward.items()));admitted=tuple(sorted(edges.values()))
        # Re-audit both joins and the two recipient cached edges at final read.
        rep2=self.recipient.advance(max_new_edges=0)
        don2=self.donor.advance(max_new_edges=0)
        if rep2.status!=READY or don2.status!=READY or canonical_digest(rep2)!=rx or canonical_digest(don2)!=dy:
            return report('TRANSPORT_EVIDENCE_WITHDRAWN',rx,dy,counts=counts())
        try:
            if (old_bridge.snapshot.owner_view.step(rs,a)!=old_bridge.snapshot.edges[rs,a] or
                new_bridge.snapshot.owner_view.step(rns,a)!=new_bridge.snapshot.edges[rns,a]):
                return report('WALL_OBSERVATION',rx,dy,counts=counts())
        except (AttributeError,KeyError):return report('WALL_OBSERVATION',rx,dy,counts=counts())
        digest=sha256(json.dumps({'type':'finite-cross-scope-transport/v1',
            'recipient':rx,'donor':dy,'selected_edge':self.edge,
            'old_map':tuple(sorted(fo.items())),'new_map':tuple(sorted(gn.items())),
            'square':square,'state_pairs':pairs,'admitted_edges':admitted},
            sort_keys=True,separators=(',',':')).encode()).hexdigest()
        return report('CROSS_SCOPE_INTERTWINING_WITNESSED',rx,dy,digest,pairs,admitted,
                      square,None,counts(),
                      'Selected old/new edges independently replayed at recipient owner pins; no donor edge copied.')


@dataclass(frozen=True)
class CrossScopeTaskResult:
    status: str
    report: CrossScopeTransportReport
    obligations: tuple


class CrossScopeTransportTask:
    """Explicit task on ONLY the exact, newly audited four-scope transport."""
    def __init__(self, transport:CrossScopeIntertwiningTransfer, declaration:Any):
        from ab_chatbot_joint_evidence_task import JointEvidenceTask
        self.transport=transport
        self.status='INVALID_TASK'
        self.expected=None
        self.task=None
        if not (isinstance(transport,CrossScopeIntertwiningTransfer) and
                type(declaration) is dict and
                set(declaration)<={'cross_scope_fingerprint','goals','required_edges',
                                   'required_paths','required_destinations'}):return
        digest=declaration.get('cross_scope_fingerprint')
        if not (type(digest) is str and len(digest)==64 and
                all(c in '0123456789abcdef' for c in digest)):return
        old_task={k:v for k,v in declaration.items() if k!='cross_scope_fingerprint'}
        parsed=JointEvidenceTask(transport.recipient,old_task)
        self.status=parsed.status
        if parsed.status!='TASK_ACCEPTED':return
        self.expected,self.task=digest,parsed

    def advance(self):
        report=self.transport.advance()
        if self.task is None:return CrossScopeTaskResult(self.status,report,())
        if report.status!='CROSS_SCOPE_INTERTWINING_WITNESSED':
            return CrossScopeTaskResult(report.status,report,())
        if report.derived_fingerprint!=self.expected:
            return CrossScopeTaskResult('WITNESS_FINGERPRINT_MISMATCH',report,())
        f=dict(report.state_pairs)
        admitted={(s,a):(t,ns,nt) for s,a,t,ns,nt in report.admitted_edges}
        checks=[]
        for s in self.task.goals:checks.append(('GOAL',s,s in f))
        for s,a in self.task.edges:checks.append(('EDGE',(s,a),(s,a) in admitted))
        for word,os,ns in self.task.paths:
            s=t=ROOT;valid=True
            for a in word:
                e=admitted.get((s,a))
                if e is None or e[1]!=t:valid=False;break
                s,t=e[0],e[2]
            checks.append(('PATH',(word,os,ns),valid and (s,t)==(os,ns)))
        for s,n in self.task.destinations:
            checks.append(('DESTINATION',(s,n),f.get(s)==n))
        return CrossScopeTaskResult('TASK_COMPLETED_ON_CROSS_SCOPE_WITNESS' if all(row[2] for row in checks)
                else 'TASK_REQUIREMENTS_UNPROVED',report,tuple(checks))
