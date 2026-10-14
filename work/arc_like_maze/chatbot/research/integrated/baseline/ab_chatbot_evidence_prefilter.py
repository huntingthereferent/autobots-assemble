"""Witness-based preflight for an explicitly required finite labeled edge.

Only contradictions already determined by *both* pinned edge observations and
fixed seed state assignments permit pruning. Missing evidence means UNDECIDED.
No failed edge under some OTHER pairing is treated as universally forbidden.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal

from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio
from ab_chatbot_rule_change import _owner_consistent, _version
from ab_chatbot_union_extension import _cached_step
from ab_chatbot_language_bridge import ObservationWall, PinnedEdges
from ab_chatbot_discovered_correspondence import DOMAIN_SET


@dataclass(frozen=True)
class ExclusionCertificate:
    words: tuple[str, ...]
    required_source: tuple[int, int, int]
    action: str
    observed_old_target: tuple[int, int, int]
    paired_new_source: tuple[int, int, int]
    observed_new_target: tuple[int, int, int]
    existing_old_target_image: tuple[int, int, int] | None
    existing_new_target_preimage: tuple[int, int, int] | None
    cause: Literal['SOURCE_COLLISION', 'TARGET_COLLISION']


@dataclass(frozen=True)
class Preflight:
    verdict: Literal['NOT_CONTRADICTED', 'UNDECIDED', 'CONTRADICTED']
    certificate: ExclusionCertificate | None


def inspect_required_edge(old, new, selected, required):
    """Zero new observations. An excluded candidate violates a stated task requirement.

    NOT_CONTRADICTED is NOT proof that the edge will ultimately be admitted.
    Both referenced pinned snapshots must already contain the relevant edges.
    """
    s, action = required
    mapping = dict(selected.state_pairs)
    inverse = {image: state for state, image in mapping.items()}
    if s not in mapping:
        return Preflight('UNDECIDED', None)
    new_s = mapping[s]
    old_snap, new_snap = old.snapshot, new.snapshot
    if (old.origin_scope != 'LOCAL_OWNER_VERIFIED' or
            new.origin_scope != 'LOCAL_OWNER_VERIFIED'):
        return Preflight('UNDECIDED', None)
    if not isinstance(old_snap, PinnedEdges) or not isinstance(new_snap, PinnedEdges):
        # Complete snapshots are already owner-checked at pinning in the bridge.
        # Replaying is still required below; unknown formats do not authorize pruning.
        return Preflight('UNDECIDED', None)
    if (s, action) not in old_snap.edges or (new_s, action) not in new_snap.edges:
        return Preflight('UNDECIDED', None)
    t, nt = _cached_step(old, s, action), _cached_step(new, new_s, action)
    if not (_owner_consistent(old, s, action, t) and
            _owner_consistent(new, new_s, action, nt)):
        raise ObservationWall('required-edge cache differs from pinned local owner')
    cause = ('SOURCE_COLLISION' if t in mapping and mapping[t] != nt else
             'TARGET_COLLISION' if nt in inverse and inverse[nt] != t else None)
    if cause is None:
        return Preflight('NOT_CONTRADICTED', None)
    return Preflight('CONTRADICTED', ExclusionCertificate(
        selected.words, s, action, t, new_s, nt,
        mapping.get(t), inverse.get(nt), cause))


class RequiredEdgePortfolio(PostExtensionPortfolio):
    """Optional pruning under a separately declared must-admit-edge contract.

    A pruned candidate is disqualified only for THIS goal contract, never as a
    mathematical partial correspondence in general. Survivors still undergo
    complete existing extension/replay; no sources or old algorithms modified.
    """
    def __init__(self, old, new, goals, *, required_edge, **kwargs):
        if (type(required_edge) is not tuple or len(required_edge) != 2 or
                required_edge[0] not in DOMAIN_SET or required_edge[1] not in ('A','B')):
            raise ValueError('required edge must be a finite state and A/B action')
        super().__init__(old, new, goals, **kwargs)
        self.required_edge = required_edge
        self.certificates: tuple[ExclusionCertificate, ...] = ()
        self.undecided: int = 0
        self.before_filter: int | None = None
        self._rejected_selections = ()
        self._pinned = (self.discovered.old.snapshot, self.discovered.new.snapshot,
                        _version(self.discovered.old), _version(self.discovered.new))

    def _preflight_current(self):
        return (self.discovered.old.snapshot is self._pinned[0] and
                self.discovered.new.snapshot is self._pinned[1] and
                _version(self.discovered.old) == self._pinned[2] and
                _version(self.discovered.new) == self._pinned[3])

    def _discover_selections(self):
        status = super()._discover_selections()
        if status is not None or not self.selections:
            return status
        self.before_filter = len(self.selections)
        kept, rejected, certificates, undecided = [], [], [], 0
        for selection in self.selections:
            result = inspect_required_edge(self.discovered.old, self.discovered.new,
                                           selection, self.required_edge)
            if result.verdict == 'CONTRADICTED':
                certificates.append(result.certificate)
                rejected.append(selection)
            else:
                kept.append(selection)
                undecided += result.verdict == 'UNDECIDED'
        self.certificates = tuple(certificates)
        self._rejected_selections = tuple(rejected)
        self.undecided = undecided
        self.selections = tuple(kept)
        return None

    def advance(self, *, max_new_edges=108):
        if not self._preflight_current():
            return self._report('UNKNOWN_VERSION', 'Pinned source changed; required-edge preflight invalid.')
        try:
            # Explicitly replay saved pruning witnesses on every read; no cache
            # change can silently retain an old exclusion proof.
            for cert in self.certificates:
                current = inspect_required_edge(
                    self.discovered.old, self.discovered.new,
                    next(sel for sel in self._rejected_selections if sel.words == cert.words),
                    self.required_edge)
                if current.verdict != 'CONTRADICTED' or current.certificate != cert:
                    raise ObservationWall('required-edge pruning certificate no longer replays')
        except (ObservationWall, KeyError, StopIteration, ValueError) as exc:
            return self._report('WALL_OBSERVATION', f'Pruning evidence failed: {exc}')
        # Capture candidates as distinct data for certificate replay.
        result = super().advance(max_new_edges=max_new_edges)
        if result.status in ('SEARCHING','EVALUATING','UNKNOWN_BUDGET','UNKNOWN_VERSION',
                             'WALL_OBSERVATION'):
            return result
        if not hasattr(self, '_extenders'):
            return replace(result, status='REQUIRED_EDGE_UNPROVED', selected=None,
                           possible_goal_images=(), detail='No witnessed candidate extension.')
        candidates = [(trial, ext) for trial, ext in zip(self.finished,self._extenders)
                      if self.required_edge in ext.edges]
        if not candidates:
            return replace(result, status='REQUIRED_EDGE_UNPROVED', selected=None,
                           possible_goal_images=(), detail='No completed candidate admitted the required edge.')
        best = max((trial for trial, _ in candidates),
                   key=lambda t:(len(t.carried),t.admitted_edges,t.paired_states,
                                 -t.excluded_edges,tuple((-len(w),w) for w in t.words)))
        original = result.status
        status = ('GOALS_CARRIED_' if len(best.carried)==len(self.goals) else 'PARTIAL_GOALS_') + (
            'WITNESSED' if original.endswith('_WITNESSED') else 'REMOTE_REPORTED')
        images=tuple((g,tuple(sorted({image for trial,_ in candidates
                    for goal,image,_ in trial.carried if goal==g}))) for g in self.goals)
        return replace(result, status=status, selected=best, possible_goal_images=images,
                       detail='Required edge independently admitted in chosen replayed extension; '
                              'pruned candidates are disqualified only under the stated requirement.')
