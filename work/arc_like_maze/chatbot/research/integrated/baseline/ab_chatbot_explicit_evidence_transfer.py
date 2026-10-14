"""Explicit, auditable finite evidence transfer between independently witnessed joins.

Only already-observed donor edges may enter a NEW derived partial relation. Two joins
must share the EXACT local pin registry and old/new owner-bound observer objects.
This is not an identity transport across distinct source versions or owners.
Neither join is mutated and each is zero-read re-audited on every access.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_joint_witness_binding import canonical_digest
from ab_chatbot_joint_evidence_task import JointEvidenceTask

ROOT=(0,0,0)
READY='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED'

@dataclass(frozen=True)
class TransferConflict:
    cause: str
    source_state: tuple
    action: str
    conflicting_old: tuple
    conflicting_new: tuple
    retained_word: str
    donor_word: str
    old_equal: bool
    new_equal: bool

@dataclass(frozen=True)
class TransferReport:
    status: str
    recipient_digest: str | None
    donor_digest: str | None
    derived_digest: str | None
    state_pairs: tuple
    admitted_edges: tuple
    provenance: tuple
    obstruction: TransferConflict | None
    old_observed: int
    new_observed: int
    detail: str


def _root_paths(edges):
    paths={ROOT:''}
    frontier=[ROOT]
    by_source={}
    for s,a,t,ns,nt in edges:
        by_source.setdefault(s,[]).append((a,t))
    for s in frontier:
        for a,t in sorted(by_source.get(s,())):
            if t not in paths:
                paths[t]=paths[s]+a
                frontier.append(t)
    return paths


class ExplicitEvidenceTransfer:
    """User-declared edge selection; no implicit all-edge transport or extension."""
    def __init__(self, recipient: CrossPinJoin, donor: CrossPinJoin, declaration: Any):
        self.recipient,self.donor=recipient,donor
        self.status='INVALID_TRANSFER'
        self.expected=()
        self.edge_keys=()
        if not (isinstance(recipient,CrossPinJoin) and isinstance(donor,CrossPinJoin)
                and donor is not recipient and type(declaration) is dict
                and set(declaration)=={'recipient_fingerprint','donor_fingerprint','transfer_edges'}):
            return
        x,y=declaration['recipient_fingerprint'],declaration['donor_fingerprint']
        requested=declaration['transfer_edges']
        if not (type(x) is str and type(y) is str and len(x)==len(y)==64
                and all(ch in '0123456789abcdef' for ch in x+y)
                and type(requested) is list and 1<=len(requested)<=16):
            return
        keys=[]
        for item in requested:
            if not (type(item) is dict and set(item)=={'state','action'}
                    and type(item['state']) is list and len(item['state'])==3
                    and all(type(n) is int and n in (0,1,2) for n in item['state'])
                    and item['action'] in ('A','B')):
                return
            keys.append((tuple(item['state']),item['action']))
        if len(set(keys))!=len(keys):
            return
        self.expected=(x,y)
        self.edge_keys=tuple(keys)
        self.status='TRANSFER_ACCEPTED'

    def advance(self)->TransferReport:
        empty=()
        if self.status!='TRANSFER_ACCEPTED':
            return TransferReport(self.status,None,None,None,empty,empty,empty,None,0,0,'Explicit transfer declaration invalid.')
        # Pin identity of the SAME two local owner-held snapshots, not merely a label/version.
        if not (self.recipient.registry is self.donor.registry
                and self.recipient.old is self.donor.old
                and self.recipient.new is self.donor.new):
            return TransferReport('TRANSFER_SOURCE_SCOPE_UNPROVED',*self.expected,None,empty,empty,empty,None,0,0,
                'Source owner/registry objects differ; no transport witness across them.')
        base=self.recipient.advance(max_new_edges=0)
        added=self.donor.advance(max_new_edges=0)
        observed=(max(base.old_observed,added.old_observed),max(base.new_observed,added.new_observed))
        for name,r in (('recipient',base),('donor',added)):
            if r.status!=READY:
                return TransferReport(r.status,*self.expected,None,empty,empty,empty,None,*observed,
                    name+' is not a currently verified compatible join: '+r.details)
        if base.pins!=added.pins or base.versions!=added.versions:
            return TransferReport('TRANSFER_SOURCE_SCOPE_UNPROVED',*self.expected,None,empty,empty,empty,None,*observed,
                                  'Pinned historical source referents differ.')
        bx,dy=canonical_digest(base),canonical_digest(added)
        if (bx,dy)!=self.expected:
            return TransferReport('WITNESS_FINGERPRINT_MISMATCH',bx,dy,None,empty,empty,empty,None,*observed,
                                  'Named witness does not match current replayed join.')
        f=dict(base.state_pairs); reverse={n:s for s,n in f.items()}
        edges={(s,a):(s,a,t,ns,nt) for s,a,t,ns,nt in base.admitted_edges}
        donor_edges={(s,a):(s,a,t,ns,nt) for s,a,t,ns,nt in added.admitted_edges}
        evidence={(s,a):('recipient',) for s,a in edges}
        original_roots=_root_paths(base.admitted_edges)
        donor_roots=_root_paths(added.admitted_edges)
        for key in self.edge_keys:
            if key not in donor_edges:
                return TransferReport('TRANSFER_EDGE_UNPROVED',bx,dy,None,empty,empty,empty,None,*observed,
                                      'Requested donor edge is not in its currently admitted history: '+repr(key))
            s,a,t,ns,nt=donor_edges[key]
            reachable=_root_paths(edges.values())
            if s not in reachable:
                return TransferReport('TRANSFER_UNROOTED',bx,dy,None,empty,empty,empty,None,*observed,
                    'Transferred edge requires an unadmitted prefix: '+repr(key))
            if f.get(s)!=ns:
                # Donor cannot change an existing source image, even for a newly named edge.
                return TransferReport('TRANSFER_STATE_CONFLICT',bx,dy,None,empty,empty,empty,
                    TransferConflict('SOURCE_PAIR_CONFLICT',s,a,s,(f.get(s),ns),reachable[s],donor_roots[s],True,False),
                    *observed,'Transferred source state image conflicts with recipient pairing.')
            if key in edges and edges[key] != (s,a,t,ns,nt):
                return TransferReport('TRANSFER_EDGE_CONFLICT',bx,dy,None,empty,empty,empty,None,*observed,
                                      'Same labeled edge has different independently retained endpoints.')
            if t in f and f[t]!=nt:
                left=original_roots.get(t) or reachable.get(t)
                right=donor_roots[t]
                certificate=TransferConflict('SOURCE_STATE_CONFLICT',s,a,t,(f[t],nt),left,right,True,False)
                return TransferReport('TRANSFER_STATE_CONFLICT',bx,dy,None,empty,empty,empty,certificate,*observed,
                                      'Two witnessed histories give one old state different new images.')
            if nt in reverse and reverse[nt]!=t:
                previous=reverse[nt]
                left=original_roots.get(previous) or reachable.get(previous)
                right=donor_roots[t]
                certificate=TransferConflict('TARGET_STATE_CONFLICT',s,a,(previous,t),nt,left,right,False,True)
                return TransferReport('TRANSFER_STATE_CONFLICT',bx,dy,None,empty,empty,empty,certificate,*observed,
                                      'Distinct old states collide in new source image.')
            f[t]=nt;reverse[nt]=t
            edges[key]=(s,a,t,ns,nt)
            evidence[key]=tuple(sorted(set(evidence.get(key,())+('donor',))))
        if len(_root_paths(edges.values()))!=len(f):
            return TransferReport('TRANSFER_UNROOTED',bx,dy,None,empty,empty,empty,None,*observed,
                                  'A mapped state has no admitted rooted path.')
        provenance=tuple(sorted((s,a,evidence[(s,a)]) for s,a in edges))
        pairs=tuple(sorted(f.items())); admitted=tuple(sorted(edges.values()))
        material={'format':'witnessed-partial-transfer/v1','recipient':bx,'donor':dy,
                  'selected_edges':self.edge_keys,'state_pairs':pairs,
                  'admitted_edges':admitted,'provenance':provenance}
        digest=sha256(json.dumps(material,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        # A second zero-read audit catches any changing pin/cache before success.
        final_rec=self.recipient.advance(max_new_edges=0)
        final_don=self.donor.advance(max_new_edges=0)
        if (final_rec.status!=READY or final_don.status!=READY or
                canonical_digest(final_rec)!=bx or canonical_digest(final_don)!=dy):
            return TransferReport('TRANSFER_EVIDENCE_WITHDRAWN',bx,dy,None,empty,empty,empty,None,*observed,
                                  'Underlying evidence failed its final audit.')
        return TransferReport('TRANSFER_PARTIAL_CORRESPONDENCE_WITNESSED',bx,dy,digest,
                              pairs,admitted,provenance,None,*observed,
                              'Explicitly selected donor edges joined to recipient pairing; no new observations.')


@dataclass(frozen=True)
class TransferredTaskResult:
    status: str
    transfer: TransferReport
    obligations: tuple


class TransferredEvidenceTask:
    def __init__(self, transfer:ExplicitEvidenceTransfer, declaration:Any):
        self.transfer=transfer
        self.status='INVALID_TASK'
        self.expected=None
        self.task=None
        if not isinstance(transfer,ExplicitEvidenceTransfer) or type(declaration) is not dict:
            return
        allowed={'transfer_fingerprint','goals','required_edges',
                 'required_paths','required_destinations'}
        if set(declaration)-allowed:
            return
        contract={k:v for k,v in declaration.items() if k!='transfer_fingerprint'}
        candidate=declaration.get('transfer_fingerprint')
        if (type(candidate) is not str or len(candidate)!=64 or
                any(ch not in '0123456789abcdef' for ch in candidate)):
            return
        task=JointEvidenceTask(transfer.recipient,contract)
        if task.status!='TASK_ACCEPTED':
            self.status=task.status
            return
        self.expected=candidate
        self.task=task
        self.status='TASK_ACCEPTED'

    def advance(self):
        report=self.transfer.advance()
        if self.status!='TASK_ACCEPTED':
            return TransferredTaskResult(self.status,report,())
        if report.status!='TRANSFER_PARTIAL_CORRESPONDENCE_WITNESSED':
            return TransferredTaskResult(report.status,report,())
        if report.derived_digest!=self.expected:
            return TransferredTaskResult('TRANSFER_FINGERPRINT_MISMATCH',report,())
        f=dict(report.state_pairs)
        edges={(s,a):(t,ns,nt) for s,a,t,ns,nt in report.admitted_edges}
        checks=[]
        for s in self.task.goals:checks.append(('GOAL',s,s in f))
        for s,a in self.task.edges:checks.append(('EDGE',(s,a),(s,a) in edges))
        for word,os,ns in self.task.paths:
            s=t=ROOT; valid=True
            for a in word:
                e=edges.get((s,a))
                if e is None or e[1]!=t:
                    valid=False;break
                s,t=e[0],e[2]
            checks.append(('PATH',(word,os,ns),valid and (s,t)==(os,ns)))
        for s,n in self.task.destinations:
            checks.append(('DESTINATION',(s,n),f.get(s)==n))
        return TransferredTaskResult('TASK_COMPLETED_ON_TRANSFER_WITNESS' if all(row[2] for row in checks)
                                     else 'TASK_REQUIREMENTS_UNPROVED',report,tuple(checks))
