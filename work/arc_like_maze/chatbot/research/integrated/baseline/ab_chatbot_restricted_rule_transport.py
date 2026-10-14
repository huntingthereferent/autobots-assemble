"""Finite, *partial* rule-change correspondence usable for new goals.

A/B here are named operations of the declared finite example, not a general
mathematics of motion. Greedy breadth-first admission builds a rooted partial
labeled graph isomorphism; a conflicting generator edge is excluded with a
replayable word-equality counterexample. No claim is made beyond admitted arcs.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_goal_agent import GoalReport
from ab_chatbot_language_bridge import (
    EdgeBudgetReached, LanguageBridge, ObservationWall, PinnedEdges, PathWitness,
)
from ab_chatbot_rule_change import WordRelation, _version, _count, _cached_path, _owner_consistent

StableStatus = Literal[
    'CONTINUING', 'RESTRICTED_SUBGRAPH_WITNESSED', 'RESTRICTED_SUBGRAPH_REMOTE_REPORTED',
    'ROOTED_PRESERVED_WITNESSED', 'ROOTED_PRESERVED_REMOTE_REPORTED',
    'UNKNOWN_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]
CarryStatus = Literal[
    'GOAL_CARRIED_WITNESSED', 'GOAL_CARRIED_REMOTE_REPORTED',
    'GOAL_OUTSIDE_RESTRICTION', 'UNKNOWN_NOT_CERTIFIED', 'UNKNOWN_VERSION',
    'WALL_OBSERVATION', 'WALL_SOURCE_GOAL',
]


@dataclass(frozen=True)
class RejectedArc:
    from_old: State
    from_new: State
    action: str
    old_destination: State
    new_destination: State
    obstruction: WordRelation


@dataclass(frozen=True)
class RestrictionReport:
    status: StableStatus
    old_version: tuple[str, int, str]
    new_version: tuple[str, int, str]
    state_pairs: tuple[tuple[State, State], ...]
    admitted: tuple[tuple[State, str, State, State], ...]
    excluded: tuple[RejectedArc, ...]
    old_observed_edges: int
    new_observed_edges: int
    detail: str


@dataclass(frozen=True)
class RestrictedGoalReport:
    status: CarryStatus
    source_target: State
    target_image: State | None
    original_path: PathWitness | None
    changed_path: PathWitness | None
    detail: str


class RestrictedRuleTransport:
    """Find/reuse a certified partial correspondence between two pinned laws.

    Breadth-first lexicographic A/B admission means the restriction depends on
    the declared choice of root and traversal order. It is not maximal, unique,
    or necessarily closed under the original two *total* generators.
    Every admitted arc is an exact witnessed commuting square on the partial
    graph; excluded arcs are not permitted for subsequent goal transport.
    """

    def __init__(self, old: LanguageBridge, new: LanguageBridge, *,
                 old_root: State = (0, 0, 0), new_root: State = (0, 0, 0), action_order: str = 'AB', frontier_mode: str = 'BFS'):
        if frontier_mode not in ('BFS', 'DFS'):
            raise ValueError('frontier_mode must be BFS or DFS')
        if action_order not in ('AB', 'BA'):
            raise ValueError('action_order must be AB or BA')
        if old_root not in DOMAIN_SET or new_root not in DOMAIN_SET:
            raise ValueError('roots must belong to the finite domain')
        self.action_order = action_order
        self.frontier_mode = frontier_mode
        self.old, self.new = old, new
        self.old_root, self.new_root = old_root, new_root
        self.old_snap, self.new_snap = old.snapshot, new.snapshot
        self.old_version, self.new_version = _version(old), _version(new)
        self.forward: dict[State, tuple[State, str]] = {old_root: (new_root, '')}
        self.reverse: dict[State, tuple[State, str]] = {new_root: (old_root, '')}
        self.queue: deque[State] = deque([old_root])
        self.active: State | None = None
        self.cursor = 0
        self.admitted: dict[tuple[State, str], tuple[State, State]] = {}
        self.excluded: list[RejectedArc] = []
        self.finished: StableStatus | None = None

    def _current(self) -> bool:
        return (self.old.snapshot is self.old_snap and self.new.snapshot is self.new_snap
                and _version(self.old) == self.old_version and _version(self.new) == self.new_version)

    def _owned(self) -> bool:
        return (self.old.origin_scope == 'LOCAL_OWNER_VERIFIED'
                and self.new.origin_scope == 'LOCAL_OWNER_VERIFIED')

    def _result(self, status: StableStatus, detail: str) -> RestrictionReport:
        return RestrictionReport(
            status, self.old_version, self.new_version,
            tuple((s, image) for s, (image, _) in self.forward.items()),
            tuple((s, a, t, v) for (s, a), (t, v) in self.admitted.items()),
            tuple(self.excluded), _count(self.old), _count(self.new), detail,
        )

    def _relation(self, left: str, right: str) -> WordRelation:
        a, b = _cached_path(self.old, self.old_root, left), _cached_path(self.old, self.old_root, right)
        c, d = _cached_path(self.new, self.new_root, left), _cached_path(self.new, self.new_root, right)
        return WordRelation(left, right, a, b, c, d,
                            a.states[-1] == b.states[-1], c.states[-1] == d.states[-1])

    def _audit(self) -> None:
        """Recheck *all* cached admitted arcs, including locally forged entries."""
        for (s, a), (old_to, new_to) in self.admitted.items():
            mapped = self.forward.get(s)
            if mapped is None or self.forward.get(old_to, (None,))[0] != new_to:
                raise ObservationWall('stored partial mapping no longer commutes')
            for bridge, src, dst in ((self.old, s, old_to), (self.new, mapped[0], new_to)):
                snap = bridge.snapshot
                if isinstance(snap, PinnedEdges) and (src, a) not in snap.edges:
                    raise ObservationWall('missing admitted edge in pinned cache')
                got = snap.step(src, a)
                if got != dst or not _owner_consistent(bridge, src, a, got):
                    raise ObservationWall('cached admitted edge inconsistent with bound owner')
        for denied in self.excluded:
            s, t, action = denied.from_old, denied.from_new, denied.action
            if (s, action) in self.admitted or self.forward.get(s, (None,))[0] != t:
                raise ObservationWall('rejected arc conflicts with admitted graph')
            for bridge, src, dst in ((self.old, s, denied.old_destination),
                                     (self.new, t, denied.new_destination)):
                snap = bridge.snapshot
                if isinstance(snap, PinnedEdges) and (src, action) not in snap.edges:
                    raise ObservationWall('missing rejected edge in pinned cache')
                out = snap.step(src, action)
                if out != dst or not _owner_consistent(bridge, src, action, out):
                    raise ObservationWall('rejected arc no longer matches cached source')
            if self._relation(denied.obstruction.left_word,
                              denied.obstruction.right_word) != denied.obstruction:
                raise ObservationWall('rejected word equality no longer replays')
            if denied.obstruction.old_equal == denied.obstruction.new_equal:
                raise ObservationWall('rejection did not demonstrate different relations')
        # Every mapped vertex must have a path entirely in the admitted graph.
        for s, (image, word) in self.forward.items():
            os, ns = self.old_root, self.new_root
            for act in word:
                arc = self.admitted.get((os, act))
                if arc is None:
                    raise ObservationWall('rooted admission history contains a missing arc')
                os, ns = arc
            if (os, ns) != (s, image):
                raise ObservationWall('admitted path no longer reaches recorded pair')

    def advance(self, *, max_new_edges: int = 4) -> RestrictionReport:
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be 0..108')
        if not self._current():
            return self._result('UNKNOWN_VERSION', 'An observer was repinned; prior evidence retained.')
        if self.finished is not None:
            try:
                self._audit()
            except (ObservationWall, ValueError) as exc:
                return self._result('WALL_OBSERVATION', f'Cached witness audit rejected: {exc}')
            return self._result(self.finished, 'Previously certified restriction reused; no new edge observations.')
        used = 0
        while self.active is not None or self.queue:
            if self.active is None:
                self.active = (self.queue.popleft() if self.frontier_mode == 'BFS'
                               else self.queue.pop())
            s = self.active
            target_s, word = self.forward[s]
            act = self.action_order[self.cursor]
            if (isinstance(self.old_snap, PinnedEdges) and (s, act) not in self.old_snap.edges
                    and used >= max_new_edges) or (
                isinstance(self.new_snap, PinnedEdges) and (target_s, act) not in self.new_snap.edges
                    and used >= max_new_edges):
                return self._result('CONTINUING', 'Per-call edge observation limit reached.')
            try:
                before = _count(self.old)
                old_to = self.old_snap.step(s, act)
                used += _count(self.old) - before
                if (isinstance(self.new_snap, PinnedEdges) and
                        (target_s, act) not in self.new_snap.edges and used >= max_new_edges):
                    return self._result('CONTINUING', 'Budget reached after old-side observation; safe to resume.')
                before = _count(self.new)
                new_to = self.new_snap.step(target_s, act)
                used += _count(self.new) - before
                if (not _owner_consistent(self.old, s, act, old_to) or
                        not _owner_consistent(self.new, target_s, act, new_to)):
                    raise ObservationWall('observed edge disagrees with its bound owner')
                prev_old, prev_new = self.forward.get(old_to), self.reverse.get(new_to)
                if ((prev_old is not None and prev_old[0] != new_to) or
                        (prev_new is not None and prev_new[0] != old_to)):
                    competing = prev_old[1] if prev_old is not None and prev_old[0] != new_to else prev_new[1]
                    conflict = self._relation(competing, word + act)
                    if conflict.old_equal == conflict.new_equal:
                        raise ObservationWall('excluded edge did not produce a replayable mismatch')
                    self.excluded.append(RejectedArc(s, target_s, act, old_to, new_to, conflict))
                else:
                    self.admitted[(s, act)] = (old_to, new_to)
                    if prev_old is None:
                        self.forward[old_to] = (new_to, word + act)
                        self.reverse[new_to] = (old_to, word + act)
                        self.queue.append(old_to)
                self.cursor += 1
                if self.cursor == 2:
                    self.cursor = 0
                    self.active = None
            except EdgeBudgetReached:
                return self._result('UNKNOWN_BUDGET', 'Pinned total edge budget exhausted; no hidden increase.')
            except (ObservationWall, ValueError) as exc:
                return self._result('WALL_OBSERVATION', f'Observation rejected: {exc}')
        try:
            self._audit()
        except (ObservationWall, ValueError) as exc:
            return self._result('WALL_OBSERVATION', f'Final partial-map audit rejected: {exc}')
        self.finished = (('RESTRICTED_SUBGRAPH_' if self.excluded else 'ROOTED_PRESERVED_') +
                         ('WITNESSED' if self._owned() else 'REMOTE_REPORTED'))
        return self._result(self.finished,
                            'Rooted partial labeled graph verified on admitted edges; '
                            'excluded edges prohibit transport, off-graph paths unknown.')

    def carry_target(self, source_target: State) -> RestrictedGoalReport:
        if source_target not in DOMAIN_SET:
            raise ValueError('target outside finite domain')
        if not self._current():
            return RestrictedGoalReport('UNKNOWN_VERSION', source_target, None, None, None,
                                        'Pinned version changed, no goal transported.')
        if self.finished is None:
            return RestrictedGoalReport('UNKNOWN_NOT_CERTIFIED', source_target, None, None, None,
                                        'Partial correspondence has not completed edge audit.')
        try:
            self._audit()
            if source_target not in self.forward:
                return RestrictedGoalReport('GOAL_OUTSIDE_RESTRICTION', source_target, None, None, None,
                                            'No admitted path to target; not a claim of global unreachability.')
            image, word = self.forward[source_target]
            orig = _cached_path(self.old, self.old_root, word)
            changed = _cached_path(self.new, self.new_root, word)
            if orig.states[-1] != source_target or changed.states[-1] != image:
                raise ObservationWall('goal path does not reach mapped endpoints')
            os = self.old_root
            for a in word:
                arc = self.admitted.get((os, a))
                if arc is None:
                    raise ObservationWall('goal path crossed excluded or unobserved edge')
                os = arc[0]
            return RestrictedGoalReport(
                'GOAL_CARRIED_WITNESSED' if self._owned() else 'GOAL_CARRIED_REMOTE_REPORTED',
                source_target, image, orig, changed,
                'Goal independently planned along admitted subgraph; no new observations.')
        except (ObservationWall, ValueError) as exc:
            return RestrictedGoalReport('WALL_OBSERVATION', source_target, None, None, None,
                                        f'Cached witness replay failed: {exc}')

    def carry_prior_goal(self, source_goal: GoalReport) -> RestrictedGoalReport:
        """Validate a prior original-system goal, then find an admitted route.

        The prior path might cross an excluded edge: never silently transport it.
        A *new* admissible route is chosen by rooted BFS admission instead.
        """
        source_target = source_goal.target
        if not self._current():
            return RestrictedGoalReport('UNKNOWN_VERSION', source_target, None, None, None,
                                        'Pinned version changed.')
        path = source_goal.path
        if (source_goal.status not in ('COMPLETE_WITNESSED', 'COMPLETE_REMOTE_REPORTED') or
                path is None or source_goal.start != self.old_root or
                source_goal.pinned_version != self.old_version or
                source_goal.origin_scope != self.old.origin_scope or
                not path.states or path.states[0] != self.old_root or
                path.states[-1] != source_target or
                len(path.states) != len(path.word) + 1 or
                any(x not in 'AB' for x in path.word)):
            return RestrictedGoalReport('WALL_SOURCE_GOAL', source_target, None, None, None,
                                        'Prior goal lacks compatible pinned witness.')
        try:
            actual = _cached_path(self.old, self.old_root, path.word)
            if actual != path:
                raise ObservationWall('prior goal witness differs from cached observations')
        except (ObservationWall, ValueError) as exc:
            return RestrictedGoalReport('WALL_SOURCE_GOAL', source_target, None, None, None,
                                        f'Prior goal replay failed: {exc}')
        return self.carry_target(source_target)


def main() -> None:
    from ab_chatbot_discovered_correspondence import DOMAIN
    from ab_chatbot_goal_agent import GoalAgent
    from ab_chatbot_http_snapshot import LoopbackHTTP, RemoteObserver, SourceOwnedHTTP
    from ab_chatbot_stability_witness import TransportedLaw

    ident = tuple(DOMAIN)
    a, b = (SourceOwnedHTTP(TransportedLaw(phi, ident)) for phi in ((0, 0, 0), (0, 1, 2)))
    with LoopbackHTTP(a) as sa, LoopbackHTTP(b) as sb:
        old = LanguageBridge(RemoteObserver(sa.url, bound_loopback=sa), owner=a, edge_budget=54)
        new = LanguageBridge(RemoteObserver(sb.url, bound_loopback=sb), owner=b, edge_budget=54)
        agent = RestrictedRuleTransport(old, new)
        while True:
            result = agent.advance(max_new_edges=3)
            if result.status != 'CONTINUING':
                break
        print('Restriction:', result.status, 'pairs:', len(result.state_pairs),
              'admitted:', len(result.admitted), 'excluded:', len(result.excluded),
              'unique edge reads:', result.old_observed_edges, result.new_observed_edges)
        goal = GoalAgent(old, (0, 2, 0))
        while True:
            solved = goal.advance(max_new_edges=2)
            if solved.status != 'CONTINUING':
                break
        carried = agent.carry_prior_goal(solved)
        print('Prior goal:', solved.status, 'prior route:', solved.path.word if solved.path else None)
        print('Carried:', carried.status, 'route:', carried.changed_path.word if carried.changed_path else None,
              'image:', carried.target_image)
        print('Continue with B from mapped goal:',
              agent.admitted.get(((0, 2, 0), 'B')))


if __name__ == '__main__':
    main()
