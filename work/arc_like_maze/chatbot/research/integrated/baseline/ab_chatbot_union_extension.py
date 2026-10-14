"""Budgeted, witnessed *edge extension* of a previously joined path restriction.

Starts from PathUnionAgent's selected (rooted) witnessed partial pairing and
attempts uncovered A/B edges. An edge is admitted only when it preserves a
partial injection and its paired labeled step is observed on both pinned laws.
No change to old chatbot modules, no global maximality, no physical claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_path_union import PathUnionAgent, JoinedRestriction
from ab_chatbot_discovered_correspondence import State
from ab_chatbot_language_bridge import PinnedEdges, EdgeBudgetReached, ObservationWall
from ab_chatbot_rule_change import WordRelation, _cached_path, _count, _owner_consistent, _version

Edge = tuple[State, str, State, State, State]
Status = Literal[
    'CONTINUING', 'ROOTED_CLOSED_WITNESSED', 'ROOTED_CLOSED_REMOTE_REPORTED',
    'PARTIAL_EXTENSION_WITNESSED', 'PARTIAL_EXTENSION_REMOTE_REPORTED',
    'UNKNOWN_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]

@dataclass(frozen=True)
class ExcludedEdge:
    source: State
    action: str
    old_target: State
    new_target: State
    cause: str
    witness: WordRelation

@dataclass(frozen=True)
class ExtensionReport:
    status: Status
    initial_states: int
    initial_edges: int
    state_pairs: tuple[tuple[State, State], ...]
    admitted_edges: tuple[Edge, ...]
    new_edges: tuple[Edge, ...]
    rejected: tuple[ExcludedEdge, ...]
    considered: int
    pending: int
    old_observed_edges: int
    new_observed_edges: int
    detail: str

class UnionEdgeExtender:
    """Single chosen union; tries A then B per mapped old state in BFS-like order.

    Admission depends on discovery order and the chosen starting union. A
    rejected extension does not prove all other path pairings impossible.
    Calling advance resumes without abandoning previously checked evidence.
    """
    def __init__(self, source: PathUnionAgent, *, action_order: str = "AB"):
        if action_order not in ("AB", "BA"):
            raise ValueError("action_order must be AB or BA")
        self.action_order = action_order
        union = source.run()  # zero new reads, audits base evidence
        if union.status not in ('UNION_WITNESSED', 'UNION_REMOTE_REPORTED',
                                'PARTIAL_UNION_WITNESSED', 'PARTIAL_UNION_REMOTE_REPORTED'):
            raise ValueError(f'no verified initial union: {union.status}')
        assert union.selected is not None
        self.discovered = source.discovered
        self.base: JoinedRestriction = union.selected
        d = self.discovered
        self.old, self.new = d.old, d.new
        self.old_snapshot, self.new_snapshot = d.old_snap, d.new_snap
        self.old_version, self.new_version = d.old_version, d.new_version
        self.forward = dict(self.base.state_pairs)
        self.reverse = {v: k for k, v in self.forward.items()}
        self.edges: dict[tuple[State, str], Edge] = {(s,a): (s,a,t,ns,nt)
            for s,a,t,ns,nt in self.base.admitted_edges}
        self.new_edges: list[Edge] = []
        self.rejected: list[ExcludedEdge] = []
        # Reachable root words witnessing the map, shortest then alphabetically.
        self.words: dict[State, str] = {d.old_root: ''}
        for word in sorted(self.base.words, key=lambda w:(len(w),w)):
            old = d.old_root
            path = _cached_path(self.old, old, word)
            for idx, state in enumerate(path.states):
                candidate = word[:idx]
                if state not in self.words or (len(candidate),candidate) < (len(self.words[state]), self.words[state]):
                    self.words[state] = candidate
        if set(self.forward) != set(self.words):
            raise ValueError('initial union has no rooted witness for every paired state')
        self.queue = [(state, action) for state in sorted(self.forward) for action in self.action_order
                      if (state, action) not in self.edges]
        self.cursor = 0
        self.terminal = False

    def _current(self) -> bool:
        d = self.discovered
        return (d.old.snapshot is self.old_snapshot and d.new.snapshot is self.new_snapshot
                and _version(d.old) == self.old_version and _version(d.new) == self.new_version)

    def _audit(self) -> None:
        d = self.discovered
        checked = d.advance(max_new_edges=0)
        if checked.status in ('UNKNOWN_VERSION', 'WALL_OBSERVATION'):
            raise ObservationWall('original discovered history failed replay')
        for word in self.base.words:
            op = _cached_path(self.old, d.old_root, word).states
            np = _cached_path(self.new, d.new_root, word).states
            for o,n in zip(op,np):
                if self.forward.get(o) != n or self.reverse.get(n) != o:
                    raise ObservationWall('original selected path no longer fits pairing')
        # Every retained edge must continue to match its claimed paired action,
        # including edges discovered after construction.
        for s, a, old_t, new_s, new_t in self.edges.values():
            if self.forward.get(s) != new_s or self.forward.get(old_t) != new_t:
                raise ObservationWall('retained edge does not match stored pairing')
            if (_cached_step(self.old, s, a) != old_t or
                _cached_step(self.new, new_s, a) != new_t):
                raise ObservationWall('retained edge failed replay')
        for s, word in self.words.items():
            if (_cached_path(self.old, d.old_root, word).states[-1] != s or
                _cached_path(self.new, d.new_root, word).states[-1] != self.forward[s]):
                raise ObservationWall('rooted word no longer witnesses its paired state')
        for r in self.rejected:
            w = r.witness
            if (w.old_left != _cached_path(self.old, d.old_root, w.left_word) or
                w.old_right != _cached_path(self.old, d.old_root, w.right_word) or
                w.new_left != _cached_path(self.new, d.new_root, w.left_word) or
                w.new_right != _cached_path(self.new, d.new_root, w.right_word) or
                w.old_equal == w.new_equal or
                w.old_equal != (w.old_left.states[-1] == w.old_right.states[-1]) or
                w.new_equal != (w.new_left.states[-1] == w.new_right.states[-1])):
                raise ObservationWall('rejected-edge counterexample failed replay')

    def _report(self, status: Status, detail: str) -> ExtensionReport:
        return ExtensionReport(status, len(self.base.state_pairs), len(self.base.admitted_edges),
              tuple(sorted(self.forward.items())), tuple(sorted(self.edges.values())),
              tuple(self.new_edges), tuple(self.rejected), self.cursor,
              len(self.queue)-self.cursor, _count(self.old), _count(self.new), detail)

    def _exclude(self, s: State, a: str, old_t: State, new_t: State) -> None:
        word = self.words[s] + a
        if old_t in self.forward and self.forward[old_t] != new_t:
            old_word = self.words[old_t]
            cause = 'SOURCE_COLLISION'
        elif new_t in self.reverse and self.reverse[new_t] != old_t:
            old_word = self.words[self.reverse[new_t]]
            cause = 'TARGET_COLLISION'
        else:
            raise ObservationWall('excluded edge has no verified collision')
        d = self.discovered
        paths = (_cached_path(self.old, d.old_root, old_word),
                 _cached_path(self.old, d.old_root, word),
                 _cached_path(self.new, d.new_root, old_word),
                 _cached_path(self.new, d.new_root, word))
        witness = WordRelation(old_word, word, *paths,
                  paths[0].states[-1] == paths[1].states[-1],
                  paths[2].states[-1] == paths[3].states[-1])
        if witness.old_equal == witness.new_equal:
            raise ObservationWall('collision lacks separating word equality')
        self.rejected.append(ExcludedEdge(s, a, old_t, new_t, cause, witness))

    def advance(self, *, max_new_edges: int = 4) -> ExtensionReport:
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be an integer 0..108')
        if not self._current():
            return self._report('UNKNOWN_VERSION','Pinned source changed; retained evidence not reused.')
        try:
            self._audit()
        except (ObservationWall, ValueError, KeyError) as exc:
            return self._report('WALL_OBSERVATION',f'Replay failed: {exc}')
        if self.terminal:
            return self._final()
        spent = 0
        while self.cursor < len(self.queue):
            s,a = self.queue[self.cursor]
            if (s,a) in self.edges:
                self.cursor += 1
                continue
            new_s = self.forward[s]
            if isinstance(self.old_snapshot, PinnedEdges) and (s,a) not in self.old_snapshot.edges and spent >= max_new_edges:
                return self._report('CONTINUING','Observation allowance reached; resume without changing existing union.')
            try:
                before = _count(self.old)
                old_t = self.old_snapshot.step(s,a)
                spent += _count(self.old) - before
                if isinstance(self.new_snapshot, PinnedEdges) and (new_s,a) not in self.new_snapshot.edges and spent >= max_new_edges:
                    return self._report('CONTINUING','First edge observed; paired edge still pending.')
                before = _count(self.new)
                new_t = self.new_snapshot.step(new_s,a)
                spent += _count(self.new) - before
                if not (_owner_consistent(self.old,s,a,old_t) and
                        _owner_consistent(self.new,new_s,a,new_t)):
                    raise ObservationWall('edge contradicts bound local owner')
                if ((old_t in self.forward and self.forward[old_t] != new_t) or
                    (new_t in self.reverse and self.reverse[new_t] != old_t)):
                    self._exclude(s,a,old_t,new_t)
                else:
                    if old_t not in self.forward:
                        self.forward[old_t] = new_t
                        self.reverse[new_t] = old_t
                        self.words[old_t] = self.words[s] + a
                        self.queue.extend((old_t, label) for label in self.action_order
                                          if (old_t,label) not in self.edges)
                    edge = (s,a,old_t,new_s,new_t)
                    self.edges[(s,a)] = edge
                    self.new_edges.append(edge)
                self.cursor += 1
            except EdgeBudgetReached:
                return self._report('UNKNOWN_BUDGET','Pinned edge budget exhausted; extend it explicitly before resuming.')
            except (ObservationWall, ValueError, KeyError) as exc:
                return self._report('WALL_OBSERVATION', f'Edge investigation stopped: {exc}')
        self.terminal = True
        return self._final()

    def _final(self) -> ExtensionReport:
        owned = (self.old.origin_scope == 'LOCAL_OWNER_VERIFIED' and
                 self.new.origin_scope == 'LOCAL_OWNER_VERIFIED')
        if not self.rejected:
            status = 'ROOTED_CLOSED_' + ('WITNESSED' if owned else 'REMOTE_REPORTED')
        else:
            status = 'PARTIAL_EXTENSION_' + ('WITNESSED' if owned else 'REMOTE_REPORTED')
        return self._report(status,
            f'Checked every missing A/B edge from {len(self.forward)} admitted states. '
            f'Admitted {len(self.new_edges)} new edges; excluded {len(self.rejected)} '
            'with rooted word-equality counterexamples. Closed only if none excluded; '
            'greedy extension of one selected pairing, not a maximal universal relation.')

def _cached_step(bridge, source: State, action: str) -> State:
    snap = bridge.snapshot
    if isinstance(snap, PinnedEdges) and (source,action) not in snap.edges:
        raise ObservationWall('missing retained edge')
    target = snap.step(source,action)
    if not _owner_consistent(bridge,source,action,target):
        raise ObservationWall('retained edge contradicts owner')
    return target
