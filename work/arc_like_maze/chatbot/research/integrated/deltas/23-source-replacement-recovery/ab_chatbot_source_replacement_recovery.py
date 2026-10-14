"""On-demand recovery with a NEW independently owner-pinned replacement middle scope.

This is an adapter around the unchanged SourceChangePropagation, TwoHopTransport
and TwoRouteComparison. It does not poll sources, infer maps, or move evidence
between pins. The old comparison remains a historical record, including its
route conflict. A new route must acquire and replay its own observations.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ab_chatbot_source_change_propagation import SourceChangePropagation, PropagationReport
from ab_chatbot_two_route_comparison import TwoRouteComparison, RouteComparison
from ab_chatbot_two_hop_transport import TwoHopTransport, TwoHopReport

PROVED = 'TWO_HOP_CHAIN_WITNESSED'
ROUTE_RESULTS = {'ROUTES_AGREE_ON_SELECTED_EDGE','ROUTE_COMPOSED_MAP_CONFLICT'}


def _digest(v):
    return type(v) is str and len(v) == 64 and all(c in '0123456789abcdef' for c in v)


@dataclass(frozen=True)
class RecoveryReport:
    status: str
    historical: RouteComparison | None
    historical_refresh: PropagationReport | None
    replacement: TwoHopReport | None
    recovered_comparison: RouteComparison | None
    earlier_right_scope: object
    replacement_scope: object
    observations_before: tuple
    observations_after: tuple
    detail: str


class SourceReplacementRecovery:
    """Compare with fresh middle-source evidence while preserving old provenance.

    Existing comparison must have a completed baseline. The historical right
    chain must be withdrawn before this replacement is *promoted as recovery*.
    A live old chain is not silently superseded by a newly convenient answer.
    """
    def __init__(self, history: SourceChangePropagation, replacement: TwoHopTransport,
                 declaration: Any):
        self.history, self.replacement = history, replacement
        self.status = 'INVALID_RECOVERY'
        self.expected = ()
        self.old_middle = None
        self.new_middle = None
        self.baseline = None
        self.new_comparison = None
        self.records: list[RecoveryReport] = []
        if not (type(history) is SourceChangePropagation and
                isinstance(replacement, TwoHopTransport) and
                type(declaration) is dict and
                set(declaration) == {'historical_left_fingerprint',
                                    'historical_right_fingerprint',
                                    'replacement_right_fingerprint'}):
            return
        values = tuple(declaration[k] for k in ('historical_left_fingerprint',
                                               'historical_right_fingerprint',
                                               'replacement_right_fingerprint'))
        if not all(_digest(v) for v in values) or not history.history:
            return
        baseline = history.history[0]
        if baseline.status != 'BASELINE_WITNESSED' or baseline.current.status not in ROUTE_RESULTS:
            return
        previous=history.comparison
        if previous.expected != values[:2] or replacement.status != 'CHAIN_DECLARED':
            return
        l,r = previous.left, previous.right
        donor,final=l.first.donor,l.final
        middle=replacement.first.recipient
        prior_middle=r.first.recipient
        # A genuinely new source scope (or new snapshot pair) cannot reuse the
        # original middle join, its registry or either pinned observer.
        if (replacement is l or replacement is r or
            replacement.first.donor is not donor or replacement.final is not final or
            replacement.first.edge != l.first.edge or
            middle is prior_middle or middle is l.first.recipient or
            middle.registry is prior_middle.registry or
            middle.registry is l.first.recipient.registry or
            middle.registry is donor.registry or middle.registry is final.registry or
            any(x is y for x in (middle.old,middle.new)
                for y in (prior_middle.old,prior_middle.new,l.first.recipient.old,
                          l.first.recipient.new,donor.old,donor.new,final.old,final.new))):
            return
        # Construct only; never invoke an observing operation in __init__.
        fresh=TwoRouteComparison(l,replacement,{
            'left_chain_fingerprint':values[0],
            'right_chain_fingerprint':values[2]})
        if fresh.status != 'ROUTES_DECLARED':
            return
        self.new_comparison = fresh
        self.expected = values
        self.old_middle = prior_middle
        self.new_middle = middle
        self._identity=(replacement.first, middle, middle.old, middle.new,
                        middle.registry, l, donor, final, prior_middle)
        self.baseline = baseline.current
        self.status = 'RECOVERY_DECLARED'

    def _counts(self):
        if self.new_comparison is None:return ()
        l=self.history.comparison.left
        return tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in (
            l.first.donor,l.first.recipient,self.old_middle,self.new_middle,l.final))

    def advance(self):
        before=self._counts()
        def emit(status,refresh=None,new_route=None,comparison=None,detail=''):
            report=RecoveryReport(status,self.baseline,refresh,new_route,comparison,
                self.old_middle,self.new_middle,before,self._counts(),detail)
            self.records.append(report)
            return report
        if self.status!='RECOVERY_DECLARED':return emit(self.status)
        first,m,old,new,registry,l,donor,final,prior=self._identity
        if (self.replacement.first is not first or first.recipient is not m or
            m.old is not old or m.new is not new or m.registry is not registry or
            self.history.comparison.left is not l or l.first.donor is not donor or
            l.final is not final or self.history.comparison.right.first.recipient is not prior or
            self.new_comparison.right is not self.replacement or
            self.new_comparison.left is not l):
            return emit('RECOVERY_SCOPE_CHANGED',detail='Exact source/route object identity changed.')
        # Refreshes the HISTORICAL comparator before considering the new route.
        refresh=self.history.advance()
        if refresh.left_route!='PRESERVED':
            return emit('RECOVERY_LEFT_EVIDENCE_UNPROVED',refresh,detail='Unchanged side must replay.')
        if refresh.right_route=='PRESERVED':
            return emit('RECOVERY_NOT_NEEDED',refresh,detail='Historical right route still verifies.')
        # Both routes and all their selected squares are independently replayed.
        compared=self.new_comparison.advance()
        new_route=compared.right
        if compared.status not in ROUTE_RESULTS:
            return emit('REPLACEMENT_EVIDENCE_UNPROVED',refresh,new_route,compared,
                        'New route has no current independently verified certificate.')
        # Repeat both audits; historical revocation cannot be silently undone.
        again=self.history.advance()
        checked=self.new_comparison.advance()
        if (again.left_route!='PRESERVED' or again.right_route=='PRESERVED' or
            checked.status!=compared.status or checked.status not in ROUTE_RESULTS or
            checked.left_composed!=compared.left_composed or
            checked.right_composed!=compared.right_composed or
            checked.left is None or checked.right is None or
            checked.left.fingerprint!=self.expected[0] or
            checked.right.fingerprint!=self.expected[2]):
            return emit('RECOVERY_EVIDENCE_WITHDRAWN',again,checked.right,checked,
                        'Repeat audit did not preserve required current evidence.')
        kind='RECOVERY_AGREEMENT_WITNESSED' if checked.status=='ROUTES_AGREE_ON_SELECTED_EDGE' else 'RECOVERY_CONFLICT_WITNESSED'
        return emit(kind,again,checked.right,checked,
                    'New route independently verified; old route and comparison remain historical.')
