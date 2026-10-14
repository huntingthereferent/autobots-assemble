"""Carry an observed finite goal through independently discovered rooted A/B correspondence.

This is a scoped composition of EXISTING discovery and GoalAgent witnesses,
not a newly invented relation or a general claim about A/B/motion.

The discovery sees only target .step observations and never receives an H.
A positive rooted mapping certifies generator intertwining only on the
source-root-reachable carrier. No off-orbit or full-system claim follows.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_relation_probe import FiniteSystem
from ab_chatbot_discovered_correspondence import (
    DOMAIN_SET, Discovery, State, discover,
)
from ab_chatbot_language_bridge import (
    EdgeBudgetReached, LanguageBridge, ObservationWall, PinnedEdges,
    PathWitness,
)
from ab_chatbot_goal_agent import GoalReport

TransportStatus = Literal[
    'PRESERVED_ROOTED_WITNESSED', 'PRESERVED_ROOTED_REMOTE_REPORTED',
    'UNKNOWN_RELATION_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
    'ROOTED_OBSTRUCTED', 'WALL_SOURCE_GOAL',
]


def _version(bridge: LanguageBridge) -> tuple[str, int, str]:
    s = bridge.snapshot
    return (s.claimed_source, s.revision, s.digest)


def _cached(bridge: LanguageBridge, s: State, action: str) -> State | None:
    snap = bridge.snapshot
    if isinstance(snap, PinnedEdges):
        return snap.edges.get((s, action))
    return snap.step(s, action)  # a complete fixed-version snapshot


def _check_rooted(source: FiniteSystem, record: Discovery, root: State,
                  image_root: State) -> bool:
    """Independently replay restricted conjugacy from *recorded* target edges."""
    if record.status != 'ROOTED_REACHABLE':
        return False
    mapping = dict(record.rooted_pairs)
    observed = {(e.state, e.action): e.output for e in record.observed}
    if (not mapping or len(mapping) != len(record.rooted_pairs) or
            len(set(mapping.values())) != len(mapping) or
            mapping.get(root) != image_root or
            set(mapping) - DOMAIN_SET or set(mapping.values()) - DOMAIN_SET):
        return False
    # Every mapped source state must be reachable from root within mapped set;
    # both generator squares must be witnessed for every mapped state.
    reached = {root}
    queue = [root]
    while queue:
        s = queue.pop(0)
        for action in 'AB':
            t = source.step(s, action)
            if t not in mapping:
                return False
            if observed.get((mapping[s], action)) != mapping[t]:
                return False
            if t not in reached:
                reached.add(t)
                queue.append(t)
    return reached == set(mapping) and len(observed) == 2 * len(mapping)


@dataclass(frozen=True)
class TransportReport:
    status: TransportStatus
    source_version: tuple[str, int, str]
    target_version: tuple[str, int, str]
    source_rooted_states: int
    target_new_edge_reads: int
    transported_path: PathWitness | None
    detail: str


class RootedGoalTransport:
    """Discovers one rooted finite correspondence then reuses it for goal paths.

    Caller provides a declared source mathematical model, NOT the target
    coordinate mapping. No transfer is issued until the same original source
    path is independently replayed using observations already in the cache.
    """
    def __init__(self, source_law: FiniteSystem,
                 source_bridge: LanguageBridge, target_bridge: LanguageBridge,
                 *, source_root: State = (0, 0, 0),
                 target_root: State = (0, 0, 0)):
        if type(source_law) is not FiniteSystem:
            raise TypeError('source law must be a declared FiniteSystem')
        if source_root not in DOMAIN_SET or target_root not in DOMAIN_SET:
            raise ValueError('roots must be declared states')
        self.source_law, self.source_bridge, self.target_bridge = (
            source_law, source_bridge, target_bridge)
        self.source_root, self.target_root = source_root, target_root
        self.source_snap, self.target_snap = source_bridge.snapshot, target_bridge.snapshot
        self.source_version, self.target_version = _version(source_bridge), _version(target_bridge)
        self.discovery: Discovery | None = None
        self.new_target_edges = 0
        self.failed_status: TransportStatus | None = None
        self.failure_detail = ''

    def _current(self) -> bool:
        return (self.source_bridge.snapshot is self.source_snap and
                self.target_bridge.snapshot is self.target_snap and
                _version(self.source_bridge) == self.source_version and
                _version(self.target_bridge) == self.target_version)

    def _result(self, status: TransportStatus, detail: str,
                path: PathWitness | None = None) -> TransportReport:
        return TransportReport(status, self.source_version, self.target_version,
                               len(self.discovery.rooted_pairs) if self.discovery else 0,
                               self.new_target_edges, path, detail)

    def establish(self, *, max_queries: int = 54) -> TransportReport:
        """Query *at most* max_queries distinct target edges in discovery.

        This is an overall discovery observation bound, not a hidden increase
        of the underlying HTTP observer's explicit budget.
        """
        if not self._current():
            return self._result('UNKNOWN_VERSION', 'One observer was repinned; prior task unchanged.')
        if self.discovery is not None:
            return self._result('PRESERVED_ROOTED_WITNESSED' if
                                self.target_bridge.origin_scope == 'LOCAL_OWNER_VERIFIED'
                                else 'PRESERVED_ROOTED_REMOTE_REPORTED',
                                'Previously checked rooted relation reused; zero additional reads.')
        if self.failed_status and self.failed_status not in ('UNKNOWN_RELATION_BUDGET',):
            return self._result(self.failed_status, self.failure_detail)
        if type(max_queries) is not int or not 0 <= max_queries <= 54:
            raise ValueError('max_queries must be 0..54')
        prior = len(self.target_snap.edges) if isinstance(self.target_snap, PinnedEdges) else 54
        try:
            rec = discover(self.source_law, self.target_snap.step,
                           source_root=self.source_root,
                           target_root=self.target_root,
                           full=False, max_queries=max_queries)
        except EdgeBudgetReached:
            rec = None
            self.failed_status, self.failure_detail = (
                'UNKNOWN_RELATION_BUDGET', 'Target observer total edge budget reached; old observations retained.')
        except (ObservationWall, ValueError) as err:
            rec = None
            self.failed_status, self.failure_detail = ('WALL_OBSERVATION', f'Target observation rejected: {err}')
        after = len(self.target_snap.edges) if isinstance(self.target_snap, PinnedEdges) else 54
        self.new_target_edges += after-prior
        if rec is None:
            return self._result(self.failed_status, self.failure_detail)
        if rec.status == 'UNKNOWN_QUERY_BUDGET':
            self.failed_status = 'UNKNOWN_RELATION_BUDGET'
            self.failure_detail = 'Declared discovery-query cap reached; no rooted relation yet certified.'
            return self._result(self.failed_status, self.failure_detail)
        if rec.status != 'ROOTED_REACHABLE':
            self.failed_status = 'ROOTED_OBSTRUCTED' if rec.status == 'ROOTED_OBSTRUCTED' else 'WALL_OBSERVATION'
            self.failure_detail = f'Discovery ended with {rec.status}: {rec.detail}'
            return self._result(self.failed_status, self.failure_detail)
        if not _check_rooted(self.source_law, rec, self.source_root, self.target_root):
            self.failed_status = 'WALL_OBSERVATION'
            self.failure_detail = 'Recorded rooted squares did not replay.'
            return self._result(self.failed_status, self.failure_detail)
        self.discovery = rec
        self.failed_status = None
        return self._result('PRESERVED_ROOTED_WITNESSED' if
                            self.target_bridge.origin_scope == 'LOCAL_OWNER_VERIFIED'
                            else 'PRESERVED_ROOTED_REMOTE_REPORTED',
                            'Explicit two-generator rooted correspondence replayed; off-orbit relation unknown.')

    def carry(self, prior_goal: GoalReport, *, max_queries: int = 54) -> TransportReport:
        if not self._current():
            return self._result('UNKNOWN_VERSION', 'Observer version changed; no route transported.')
        # A fabricated GoalReport isn't a mathematical witness. Replay it from
        # actual *cached* original-source observations, without new source calls.
        path = prior_goal.path
        if (prior_goal.status not in ('COMPLETE_WITNESSED', 'COMPLETE_REMOTE_REPORTED') or
                path is None or not path.states or
                prior_goal.start != self.source_root or
                path.states[0] != self.source_root or
                path.states[-1] != prior_goal.target or
                len(path.states) != len(path.word)+1 or
                any(a not in 'AB' for a in path.word) or
                prior_goal.pinned_version != self.source_version or
                prior_goal.origin_scope != self.source_bridge.origin_scope):
            return self._result('WALL_SOURCE_GOAL', 'Source goal does not replay its declared scope.')
        for i, action in enumerate(path.word):
            s, t = path.states[i:i+2]
            if (_cached(self.source_bridge, s, action) != t or
                    self.source_law.step(s, action) != t):
                return self._result('WALL_SOURCE_GOAL', 'Source path disagrees with cached observation or declared model.')
        established = self.establish(max_queries=max_queries)
        if self.discovery is None:
            return established
        mapping = dict(self.discovery.rooted_pairs)
        if any(s not in mapping for s in path.states):
            return self._result('WALL_SOURCE_GOAL', 'Goal escaped certified source-rooted carrier.')
        translated = tuple(mapping[s] for s in path.states)
        recorded = {(e.state, e.action): e.output for e in self.discovery.observed}
        if any(recorded.get((translated[i], action)) != translated[i+1]
               for i, action in enumerate(path.word)):
            return self._result('WALL_OBSERVATION', 'Transported generator square failed recorded replay.')
        verified = (self.source_bridge.origin_scope == 'LOCAL_OWNER_VERIFIED' and
                    self.target_bridge.origin_scope == 'LOCAL_OWNER_VERIFIED' and
                    prior_goal.status == 'COMPLETE_WITNESSED')
        return self._result('PRESERVED_ROOTED_WITNESSED' if verified else
                            'PRESERVED_ROOTED_REMOTE_REPORTED',
                            'Same action word preserved through verified rooted mapping; '
                            'state labels need not match. No full-state or external-world claim.',
                            PathWitness(path.word, translated))


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_goal_agent import GoalAgent
    from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
    from ab_chatbot_stability_witness import TransportedLaw

    phi = (0, 0, 0)
    ident = tuple(DOMAIN)
    shear = tuple((i, j, (k+i*j)%3) for i, j, k in DOMAIN)
    a = SourceOwnedHTTP(TransportedLaw(phi, ident))
    b = SourceOwnedHTTP(TransportedLaw(phi, shear))
    with LoopbackHTTP(a) as sa, LoopbackHTTP(b) as sb:
        ba = LanguageBridge(RemoteObserver(sa.url, bound_loopback=sa), owner=a, edge_budget=54)
        bb = LanguageBridge(RemoteObserver(sb.url, bound_loopback=sb), owner=b, edge_budget=54)
        goal = GoalAgent(ba, (1, 2, 0)).advance(max_new_edges=54)
        trans = RootedGoalTransport(FiniteSystem(phi), ba, bb)
        result = trans.carry(goal, max_queries=18)
        print('Original:', goal.status, goal.path)
        print('Transport:', result.status, result.transported_path)
        print('Rooted relation:', result.source_rooted_states, 'states; new target reads:', result.target_new_edge_reads)


if __name__ == '__main__':
    main()
