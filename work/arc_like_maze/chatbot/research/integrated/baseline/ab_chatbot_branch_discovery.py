"""Evidence-first branching discovery of finite *path restrictions*.

Rather than choose between preset BFS/DFS greedy maps, extend all currently
admissible A/B path prefixes to a declared depth. Each path's visited-state
pairing is required to be injective and functionally consistent. Rejected
extensions preserve a replayable word-equality obstruction. Completed goal
routes are partial rooted labeled correspondences on their *admitted paths*,
not full-system maps, maximal restrictions, or physical movement claims.

Exploration is breadth-first over action words, with a hard depth limit and
pinned per-source observation budgets. A negative result means only that no
consistent goal path was found under the declared bound.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_language_bridge import (
    EdgeBudgetReached, LanguageBridge, ObservationWall, PinnedEdges, PathWitness,
)
from ab_chatbot_rule_change import WordRelation, _version, _count, _cached_path, _owner_consistent

BranchStatus = Literal[
    'CONTINUING', 'GOAL_CARRIED_WITNESSED', 'GOAL_CARRIED_REMOTE_REPORTED',
    'GOAL_OUTSIDE_SEARCH_BOUND', 'UNKNOWN_BUDGET', 'UNKNOWN_VERSION',
    'WALL_OBSERVATION',
]


@dataclass(frozen=True)
class PathRestriction:
    """One independently checkable restriction on the edges of a rooted path."""
    word: str
    original_path: PathWitness
    changed_path: PathWitness
    pairing: tuple[tuple[State, State], ...]

    @property
    def source_target(self) -> State:
        return self.original_path.states[-1]

    @property
    def target_image(self) -> State:
        return self.changed_path.states[-1]


@dataclass(frozen=True)
class RejectedBranch:
    attempted_word: str
    obstruction: WordRelation
    cause: str


@dataclass(frozen=True)
class BranchReport:
    status: BranchStatus
    source_target: State
    selected: PathRestriction | None
    alternatives: tuple[PathRestriction, ...]
    rejected: tuple[RejectedBranch, ...]
    explored_prefixes: int
    admitted_extensions: int
    depth_limit: int
    old_observed_edges: int
    new_observed_edges: int
    detail: str


@dataclass(frozen=True)
class _Prefix:
    word: str
    old_states: tuple[State, ...]
    new_states: tuple[State, ...]


class BranchDiscoverer:
    """Enumerate self-consistent path pairings up to ``max_depth``.

    No candidate path word or state correspondence is provided in advance.
    An additional path can be admitted even if an earlier greedy whole-rooted
    restriction excluded a different edge. This is *branching path search*,
    not exhaustive enumeration of all possible partial graph isomorphisms.
    """

    def __init__(self, old: LanguageBridge, new: LanguageBridge, source_target: State,
                 *, old_root: State = (0, 0, 0), new_root: State = (0, 0, 0),
                 max_depth: int = 7):
        if source_target not in DOMAIN_SET or old_root not in DOMAIN_SET or new_root not in DOMAIN_SET:
            raise ValueError('goal and roots must lie in the declared 27-state domain')
        if type(max_depth) is not int or not 0 <= max_depth <= 8:
            raise ValueError('max_depth must be an integer between 0 and 8')
        self.old, self.new = old, new
        self.target = source_target
        self.old_root, self.new_root = old_root, new_root
        self.old_snap, self.new_snap = old.snapshot, new.snapshot
        self.old_version, self.new_version = _version(old), _version(new)
        self.max_depth = max_depth
        root = _Prefix('', (old_root,), (new_root,))
        self.frontier = deque([root])
        self.active: _Prefix | None = None
        self.cursor = 0
        self.prefixes: list[_Prefix] = [root]
        self.rejected: list[RejectedBranch] = []
        self.goals: list[PathRestriction] = []
        if source_target == old_root:
            self.goals.append(self._candidate(root))
        self.explored = 0
        self.finished = False

    @staticmethod
    def _candidate(prefix: _Prefix) -> PathRestriction:
        # Dictionary preserves discovery order, including the starting pair.
        paired = tuple(dict(zip(prefix.old_states, prefix.new_states)).items())
        return PathRestriction(prefix.word,
                               PathWitness(prefix.word, prefix.old_states),
                               PathWitness(prefix.word, prefix.new_states), paired)

    def _current(self) -> bool:
        return (self.old.snapshot is self.old_snap and self.new.snapshot is self.new_snap
                and _version(self.old) == self.old_version and _version(self.new) == self.new_version)

    def _owned(self) -> bool:
        return (self.old.origin_scope == 'LOCAL_OWNER_VERIFIED'
                and self.new.origin_scope == 'LOCAL_OWNER_VERIFIED')

    def _report(self, status: BranchStatus, detail: str) -> BranchReport:
        candidates = tuple(sorted(self.goals, key=lambda p: (len(p.word), p.word, p.target_image)))
        return BranchReport(status, self.target, candidates[0] if candidates else None,
                            candidates, tuple(self.rejected), self.explored,
                            len(self.prefixes) - 1, self.max_depth,
                            _count(self.old), _count(self.new), detail)

    def _reject(self, prefix: _Prefix, action: str, old_next: State,
                new_next: State, old_index: int | None, new_index: int | None) -> None:
        if old_index is not None:
            index, cause = old_index, 'SOURCE_COLLISION'
        else:
            assert new_index is not None
            index, cause = new_index, 'TARGET_COLLISION'
        old_full = prefix.old_states + (old_next,)
        new_full = prefix.new_states + (new_next,)
        attempted = prefix.word + action
        old_equal = prefix.old_states[index] == old_next
        new_equal = prefix.new_states[index] == new_next
        if old_equal == new_equal:
            raise ObservationWall('rejected extension lacks a separating equality witness')
        relation = WordRelation(
            prefix.word[:index], attempted,
            PathWitness(prefix.word[:index], prefix.old_states[:index+1]),
            PathWitness(attempted, old_full),
            PathWitness(prefix.word[:index], prefix.new_states[:index+1]),
            PathWitness(attempted, new_full), old_equal, new_equal)
        self.rejected.append(RejectedBranch(attempted, relation, cause))

    def _audit(self) -> None:
        """Replay every admitted and rejected observed path from pinned caches."""
        for prefix in self.prefixes:
            if (_cached_path(self.old, self.old_root, prefix.word).states != prefix.old_states or
                    _cached_path(self.new, self.new_root, prefix.word).states != prefix.new_states):
                raise ObservationWall('stored admitted path no longer replays')
            fwd, reverse = {}, {}
            for o, n in zip(prefix.old_states, prefix.new_states):
                if (o in fwd and fwd[o] != n) or (n in reverse and reverse[n] != o):
                    raise ObservationWall('stored admitted pairing is inconsistent')
                fwd[o], reverse[n] = n, o
        for rejection in self.rejected:
            r = rejection.obstruction
            replay = (
                _cached_path(self.old, self.old_root, r.left_word),
                _cached_path(self.old, self.old_root, r.right_word),
                _cached_path(self.new, self.new_root, r.left_word),
                _cached_path(self.new, self.new_root, r.right_word),
            )
            if replay != (r.old_left, r.old_right, r.new_left, r.new_right):
                raise ObservationWall('stored rejection paths no longer replay')
            if (r.old_equal != (r.old_left.states[-1] == r.old_right.states[-1]) or
                    r.new_equal != (r.new_left.states[-1] == r.new_right.states[-1]) or
                    r.old_equal == r.new_equal or r.right_word != rejection.attempted_word):
                raise ObservationWall('stored rejection has no genuine collision witness')
        for candidate in self.goals:
            if candidate.original_path.states[-1] != self.target:
                raise ObservationWall('candidate does not reach requested goal')
            if candidate not in tuple(self._candidate(p) for p in self.prefixes):
                raise ObservationWall('candidate has no admitted prefix history')

    def advance(self, *, max_new_edges: int = 4) -> BranchReport:
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be an integer from 0 to 108')
        if not self._current():
            return self._report('UNKNOWN_VERSION', 'Pinned source changed; existing evidence retained.')
        try:
            self._audit()
        except (ObservationWall, ValueError) as exc:
            return self._report('WALL_OBSERVATION', f'Observed evidence failed replay: {exc}')
        if self.finished:
            return self._finish()
        used = 0
        while self.active is not None or self.frontier:
            if self.active is None:
                prefix = self.frontier.popleft()
                if len(prefix.word) >= self.max_depth:
                    continue
                self.active = prefix
                self.cursor = 0
            p = self.active
            action = 'AB'[self.cursor]
            old_here, new_here = p.old_states[-1], p.new_states[-1]
            if ((isinstance(self.old_snap, PinnedEdges)
                 and (old_here, action) not in self.old_snap.edges and used >= max_new_edges)
                or (isinstance(self.new_snap, PinnedEdges)
                    and (new_here, action) not in self.new_snap.edges and used >= max_new_edges)):
                return self._report('CONTINUING', 'Observation allowance reached; resume the pending branch.')
            try:
                before = _count(self.old)
                old_next = self.old_snap.step(old_here, action)
                used += _count(self.old) - before
                if (isinstance(self.new_snap, PinnedEdges)
                        and (new_here, action) not in self.new_snap.edges
                        and used >= max_new_edges):
                    return self._report('CONTINUING', 'One side observed; resume for the second side.')
                before = _count(self.new)
                new_next = self.new_snap.step(new_here, action)
                used += _count(self.new) - before
                if not (_owner_consistent(self.old, old_here, action, old_next) and
                        _owner_consistent(self.new, new_here, action, new_next)):
                    raise ObservationWall('edge contradicts its bound local owner')
                old_seen = next((i for i, s in enumerate(p.old_states) if s == old_next), None)
                new_seen = next((i for i, s in enumerate(p.new_states) if s == new_next), None)
                if ((old_seen is not None and p.new_states[old_seen] != new_next) or
                    (new_seen is not None and p.old_states[new_seen] != old_next)):
                    self._reject(p, action, old_next, new_next,
                                 old_seen if old_seen is not None and p.new_states[old_seen] != new_next else None,
                                 new_seen if new_seen is not None and p.old_states[new_seen] != old_next else None)
                else:
                    child = _Prefix(p.word + action, p.old_states + (old_next,),
                                    p.new_states + (new_next,))
                    self.prefixes.append(child)
                    self.frontier.append(child)
                    if old_next == self.target:
                        self.goals.append(self._candidate(child))
                self.explored += 1
                self.cursor += 1
                if self.cursor == 2:
                    self.active = None
                    self.cursor = 0
            except EdgeBudgetReached:
                return self._report('UNKNOWN_BUDGET', 'Pinned observer edge budget exhausted.')
            except (ObservationWall, ValueError) as exc:
                return self._report('WALL_OBSERVATION', f'Observation rejected: {exc}')
        self.finished = True
        return self._finish()

    def _finish(self) -> BranchReport:
        if not self.goals:
            return self._report('GOAL_OUTSIDE_SEARCH_BOUND',
                f'No consistent rooted path of at most {self.max_depth} A/B steps reached goal; '
                'not a whole-system unreachability result.')
        images = {p.target_image for p in self.goals}
        unique = (' Distinct admitted path restrictions lead to different images; '
                  'selection is not a unique correspondence.' if len(images) > 1 else '')
        return self._report('GOAL_CARRIED_WITNESSED' if self._owned() else 'GOAL_CARRIED_REMOTE_REPORTED',
            f'Goal selected among {len(self.goals)} independently replayed path restrictions '
            f'within depth {self.max_depth}; every excluded attempted branch has a '
            'word-equality obstruction. No maximality or full-state claim.' + unique)
