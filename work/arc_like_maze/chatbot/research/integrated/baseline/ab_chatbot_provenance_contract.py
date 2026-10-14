"""Explicit source-proof obligations, composed onto the existing task chatbot.

A claimed HTTP source label, digest, version or matching finite path is NOT an
origin attestation.  Only the already-existing live local-owner binding may
satisfy LOCAL_OWNER_VERIFIED.  This never upgrades remote mathematical evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any

from ab_chatbot_mixed_obligations import MixedTaskSession, read_mixed_task
from ab_chatbot_multi_required import read_multi_task
from ab_chatbot_rule_change import _version
from ab_chatbot_language_bridge import ObservationWall

LOCAL = 'LOCAL_OWNER_VERIFIED'

@dataclass(frozen=True)
class ProvenanceRequirement:
    side: str
    scope: str

@dataclass(frozen=True)
class ProvenanceContract:
    required: tuple[ProvenanceRequirement, ...]
    base_fingerprint: str
    original_input: str
    fingerprint: str

@dataclass(frozen=True)
class ProvenanceIntake:
    status: str
    contract: ProvenanceContract | None
    base_input: object | None
    detail: str

@dataclass(frozen=True)
class SourceProof:
    side: str
    required: str
    observed: str
    satisfied: bool
    revision: tuple
    explanation: str

@dataclass(frozen=True)
class ProvenanceOutcome:
    status: str
    contract: ProvenanceContract | None
    source_proofs: tuple[SourceProof, ...]
    base_outcome: object | None
    detail: str


def read_provenance_task(raw: Any) -> ProvenanceIntake:
    """Only a structured, explicitly requested LOCAL_OWNER_VERIFIED obligation.

    Other obligations remain the unchanged responsibility of MixedTaskSession.
    """
    if type(raw) is not dict or 'required_provenance' not in raw:
        return ProvenanceIntake('NOT_PROVENANCE', None, raw,
                                'No new source-proof obligation declared.')
    requested=raw['required_provenance']
    if (type(requested) is not dict or not requested or
        set(requested)-{'old','new'} or
        any(type(v) is not str or v != LOCAL for v in requested.values())):
        return ProvenanceIntake('INVALID_TASK',None,None,
                   'required_provenance names one or both sides with LOCAL_OWNER_VERIFIED only.')
    base={k:v for k,v in raw.items() if k!='required_provenance'}
    mixed=read_mixed_task(base)
    if mixed.status=='NOT_MIXED':
        legacy=read_multi_task(base)
        status,source=legacy.status,legacy.contract
        detail=legacy.explanation
    else:
        status,source=mixed.status,mixed.contract
        detail=mixed.detail
    if source is None:
        return ProvenanceIntake(status,None,None,'Underlying task invalid: '+detail)
    required=tuple(ProvenanceRequirement(side,LOCAL) for side in ('old','new') if side in requested)
    normal={'base_fingerprint':source.fingerprint,
            'required_provenance':{r.side:r.scope for r in required}}
    digest=hashlib.sha256(json.dumps(normal,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    original=json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    contract=ProvenanceContract(required,source.fingerprint,original,digest)
    return ProvenanceIntake('TASK_ACCEPTED',contract,base,
                  'Source-proof demand recorded, not yet mathematically or locally verified.')


class ProvenanceTaskSession:
    """Provenance gate around the prior task session; no prior solver edits.

    Proof is re-evaluated on every advance, including completed zero-read
    replays. If it fails, return no old selected result or claimed success.
    """
    def __init__(self,old,new,task_input:Any,**kwargs):
        self.intake=read_provenance_task(task_input)
        self.old,self.new=old,new
        self._snapshots=(old.snapshot,new.snapshot)
        self._versions=(_version(old),_version(new))
        self._initial_scopes=(old.origin_scope,new.origin_scope)
        self.base=None
        if self.intake.status in ('TASK_ACCEPTED','NOT_PROVENANCE'):
            self.base=MixedTaskSession(old,new,self.intake.base_input,**kwargs)

    def _checks(self) -> tuple[SourceProof,...]:
        assert self.intake.contract is not None
        answer=[]
        # Refresh BOTH labels, including the side not explicitly demanded.
        # Loss of a live owner binding must downgrade future math labels too.
        # Conversely, a formerly remote origin cannot be upgraded without a
        # new explicit pin, even if owner metadata is later reattached.
        current_by_side={}
        for side,bridge,initial in zip(('old','new'),(self.old,self.new),self._initial_scopes):
            current=bridge._scope(bridge.snapshot)
            if initial != LOCAL:
                current='REMOTE_ORIGIN_UNVERIFIED'
            bridge.origin_scope=current
            current_by_side[side]=current
        for r in self.intake.contract.required:
            bridge=self.old if r.side=='old' else self.new
            current=current_by_side[r.side]
            yes=current==r.scope
            answer.append(SourceProof(r.side,r.scope,current,yes,
                          _version(bridge),
                          ('Bound in-process local owner and matching pinned version'
                           if yes else 'Live verified owner binding unavailable; remote labels are not proof')))
        return tuple(answer)

    def advance(self,*,max_new_edges=108) -> ProvenanceOutcome:
        if self.base is None:
            return ProvenanceOutcome(self.intake.status,None,(),None,self.intake.detail)
        if self.intake.contract is None:
            result=self.base.advance(max_new_edges=max_new_edges)
            return ProvenanceOutcome(result.status,None,(),result,
                                    'No source-proof constraint was introduced.')
        if (self.old.snapshot is not self._snapshots[0] or
              self.new.snapshot is not self._snapshots[1] or
              (_version(self.old),_version(self.new))!=self._versions):
            return ProvenanceOutcome('UNKNOWN_VERSION',self.intake.contract,(),None,
                                    'Pinned source versions changed: no completion admitted.')
        try:
            checks=self._checks()
        except (ObservationWall,ValueError,KeyError,AttributeError) as e:
            return ProvenanceOutcome('WALL_OBSERVATION',self.intake.contract,(),None,
                                    'Unable to replay live owner binding: '+str(e))
        if not all(c.satisfied for c in checks):
            return ProvenanceOutcome('PROVENANCE_UNPROVED',self.intake.contract,checks,None,
                   'Declared local-owner evidence unavailable. No task transitions requested.')
        result=self.base.advance(max_new_edges=max_new_edges)
        # Some older mixed portfolios cache each trial's original status. They
        # replay the math, but could reconstruct a WITNESSED suffix from that
        # cached trial even after an unrequired side has lost its local owner.
        # Provenance status is authoritative here, not those old cached labels.
        both_local=(self.old.origin_scope==LOCAL and self.new.origin_scope==LOCAL)
        if not both_local and result.status.endswith('_WITNESSED'):
            downgraded=result.status[:-len('_WITNESSED')]+'_REMOTE_REPORTED'
            nested=getattr(result,'report',None)
            if nested is not None:
                nested=replace(nested,status=downgraded)
                result=replace(result,status=downgraded,report=nested)
            else:
                result=replace(result,status=downgraded)
        return ProvenanceOutcome(result.status,self.intake.contract,checks,result,
                    'Source proof currently verified; result retains current live source status.')
