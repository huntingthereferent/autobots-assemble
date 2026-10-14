"""Witness shared and broken rooted A/B relations after the rules change.

Two independently pinned observers supply actual finite transitions. The probe
chooses A/B observations itself and builds the pointed, labeled correspondence
from coincident action words. A conflict returns explicit *two-word* evidence:
an equality of endpoints in exactly one of the two observed systems.

No unknown rule family is assumed, no coordinate alignment is supplied, and
rooted evidence makes no assertion about unvisited states or physical motion.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_language_bridge import (
    EdgeBudgetReached, LanguageBridge, ObservationWall, PinnedEdges, PathWitness,
)

RuleStatus = Literal[
    'CONTINUING', 'RELATION_CHANGED_WITNESSED', 'RELATION_CHANGED_REMOTE_REPORTED',
    'ROOTED_PRESERVED_WITNESSED', 'ROOTED_PRESERVED_REMOTE_REPORTED',
    'UNKNOWN_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]


@dataclass(frozen=True)
class WordRelation:
    left_word: str
    right_word: str
    old_left: PathWitness
    old_right: PathWitness
    new_left: PathWitness
    new_right: PathWitness
    old_equal: bool
    new_equal: bool


@dataclass(frozen=True)
class RuleChangeReport:
    status: RuleStatus
    old_version: tuple[str, int, str]
    new_version: tuple[str, int, str]
    compared_pairs: int
    old_observed_edges: int
    new_observed_edges: int
    preserved: tuple[WordRelation, ...]
    broken: WordRelation | None
    detail: str


def _version(bridge: LanguageBridge) -> tuple[str, int, str]:
    s = bridge.snapshot
    return (s.claimed_source, s.revision, s.digest)


def _count(bridge: LanguageBridge) -> int:
    snap = bridge.snapshot
    return len(snap.edges) if isinstance(snap, PinnedEdges) else len(snap.values)


def _owner_consistent(bridge: LanguageBridge, state: State, action: str, output: State) -> bool:
    """Locally bound cached evidence must still match the owner-held law."""
    snap = bridge.snapshot
    if bridge.origin_scope != 'LOCAL_OWNER_VERIFIED':
        return True
    view = getattr(snap, 'owner_view', None)
    if view is None:
        # Complete snapshots were checked at acquisition by LanguageBridge.
        return not isinstance(snap, PinnedEdges)
    return view.step(state, action) == output


def _cached_path(bridge: LanguageBridge, root: State, word: str) -> PathWitness:
    """Replay an existing observation only; never secretly acquire new edges."""
    snap = bridge.snapshot
    states = [root]
    for act in word:
        here = states[-1]
        if isinstance(snap, PinnedEdges) and (here, act) not in snap.edges:
            raise ObservationWall('missing witnessed edge in comparison path')
        output = snap.step(here, act)
        if not _owner_consistent(bridge, here, act, output):
            raise ObservationWall('cached edge differs from the bound local owner')
        states.append(output)
    return PathWitness(word, tuple(states))


class RuleChangeAgent:
    """Bounded and resumable comparison of rooted *observed* action relations.

    The first obstruction is a word equality that holds on only one side.
    Without an obstruction, exhausting the paired reachable component proves
    a rooted generator-preserving bijection, NOT a full-system bijection.
    """

    def __init__(self, old: LanguageBridge, new: LanguageBridge, *,
                 old_root: State = (0, 0, 0), new_root: State = (0, 0, 0)):
        if old_root not in DOMAIN_SET or new_root not in DOMAIN_SET:
            raise ValueError('roots must belong to the finite state domain')
        self.old, self.new = old, new
        self.old_root, self.new_root = old_root, new_root
        self.old_snap, self.new_snap = old.snapshot, new.snapshot
        self.old_version, self.new_version = _version(old), _version(new)
        self.forward: dict[State, tuple[State, str]] = {old_root: (new_root, '')}
        self.reverse: dict[State, tuple[State, str]] = {new_root: (old_root, '')}
        self.queue: deque[tuple[State, State, str]] = deque([(old_root, new_root, '')])
        self.action_cursor = 0
        self.preserved: list[WordRelation] = []
        self.broken: WordRelation | None = None
        self.terminal: RuleStatus | None = None

    def _current(self) -> bool:
        return (self.old.snapshot is self.old_snap and
                self.new.snapshot is self.new_snap and
                _version(self.old) == self.old_version and
                _version(self.new) == self.new_version)

    def _owned(self) -> bool:
        return (self.old.origin_scope == 'LOCAL_OWNER_VERIFIED' and
                self.new.origin_scope == 'LOCAL_OWNER_VERIFIED')

    def _record(self, left: str, right: str) -> WordRelation:
        a = _cached_path(self.old, self.old_root, left)
        b = _cached_path(self.old, self.old_root, right)
        c = _cached_path(self.new, self.new_root, left)
        d = _cached_path(self.new, self.new_root, right)
        return WordRelation(left, right, a, b, c, d,
                            a.states[-1] == b.states[-1],
                            c.states[-1] == d.states[-1])

    def _report(self, status: RuleStatus, detail: str) -> RuleChangeReport:
        return RuleChangeReport(status, self.old_version, self.new_version,
                                len(self.forward), _count(self.old), _count(self.new),
                                tuple(self.preserved), self.broken, detail)

    def advance(self, *, max_new_edges: int = 4) -> RuleChangeReport:
        """Observe at most this many new edges *combined* across both sides."""
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be an integer from 0 through 108')
        if not self._current():
            return self._report('UNKNOWN_VERSION', 'An observer was repinned; prior evidence retained.')
        if self.terminal is not None:
            return self._report(self.terminal, 'Previously established result; zero new edge observations.')
        used = 0
        while self.queue:
            old_state, new_state, word = self.queue[0]
            action = 'AB'[self.action_cursor]
            if any(isinstance(bridge.snapshot, PinnedEdges) and
                   (state, action) not in bridge.snapshot.edges
                   for bridge, state in ((self.old, old_state), (self.new, new_state))):
                if used >= max_new_edges:
                    return self._report('CONTINUING', 'Per-call edge budget reached; comparison can resume.')
            try:
                before = _count(self.old)
                next_old = self.old_snap.step(old_state, action)
                used += _count(self.old) - before
                # Resume from the same cursor with the cached old edge if
                # a single request's allowance is exhausted before new edge.
                if (isinstance(self.new_snap, PinnedEdges) and
                        (new_state, action) not in self.new_snap.edges and
                        used >= max_new_edges):
                    return self._report('CONTINUING', 'Per-call edge budget reached after old-side observation.')
                before = _count(self.new)
                next_new = self.new_snap.step(new_state, action)
                used += _count(self.new) - before
                if (not _owner_consistent(self.old, old_state, action, next_old) or
                        not _owner_consistent(self.new, new_state, action, next_new)):
                    raise ObservationWall('used edge disagrees with its bound local owner')
            except EdgeBudgetReached:
                return self._report('UNKNOWN_BUDGET', 'Pinned observer total budget exhausted; evidence retained.')
            except (ObservationWall, ValueError) as exc:
                return self._report('WALL_OBSERVATION', f'Observation rejected: {exc}')

            next_word = word + action
            previous_old = self.forward.get(next_old)
            previous_new = self.reverse.get(next_new)
            if previous_old is not None and previous_old[0] != next_new:
                try:
                    witness = self._record(previous_old[1], next_word)
                except ObservationWall as exc:
                    return self._report('WALL_OBSERVATION', f'Counterexample replay rejected: {exc}')
                if witness.old_equal == witness.new_equal:
                    return self._report('WALL_OBSERVATION', 'Conflict did not replay from recorded edges.')
                self.broken = witness
                self.terminal = ('RELATION_CHANGED_WITNESSED' if self._owned()
                                 else 'RELATION_CHANGED_REMOTE_REPORTED')
                return self._report(self.terminal, 'A rooted word equality differs; exact witnessed counterexample.')
            if previous_new is not None and previous_new[0] != next_old:
                try:
                    witness = self._record(previous_new[1], next_word)
                except ObservationWall as exc:
                    return self._report('WALL_OBSERVATION', f'Counterexample replay rejected: {exc}')
                if witness.old_equal == witness.new_equal:
                    return self._report('WALL_OBSERVATION', 'Conflict did not replay from recorded edges.')
                self.broken = witness
                self.terminal = ('RELATION_CHANGED_WITNESSED' if self._owned()
                                 else 'RELATION_CHANGED_REMOTE_REPORTED')
                return self._report(self.terminal, 'A rooted word equality differs; exact witnessed counterexample.')
            if previous_old is None and previous_new is None:
                self.forward[next_old] = (next_new, next_word)
                self.reverse[next_new] = (next_old, next_word)
                self.queue.append((next_old, next_new, next_word))
            else:
                # A repeated endpoint in both systems is a *witnessed*
                # equality that survives the change, not just matched labels.
                assert previous_old is not None and previous_new is not None
                try:
                    shared = self._record(previous_old[1], next_word)
                except ObservationWall as exc:
                    return self._report('WALL_OBSERVATION', f'Shared relation replay rejected: {exc}')
                if not (shared.old_equal and shared.new_equal):
                    return self._report('WALL_OBSERVATION', 'Shared relation failed cached replay.')
                if len(self.preserved) < 8:
                    self.preserved.append(shared)
            self.action_cursor += 1
            if self.action_cursor == 2:
                self.action_cursor = 0
                self.queue.popleft()
        self.terminal = ('ROOTED_PRESERVED_WITNESSED' if self._owned()
                         else 'ROOTED_PRESERVED_REMOTE_REPORTED')
        return self._report(self.terminal,
                            'Both A/B generators verified on each mapped rooted state; '
                            'off-root states not covered.')


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
    from ab_chatbot_stability_witness import TransportedLaw

    ident = tuple(DOMAIN)
    a = SourceOwnedHTTP(TransportedLaw((0, 0, 0), ident))
    b = SourceOwnedHTTP(TransportedLaw((0, 1, 2), ident))
    with LoopbackHTTP(a) as sa, LoopbackHTTP(b) as sb:
        old = LanguageBridge(RemoteObserver(sa.url, bound_loopback=sa), owner=a, edge_budget=54)
        new = LanguageBridge(RemoteObserver(sb.url, bound_loopback=sb), owner=b, edge_budget=54)
        agent = RuleChangeAgent(old, new)
        while True:
            result = agent.advance(max_new_edges=4)
            if result.status != 'CONTINUING':
                print('Result:', result.status)
                print('Mapped rooted pairs:', result.compared_pairs)
                print('Observed unique A/B edges:', result.old_observed_edges, result.new_observed_edges)
                print('Preserved word equalities:', [(w.left_word, w.right_word)
                                                    for w in result.preserved])
                if result.broken:
                    w = result.broken
                    print('Witness words:', repr(w.left_word), repr(w.right_word))
                    print('Original endpoints:', w.old_left.states[-1], w.old_right.states[-1])
                    print('Changed endpoints:', w.new_left.states[-1], w.new_right.states[-1])
                break


if __name__ == '__main__':
    main()
