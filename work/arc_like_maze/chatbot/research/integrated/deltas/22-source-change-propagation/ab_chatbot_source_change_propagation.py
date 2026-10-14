"""On-demand source-change propagation for the EXISTING two-route A/B chatbot.

This is NOT an autonomous process or a new solver. An external caller invokes
``advance()`` after the surrounding source moves. Only owner-pinned live replay
can preserve a certificate; hints and matching source labels cannot do so.

One middle scope affects one chain; shared donor/final scopes affect both.
Earlier audited certificates are archived as historical observations, not as
active mathematical conclusions after their supporting source changes.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any
from ab_chatbot_two_route_comparison import TwoRouteComparison, RouteComparison
from ab_chatbot_rule_change import _version

VALID = {'ROUTES_AGREE_ON_SELECTED_EDGE', 'ROUTE_COMPOSED_MAP_CONFLICT'}

@dataclass(frozen=True)
class ScopeStamp:
    name: str
    source_versions: tuple
    owner_heads: tuple
    snapshot_identifiers: tuple
    pin_validity: tuple
    evidence_hashes: tuple
    observed_edges: tuple

@dataclass(frozen=True)
class SourceChange:
    scope: str
    causes: tuple[str, ...]
    old_observations: tuple
    current_observations: tuple

@dataclass(frozen=True)
class PropagationReport:
    status: str
    left_route: str
    right_route: str
    comparison: str
    changed_scopes: tuple[SourceChange, ...]
    affected_routes: tuple[str, ...]
    observations_before: tuple
    observations_after: tuple
    historical: RouteComparison | None
    current: RouteComparison
    detail: str


def _evidence_digest(snap):
    # Only the current recorded evidence is represented; this hash is NOT
    # source authentication. Excluding counters from certificate validity
    # allows unrelated *honestly obtained* observations to accumulate.
    edges = getattr(snap, 'edges', None)
    if edges is None:
        return sha256(repr(getattr(snap, 'values', None)).encode()).hexdigest()
    records = sorted((s, a, target) for (s,a),target in edges.items())
    return sha256(json.dumps(records, separators=(',',':')).encode()).hexdigest()


class SourceChangePropagation:
    """Evidence-led dependency refresh, not source monitoring or autonomy.

    The four nodes are donor, left middle, right middle, and final. They are
    the same exact object references already admitted by TwoRouteComparison.
    ``advance`` makes zero *new* owner edge requests on completed routes.
    """
    def __init__(self, comparison: TwoRouteComparison):
        if not isinstance(comparison, TwoRouteComparison) or comparison.status != 'ROUTES_DECLARED':
            raise ValueError('an already declared pair of independent routes is required')
        self.comparison = comparison
        self._scopes = (
            ('donor', comparison.left.first.donor),
            ('left_middle', comparison.left.first.recipient),
            ('right_middle', comparison.right.first.recipient),
            ('final', comparison.left.final),
        )
        self._identities = tuple((name, joint, joint.old, joint.new, joint.registry)
                                 for name,joint in self._scopes)
        self._baseline = None
        self._last_stamps = None
        self._last_report = None
        self.history: list[PropagationReport] = []

    def _stamps(self):
        results=[]
        for name, join in self._scopes:
            old,new=join.old,join.new
            # Calling registry.verify checks exactly the recorded in-process
            # owner binding and latches invalid pins; a claimed label is never
            # sufficient to restore proof.
            tokens=join._base._tokens if join._base is not None else ()
            pins=tuple(join.registry.verify(t, bridge)
                       for t,bridge in zip(tokens,(old,new)))
            results.append(ScopeStamp(name,(_version(old),_version(new)),
                tuple((view.version, view.digest) if (view:=bridge.owner.select()) is not None else None
                      for bridge in (old,new)),
                (id(old.snapshot),id(new.snapshot)),pins,
                (_evidence_digest(old.snapshot),_evidence_digest(new.snapshot)),
                (len(old.snapshot.edges),len(new.snapshot.edges))))
        return tuple(results)

    def _scope_unchanged(self):
        return all(
            j is original_j and j.old is old and j.new is new and j.registry is registry
            for (_,j,old,new,registry),(_,original_j) in zip(self._identities,self._scopes)
        ) and tuple(self.comparison._scope_objects)==tuple(j for _,j in self._scopes)

    @staticmethod
    def _changed(previous,current):
        changes=[]
        for before,after in zip(previous,current):
            causes=[]
            if before.snapshot_identifiers!=after.snapshot_identifiers:causes.append('SNAPSHOT_REPLACED')
            if before.source_versions!=after.source_versions:causes.append('SOURCE_VERSION_CHANGED')
            if before.owner_heads!=after.owner_heads:causes.append('SOURCE_HEAD_ADVANCED')
            if before.pin_validity!=after.pin_validity:causes.append('OWNER_BINDING_CHANGED')
            if before.evidence_hashes!=after.evidence_hashes:causes.append('CACHED_EVIDENCE_CHANGED')
            if before.observed_edges!=after.observed_edges:causes.append('OBSERVATION_COUNT_CHANGED')
            if causes:changes.append(SourceChange(before.name,tuple(causes),before.observed_edges,after.observed_edges))
        return tuple(changes)

    def advance(self) -> PropagationReport:
        # No new chain or mapping is discovered. Both chains are independently
        # replayed (also on failure) by the original comparator.
        before=self._stamps()
        unchanged=self._scope_unchanged()
        result=self.comparison.advance() if unchanged else None
        after=self._stamps()
        if result is None:
            # A scope-object substitution cannot be masked by a label match.
            result=RouteComparison('ROUTE_SCOPE_CHANGED',None,None,(),(),(),(),
                                   tuple(s.observed_edges for s in before),
                                   tuple(s.observed_edges for s in after),
                                   'A registered source object or registry was replaced.')
        reference=self._last_stamps if self._last_stamps is not None else before
        changed=self._changed(reference,after)
        affected=set()
        for change in changed:
            affected.update(('left','right') if change.scope in ('donor','final')
                            else ('left',) if change.scope=='left_middle' else ('right',))
        if not unchanged:affected.update(('left','right'))
        lstatus=result.left.status if result.left is not None else 'SCOPE_UNVERIFIED'
        rstatus=result.right.status if result.right is not None else 'SCOPE_UNVERIFIED'
        lvalid=lstatus=='TWO_HOP_CHAIN_WITNESSED'
        rvalid=rstatus=='TWO_HOP_CHAIN_WITNESSED'
        active=result.status in VALID and lvalid and rvalid
        if self._baseline is None:
            status='BASELINE_WITNESSED' if active else 'BASELINE_UNPROVED'
            detail='First audited result retained as historical evidence, never promoted without a fresh replay.'
        elif not active:
            status='COMPARISON_WITHDRAWN'
            detail='Previously recorded route comparison is historical; at least one required live chain is unproved.'
        elif self._last_report and self._last_report.status=='COMPARISON_WITHDRAWN':
            status='COMPARISON_REESTABLISHED'
            detail='Both independently replayed chains now support a comparison; no historical certificate was imported.'
        elif result.status==self._baseline.status:
            status='COMPARISON_PRESERVED'
            detail='Current owner-pinned replay supports the same selected-edge comparison result.'
        else:
            status='COMPARISON_RESULT_CHANGED'
            detail='Current live evidence supports a different comparison; do not reuse the historical result.'
        report=PropagationReport(status,
            'PRESERVED' if lvalid else 'WITHDRAWN',
            'PRESERVED' if rvalid else 'WITHDRAWN',
            result.status,changed,tuple(x for x in ('left','right') if x in affected),
            tuple(s.observed_edges for s in before),tuple(s.observed_edges for s in after),
            self._baseline,result,detail)
        if self._baseline is None:self._baseline=result
        self._last_stamps=after
        self._last_report=report
        self.history.append(report)
        return report
