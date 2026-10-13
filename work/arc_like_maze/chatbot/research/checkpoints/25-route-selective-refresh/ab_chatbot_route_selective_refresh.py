"""Selective replay *within* an already witnessed two-route comparison.

A changed dependency triggers a fresh certificate audit of just the dependent
TwoHopTransport. A skipped route is CACHED_NOT_REPLAYED, never current proof.
The only proof-for-use method calls the existing full TwoRouteComparison.advance,
which audits both routes (including its own repeat audit). No autonomous polling.
"""
from __future__ import annotations
from dataclasses import dataclass
from ab_chatbot_source_change_propagation import (SourceChangePropagation,
    SourceChange, ScopeStamp)
from ab_chatbot_selective_propagation import _structure
from ab_chatbot_two_route_comparison import RouteComparison

_VALID = {'ROUTES_AGREE_ON_SELECTED_EDGE', 'ROUTE_COMPOSED_MAP_CONFLICT'}
_PROVED = 'TWO_HOP_CHAIN_WITNESSED'


@dataclass(frozen=True)
class RouteAuditRecord:
    name: str
    mode: str
    outcome: str
    proof_fresh: bool
    certificate: object  # historical on skip, independently audited when replayed


@dataclass(frozen=True)
class RouteSelectiveReport:
    status: str
    changed: tuple[SourceChange, ...]
    audited: tuple[str, ...]
    skipped: tuple[str, ...]
    routes: tuple[RouteAuditRecord, ...]
    historical_comparison: RouteComparison
    current_comparison: RouteComparison | None
    proof_for_use: bool
    observations_before: tuple
    observations_after: tuple


class RouteSelectiveRefresh:
    """Live pin/version detection plus minimal route replay; no proof laundering."""
    def __init__(self, ledger: SourceChangePropagation):
        if (type(ledger) is not SourceChangePropagation or not ledger.history or
            ledger.history[-1].current.status not in _VALID or
            ledger.history[-1].left_route != 'PRESERVED' or
            ledger.history[-1].right_route != 'PRESERVED'):
            raise ValueError('requires an already witnessed comparison ledger')
        self.ledger=ledger
        self.comparison=ledger.comparison
        self.historical=ledger.history[-1].current
        self._last={'left':self.historical.left, 'right':self.historical.right}
        self._stamps=ledger._stamps()
        self._signature=_structure(ledger)
        self.history: list[RouteSelectiveReport]=[]

    def _read_stamps(self):
        return self.ledger._stamps()

    def _changed(self, previous, current):
        return self.ledger._changed(previous,current)

    def _counts(self):
        return tuple(s.observed_edges for s in self._read_stamps())

    @staticmethod
    def _causes(changes):
        affected=set()
        for item in changes:
            affected.update(('left','right') if item.scope in ('donor','final')
                            else ('left',) if item.scope=='left_middle' else ('right',))
        return affected

    def advance(self, *, force_routes=()):
        """Replay affected routes, **not** a route-independent comparison proof."""
        if (type(force_routes) is not tuple or len(set(force_routes))!=len(force_routes)
            or any(type(x) is not str or x not in ('left','right') for x in force_routes)):
            raise ValueError('force_routes must be a subset of left/right')
        before_stamps=self._read_stamps()
        before=tuple(s.observed_edges for s in before_stamps)
        changes=self._changed(self._stamps,before_stamps)
        beginning_structure=_structure(self.ledger)
        structure_changed=(beginning_structure!=self._signature or
                           not self.ledger._scope_unchanged())
        affected=self._causes(changes)|set(force_routes)
        if structure_changed:affected={'left','right'}
        audited=[];skipped=[];records=[]
        for name in ('left','right'):
            if name in affected:
                # A scope-object/declaration substitution cannot generate
                # a success certificate even if the replacement can run.
                if structure_changed:
                    state='ROUTE_DECLARATION_CHANGED'
                    cert=None
                else:
                    route=getattr(self.comparison,name)
                    cert=route.advance()
                    # Revisit: a transient success must remain valid before
                    # this audit is recorded as fresh evidence.
                    second=route.advance()
                    if (cert.status!=_PROVED or second.status!=_PROVED or
                        cert.fingerprint!=second.fingerprint or
                        cert.fingerprint!=self.comparison.expected[0 if name=='left' else 1]):
                        cert=second
                    if (cert.status==_PROVED and
                        cert.fingerprint==self.comparison.expected[0 if name=='left' else 1] and
                        second.status==_PROVED):
                        state=_PROVED
                    else:state=cert.status if cert.status!=_PROVED else 'ROUTE_EVIDENCE_WITHDRAWN'
                self._last[name]=cert
                audited.append(name)
                records.append(RouteAuditRecord(name,'REPLAYED',state,True,cert))
            else:
                skipped.append(name)
                previous=self._last[name]
                records.append(RouteAuditRecord(name,'CACHED_NOT_REPLAYED',
                    previous.status if previous is not None else 'UNKNOWN',False,previous))
        after_stamps=self._read_stamps()
        post_changes=self._changed(before_stamps,after_stamps)
        if post_changes or _structure(self.ledger)!=beginning_structure:
            # A dependency moved DURING the audit: no purported fresh proof.
            records=[RouteAuditRecord(r.name,r.mode,'SOURCE_MOVED_DURING_AUDIT'
                if r.proof_fresh else r.outcome,False,r.certificate) for r in records]
            status='SOURCE_MOVED_DURING_AUDIT'
        elif any(r.proof_fresh and r.outcome!=_PROVED for r in records):
            status='COMPARISON_WITHDRAWN'
        elif audited:
            status='COMPARISON_REQUIRES_FULL_AUDIT'
        else:status='COMPARISON_CACHED_NOT_REPLAYED'
        report=RouteSelectiveReport(status,changes,tuple(audited),tuple(skipped),
                tuple(records),self.historical,None,False,before,
                tuple(s.observed_edges for s in after_stamps))
        self._stamps=after_stamps
        # Preserve identity/reference metadata from which the next delta is
        # measured. A structural substitution remains detectable forever.
        self.history.append(report)
        return report

    def verify_for_use(self):
        """Full existing owner-backed comparison replay, never promote cache."""
        before_stamps=self._read_stamps()
        before=tuple(s.observed_edges for s in before_stamps)
        delta=self._changed(self._stamps,before_stamps)
        safe=_structure(self.ledger)==self._signature and self.ledger._scope_unchanged()
        current=self.comparison.advance() if safe else None
        after_stamps=self._read_stamps()
        safe=(safe and _structure(self.ledger)==self._signature and
              not self._changed(before_stamps,after_stamps) and
              current is not None and current.status in _VALID and
              current.left is not None and current.right is not None and
              (current.left.fingerprint,current.right.fingerprint)==self.comparison.expected)
        self._stamps=after_stamps
        records=[]
        for name in ('left','right'):
            cert=getattr(current,name) if current is not None else None
            self._last[name]=cert
            good=bool(safe and cert is not None and cert.status==_PROVED)
            records.append(RouteAuditRecord(name,'REPLAYED',
                    cert.status if cert is not None else 'ROUTE_SCOPE_CHANGED',good,cert))
        status='COMPARISON_FULLY_WITNESSED' if safe else 'COMPARISON_WITHDRAWN'
        report=RouteSelectiveReport(status,delta,('left','right'),(),tuple(records),
            self.historical,current,safe,before,tuple(s.observed_edges for s in after_stamps))
        self.history.append(report)
        return report
