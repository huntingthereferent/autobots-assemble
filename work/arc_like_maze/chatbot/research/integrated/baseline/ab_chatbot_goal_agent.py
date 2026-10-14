"""Bounded constructive A/B *mathematical* task agent, not a definition of A/B.

Find a path to an explicitly chosen state using the existing pinned mathematical
observer. The agent chooses questions (state, A/B generator) by breadth-first
search and *only* extends its model with witnessed answers. It does not infer
unobserved transitions or require an LLM to choose the next question.

COMPLETE proves only a concrete path for a particular pinned finite model.
UNREACHABLE is justified only after every reachable outgoing edge is read.
A bounded search or observation budget returns an explicit limited result.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET
from ab_chatbot_language_bridge import (
    EdgeBudgetReached, LanguageBridge, ObservationWall, PinnedEdges,
    PathWitness, State,
)

Outcome = Literal[
    'CONTINUING', 'COMPLETE_WITNESSED', 'COMPLETE_REMOTE_REPORTED', 'UNKNOWN_BUDGET', 'UNKNOWN_VERSION',
    'WALL_OBSERVATION', 'NO_ROUTE_WITHIN_DEPTH', 'UNREACHABLE_CLOSED_COMPONENT',
]


@dataclass(frozen=True)
class GoalReport:
    status: Outcome
    start: State
    target: State
    pinned_version: tuple[str, int, str]
    origin_scope: str
    observed_edges: int
    explored_states: int
    path: PathWitness | None
    detail: str


class GoalAgent:
    """Reusable autonomous chooser of the *next finite observation*.

    `advance` uses no more than `max_new_edges` previously unseen transitions;
    repeat calls continue the SAME question and observations. The lower-level
    snapshot's explicit total edge budget is never silently raised.
    """

    def __init__(self, bridge: LanguageBridge, target: State,
                 *, start: State = (0, 0, 0), max_depth: int = 26):
        if start not in DOMAIN_SET or target not in DOMAIN_SET:
            raise ValueError('start and target must belong to F3^3')
        if type(max_depth) is not int or not 0 <= max_depth <= 26:
            raise ValueError('max_depth must be an integer from 0 to 26')
        self.bridge = bridge
        self.snapshot = bridge.snapshot
        self.start, self.target, self.max_depth = start, target, max_depth
        self.version = self._version(self.snapshot)
        self.origin_scope = bridge.origin_scope
        self.parents: dict[State, tuple[State, str] | None] = {start: None}
        self.depths: dict[State, int] = {start: 0}
        self.pending = deque([start])
        self._action_cursor = 0
        self._cutoff = False
        self._path: PathWitness | None = None
        self._ended: Outcome | None = None
        if start == target:
            self._path = PathWitness('', (start,))
            self._ended = self._completion_status()

    def _completion_status(self) -> Outcome:
        return ('COMPLETE_WITNESSED' if self.origin_scope == 'LOCAL_OWNER_VERIFIED'
                else 'COMPLETE_REMOTE_REPORTED')

    @staticmethod
    def _version(snap) -> tuple[str, int, str]:
        return snap.claimed_source, snap.revision, snap.digest

    def _edge_count(self) -> int:
        if isinstance(self.snapshot, PinnedEdges):
            return len(self.snapshot.edges)
        return len(self.snapshot.values)  # pre-fetched, coherent mathematical table

    def _replay(self, target: State) -> PathWitness:
        actions = []
        here = target
        while here != self.start:
            parent = self.parents[here]
            assert parent is not None
            before, symbol = parent
            actions.append(symbol)
            here = before
        word = ''.join(reversed(actions))
        here = self.start
        states = [here]
        for symbol in word:
            # These exact transitions were already witnessed; no new requests.
            key = (here, symbol)
            if isinstance(self.snapshot, PinnedEdges):
                assert key in self.snapshot.edges
            here = self.snapshot.step(here, symbol)
            states.append(here)
        if here != target:
            raise ObservationWall('stored plan fails witnessed-path replay')
        return PathWitness(word, tuple(states))

    def _report(self, status: Outcome, detail: str) -> GoalReport:
        return GoalReport(status, self.start, self.target, self.version,
                          self.origin_scope, self._edge_count(),
                          len(self.parents), self._path, detail)

    def authorize_total_edge_budget(self, new_max: int) -> None:
        """Caller explicitly permits a larger total budget; never automatic."""
        if self.bridge.snapshot is not self.snapshot:
            raise ValueError('cannot reauthorize observations on replaced version')
        if not isinstance(self.snapshot, PinnedEdges):
            raise ValueError('a full snapshot has no incremental edge budget')
        if (type(new_max) is not int or not
                self.snapshot.max_edges <= new_max <= 54):
            raise ValueError('budget must be a nondecreasing integer up to 54')
        self.snapshot.max_edges = new_max

    def advance(self, *, max_new_edges: int = 4) -> GoalReport:
        """Construct, observe, reuse and verify until this call's budget ends."""
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 54:
            raise ValueError('max_new_edges must be 0..54')
        if self.bridge.snapshot is not self.snapshot or self._version(self.bridge.snapshot) != self.version:
            return self._report('UNKNOWN_VERSION',
                                'Underlying observer moved to another pinned version; old task is preserved.')
        if self._ended is not None:
            return self._report(self._ended, 'Previously established terminal result; no new reads.')
        new_edges = 0
        while self.pending:
            here = self.pending[0]
            depth = self.depths[here]
            if depth >= self.max_depth:
                self._cutoff = True
                self.pending.popleft()
                self._action_cursor = 0
                continue
            symbol = ('A', 'B')[self._action_cursor]
            key = (here, symbol)
            if (isinstance(self.snapshot, PinnedEdges) and
                    key not in self.snapshot.edges and new_edges >= max_new_edges):
                return self._report('CONTINUING',
                                    'Per-call observation limit reached; repeat to continue.')
            before = self._edge_count()
            try:
                next_state = self.snapshot.step(here, symbol)
            except EdgeBudgetReached:
                return self._report('UNKNOWN_BUDGET',
                                    'Pinned total observation budget exhausted; prior evidence retained.')
            except ObservationWall as exc:
                return self._report('WALL_OBSERVATION', f'Observation rejected: {exc}')
            new_edges += self._edge_count() - before
            self._action_cursor += 1
            if self._action_cursor == 2:
                self.pending.popleft()
                self._action_cursor = 0
            if next_state not in self.parents:
                self.parents[next_state] = (here, symbol)
                self.depths[next_state] = depth + 1
                if next_state == self.target:
                    self._path = self._replay(next_state)
                    self._ended = self._completion_status()
                    return self._report(self._ended,
                                        'Target reached by replayed observations on the pinned model; '
                                        'breadth-first search gives a shortest action word. '
                                        'Only explicitly bound local owners have verified provenance.')
                self.pending.append(next_state)
        self._ended = ('NO_ROUTE_WITHIN_DEPTH' if self._cutoff
                       else 'UNREACHABLE_CLOSED_COMPONENT')
        detail = ('No action word within the declared depth reaches target.'
                  if self._cutoff else
                  'All A/B outgoing edges of the reachable component were observed; target absent.')
        return self._report(self._ended, detail)


def main() -> None:
    import argparse
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
    from ab_chatbot_stability_witness import TransportedLaw

    parser = argparse.ArgumentParser(description='Low-budget witnessed finite task agent')
    parser.add_argument('--target', default='1,2,2', help='target triple (e.g. 1,2,2)')
    parser.add_argument('--budget', type=int, default=12, help='total unique edge observations (0..54)')
    parser.add_argument('--per-call', type=int, default=3, help='new edge reads per continuation')
    parser.add_argument('--max-depth', type=int, default=26)
    args = parser.parse_args()
    target = tuple(int(v) for v in args.target.split(','))
    h = tuple((i, j, (k+i*j) % 3) for i, j, k in DOMAIN)
    owner = SourceOwnedHTTP(TransportedLaw((0, 1, 2), h))
    with LoopbackHTTP(owner) as server:
        observer = RemoteObserver(server.url, bound_loopback=server)
        bridge = LanguageBridge(observer, owner=owner, edge_budget=args.budget)
        task = GoalAgent(bridge, target, max_depth=args.max_depth)
        while True:
            report = task.advance(max_new_edges=args.per_call)
            print(f'{report.status}: states={report.explored_states}, '
                  f'edges={report.observed_edges}, version={report.pinned_version[1]}')
            if report.status != 'CONTINUING':
                print(report.detail)
                if report.path is not None:
                    print('WITNESSED ACTIONS:', report.path.word or '(identity)')
                    print('STATE PATH:', ' -> '.join(map(str, report.path.states)))
                break


if __name__ == '__main__':
    main()
