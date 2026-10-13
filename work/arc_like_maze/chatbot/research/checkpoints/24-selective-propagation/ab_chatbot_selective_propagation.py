"""Selective, on-demand refresh of multiple existing owner-pinned comparisons.

Nothing runs autonomously or polls. The caller invokes advance() on an
external change. Cheap local pin/version/snapshot/evidence fingerprints detect
which comparison certificates may be affected. An affected comparison is
fully replayed by its EXISTING SourceChangePropagation. Unchanged records are
explicitly CACHED_NOT_REPLAYED and cannot be used as fresh proof until
verify_for_use() replays the exact existing comparison.

Fingerprint checks provide change detection, NOT source authentication.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ab_chatbot_source_change_propagation import (SourceChangePropagation,
    PropagationReport, SourceChange)


def _freeze(x: Any):
    if isinstance(x, dict):
        return tuple(sorted((_freeze(k),_freeze(v)) for k,v in x.items()))
    if isinstance(x, (list, tuple)):
        return tuple(_freeze(v) for v in x)
    if isinstance(x, (str, int, float, bool, type(None))):
        return x
    return (type(x).__name__, id(x))


def _structure(history: SourceChangePropagation):
    """Catch mutable route/mapping/fingerprint substitutions between checks."""
    c=history.comparison
    def route_signature(r):
        a=r.first
        return (id(r), r.status, _freeze(r.expected), id(a), a.status,
                id(a.donor),id(a.recipient),id(r.final),
                _freeze(a.expected),_freeze(a.edge),
                _freeze(a.old_map),_freeze(a.new_map),
                _freeze(r.old_map),_freeze(r.new_map))
    return (id(c),c.status,_freeze(c.expected),
            tuple(id(s) for s in c._scope_objects),
            route_signature(c.left),route_signature(c.right),
            history._scope_unchanged())


@dataclass(frozen=True)
class SelectiveRecord:
    name: str
    mode: str  # REPLAYED or CACHED_NOT_REPLAYED; only REPLAYED is proof-for-use
    outcome: str
    dependency_changes: tuple[SourceChange, ...]
    last_audited: PropagationReport
    proof_fresh: bool


@dataclass(frozen=True)
class SelectiveReport:
    status: str
    changed_dependencies: tuple
    audited: tuple[str, ...]
    skipped: tuple[str, ...]
    records: tuple[SelectiveRecord, ...]
    owner_observations_before: tuple
    owner_observations_after: tuple


class SelectivePropagationPortfolio:
    """Skip entire unaffected comparison *audits*, never export cached proof.

    The underlying certificate graph remains immutable. Multiple comparison
    records can share exact scopes: any changed scope affects every dependent
    record; independent records need no transition replay.
    """
    def __init__(self, named: dict[str, SourceChangePropagation]):
        if (type(named) is not dict or not 2<=len(named)<=16 or
            any(type(k) is not str or not k or type(v) is not SourceChangePropagation
                or not v.history for k,v in named.items()) or
            len({id(v) for v in named.values()})!=len(named)):
            raise ValueError('2..16 distinct already-audited named comparison ledgers required')
        self.named=dict(named)
        self._basis={name:(h._stamps(),_structure(h)) for name,h in self.named.items()}
        self._last={name:h.history[-1] for name,h in self.named.items()}
        self.history: list[SelectiveReport] = []

    def _counts(self):
        return tuple((name,tuple(s.observed_edges for s in h._stamps()))
                     for name,h in self.named.items())

    def advance(self, *, force: tuple[str, ...]=()) -> SelectiveReport:
        if (type(force) is not tuple or len(set(force))!=len(force) or
            any(type(name) is not str or name not in self.named for name in force)):
            raise ValueError('force must name existing unique comparison records')
        before=self._counts()
        audited=[];skipped=[];records=[];changes=[]
        for name,h in self.named.items():
            previous,signature=self._basis[name]
            stamps=h._stamps()
            delta=h._changed(previous,stamps)
            structure_drift=_structure(h)!=signature
            if delta:
                changes.extend((name,change.scope,change.causes) for change in delta)
            if structure_drift:
                changes.append((name,'DECLARATION',('ROUTE_STRUCTURE_CHANGED',)))
            if delta or structure_drift or name in force:
                result=h.advance()  # full owner-backed replay, retains failures
                self._last[name]=result
                self._basis[name]=(h._stamps(),_structure(h))
                audited.append(name)
                records.append(SelectiveRecord(name,'REPLAYED',result.status,delta,result,True))
            else:
                # Metadata/pin checks alone do NOT revalidate owner transitions.
                # The stored result is historical, not a newly witnessed proof.
                skipped.append(name)
                previous_report=self._last[name]
                records.append(SelectiveRecord(name,'CACHED_NOT_REPLAYED',
                            previous_report.status,(),previous_report,False))
        after=self._counts()
        report=SelectiveReport('SELECTIVE_REFRESH',tuple(changes),tuple(audited),
                               tuple(skipped),tuple(records),before,after)
        self.history.append(report)
        return report

    def verify_for_use(self, name: str) -> SelectiveRecord:
        """Force full owner-backed replay before treating a cached result as proof."""
        if type(name) is not str or name not in self.named:
            raise ValueError('unknown comparison')
        r=self.advance(force=(name,))
        return next(item for item in r.records if item.name==name)
