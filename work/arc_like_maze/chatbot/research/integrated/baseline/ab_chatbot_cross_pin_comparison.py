"""Explicit cross-pin word-relation replay on the SAME existing finite chatbot.

A predecessor token is historical attribution only, never mathematical transport.
Comparison is scoped to the caller's exact two rooted word histories.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from ab_chatbot_owner_pin_contract import OwnerPinRegistry, PinDescription
from ab_chatbot_language_bridge import LanguageBridge, PinnedEdges, EdgeBudgetReached, ObservationWall
from ab_chatbot_rule_change import _version, _cached_path, _owner_consistent

ROOT=(0,0,0)

@dataclass(frozen=True)
class ComparedRelation:
    words: tuple[str,str]
    old_paths: tuple[object,object]
    new_paths: tuple[object,object]
    old_equal: bool
    new_equal: bool

@dataclass(frozen=True)
class CrossPinReport:
    status: str
    fingerprint: str | None
    pins: tuple[PinDescription,...]
    old_version: tuple | None
    new_version: tuple | None
    comparisons: tuple[ComparedRelation,...]
    old_observed: int
    new_observed: int
    detail: str

class CrossPinComparison:
    """Pin-gated per-word observation and independent replay; no inherited edges."""
    def __init__(self, old: LanguageBridge, new: LanguageBridge, task_input: Any,
                 *, registry: OwnerPinRegistry):
        self.old,self.new,self.registry=old,new,registry
        self.status='INVALID_TASK';self.fingerprint=None
        self.description='Explicit tokens and rooted A/B-word pairs required.'
        self.requests=();self._tokens=();self._records=[]
        self._jobs=[];self._cursor=0;self._retained={}
        self._versions=None;self._snapshots=None
        if type(task_input) is not dict or set(task_input)!={'required_owner_pins','compare_words'}:
            return
        pin=task_input['required_owner_pins'];words=task_input['compare_words']
        if (type(pin) is not dict or set(pin)!={'old','new'} or
                any(type(v) is not str or len(v)!=48 for v in pin.values()) or
                pin['old']==pin['new'] or
                type(words) is not list or not 1<=len(words)<=8):
            return
        normalized=[]
        for pair in words:
            if (type(pair) is not list or len(pair)!=2 or
                    any(type(w) is not str or len(w)>12 or any(a not in 'AB' for a in w)
                        for w in pair) or pair[0]==pair[1]):
                return
            normalized.append(tuple(pair))
        if len(set(normalized))!=len(normalized):return
        self._tokens=(pin['old'],pin['new'])
        descriptors=tuple(registry.description(t) for t in self._tokens)
        if any(d is None for d in descriptors):
            self.status='UNKNOWN_OWNER_PIN';return
        if old.snapshot is new.snapshot:
            self.status='INVALID_TASK';self.description='Comparisons require separate pinned snapshots.'
            return
        self.requests=tuple(normalized)
        self._records=descriptors
        self._versions=(_version(old),_version(new))
        self._snapshots=(old.snapshot,new.snapshot)
        for i,pair in enumerate(self.requests):
            for side,bridge in (('old',old),('new',new)):
                for index,word in enumerate(pair):
                    self._jobs.append((side,i,index,word))
        self.fingerprint=sha256(json.dumps({'pins':self._tokens,'words':self.requests},
                          sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.status='TASK_ACCEPTED'
        self.description='Two explicitly pinned snapshots; independent word evidence required.'

    def _pin_status(self):
        for token,bridge in zip(self._tokens,(self.old,self.new)):
            if not self.registry.verify(token,bridge):
                return False
        return True

    def _report(self,status,detail,comparisons=()):
        def count(bridge):
            return len(bridge.snapshot.edges) if isinstance(bridge.snapshot,PinnedEdges) else len(bridge.snapshot.values)
        return CrossPinReport(status,self.fingerprint,tuple(self._records),
                  self._versions[0] if self._versions else None,
                  self._versions[1] if self._versions else None,
                  tuple(comparisons),count(self.old),count(self.new),detail)

    def _audit(self):
        for (side,state,action),expected in self._retained.items():
            bridge=self.old if side=='old' else self.new
            snap=bridge.snapshot
            if isinstance(snap,PinnedEdges) and (state,action) not in snap.edges:
                raise ObservationWall('previously retained edge was removed')
            actual=snap.step(state,action)
            if actual!=expected or not _owner_consistent(bridge,state,action,actual):
                raise ObservationWall('retained edge differs from independently pinned owner')

    def advance(self,*,max_new_edges:int=108):
        if type(max_new_edges) is not int or not 0<=max_new_edges<=108:
            raise ValueError('max_new_edges must be integer 0..108')
        if self.status!='TASK_ACCEPTED':return self._report(self.status,self.description)
        if self._snapshots!=(self.old.snapshot,self.new.snapshot) or self._versions!=(_version(self.old),_version(self.new)):
            return self._report('UNKNOWN_VERSION','Pinned snapshot object or revision changed; no comparison admitted.')
        if not self._pin_status():
            return self._report('OWNER_PIN_UNPROVED','One explicit owner pin is no longer locally verified.')
        try:
            self._audit()
            used=0
            while self._cursor<len(self._jobs):
                side,_,_,word=self._jobs[self._cursor]
                bridge=self.old if side=='old' else self.new
                # Follow from root every time, independently. Previously used
                # edges are retained and rechecked; no old->new edge copying.
                s=ROOT
                for action in word:
                    key=(s,action)
                    missing=isinstance(bridge.snapshot,PinnedEdges) and key not in bridge.snapshot.edges
                    if missing and used>=max_new_edges:
                        return self._report('SEARCHING','Per-call observation cap reached; task resumable.')
                    out=bridge.snapshot.step(s,action)
                    if not _owner_consistent(bridge,s,action,out):
                        raise ObservationWall('new observed transition does not match bound owner')
                    used+=int(missing)
                    self._retained[(side,s,action)]=out
                    s=out
                self._cursor+=1
            self._audit()
            compared=[]
            for pair in self.requests:
                old_paths=tuple(_cached_path(self.old,ROOT,word) for word in pair)
                new_paths=tuple(_cached_path(self.new,ROOT,word) for word in pair)
                old_equal=old_paths[0].states[-1]==old_paths[1].states[-1]
                new_equal=new_paths[0].states[-1]==new_paths[1].states[-1]
                compared.append(ComparedRelation(pair,old_paths,new_paths,old_equal,new_equal))
            if not self._pin_status():
                return self._report('OWNER_PIN_UNPROVED','Owner binding changed during independent replay.')
            if any(r.old_equal!=r.new_equal for r in compared):
                status='RELATION_CHANGED_WITNESSED'
            elif any(r.old_equal for r in compared):
                status='DECLARED_EQUALITY_PRESERVED_WITNESSED'
            else:
                status='DECLARED_NONIDENTITY_PRESERVED_WITNESSED'
            return self._report(status,'All declared rooted word pairs replayed independently; no whole-system equivalence claimed.',compared)
        except EdgeBudgetReached:
            return self._report('UNKNOWN_BUDGET','Per-source unique edge budget exhausted; incomplete comparison.')
        except (ObservationWall,ValueError,KeyError,AttributeError) as exc:
            return self._report('WALL_OBSERVATION',f'Evidence audit failed: {exc}')
