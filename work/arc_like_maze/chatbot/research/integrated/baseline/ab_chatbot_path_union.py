"""Finite, evidence-preserving amalgamation of independently discovered A/B paths.

A selection is a partial *edge-labeled* graph correspondence on the union of
explicitly witnessed paths. It is NOT closed under all outgoing A/B actions,
maximal among all path restrictions, or a physical/world correspondence.

No candidate action word or coordinate pairing is supplied by the caller:
all candidate paths come from the completed BranchDiscoverer search history.
Search over subsets of a bounded, explicitly selected candidate pool is exact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_branch_discovery import BranchDiscoverer, PathRestriction
from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_language_bridge import ObservationWall, PathWitness
from ab_chatbot_rule_change import WordRelation, _cached_path, _count

UnionStatus = Literal[
    'UNION_WITNESSED', 'UNION_REMOTE_REPORTED', 'PARTIAL_UNION_WITNESSED',
    'PARTIAL_UNION_REMOTE_REPORTED', 'GOALS_OUTSIDE_CANDIDATES',
    'DISCOVERY_INCOMPLETE', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]


@dataclass(frozen=True)
class UnionConflict:
    """An independently replayable word-equality obstruction for one pair."""
    left_candidate: str
    right_candidate: str
    cause: str
    witness: WordRelation


@dataclass(frozen=True)
class JoinedRestriction:
    words: tuple[str, ...]
    state_pairs: tuple[tuple[State, State], ...]
    # (old-source-state, action, old-target, new-source-state, new-target)
    admitted_edges: tuple[tuple[State, str, State, State, State], ...]
    # (requested original goal, mapped changed goal, transporting word)
    carried_goals: tuple[tuple[State, State, str], ...]


@dataclass(frozen=True)
class UnionReport:
    status: UnionStatus
    requested_goals: tuple[State, ...]
    selected: JoinedRestriction | None
    candidate_words: tuple[str, ...]
    conflicts: tuple[UnionConflict, ...]
    paths_considered: int
    paths_available: int
    candidate_pool_truncated: bool
    # Each option occurs in some separately compatible subset with maximal goal coverage.
    # Alternative subsets need not be compatible with the selected union.
    possible_goal_images: tuple[tuple[State, tuple[State, ...]], ...]
    compatible_subsets: int
    old_observed_edges: int
    new_observed_edges: int
    detail: str


def _candidate_from_history(prefix) -> PathRestriction:
    return PathRestriction(prefix.word, PathWitness(prefix.word, prefix.old_states),
                           PathWitness(prefix.word, prefix.new_states),
                           tuple(dict(zip(prefix.old_states, prefix.new_states)).items()))


class PathUnionAgent:
    """Select a compatible collection of discovered paths for multiple goals.

    The bounded candidate pool is derived automatically from the path search
    history: at most `variants_per_goal` shortest paths for each declared goal,
    interleaved across goals and truncated at `max_candidates`. All candidate
    subsets are compared; the strongest score covers goals, then admitted
    edges and states. Ties are deterministic; no global maximality is claimed.
    """

    def __init__(self, discovered: BranchDiscoverer, goals: tuple[State, ...], *,
                 variants_per_goal: int = 4, max_candidates: int = 14):
        if not goals or any(x not in DOMAIN_SET for x in goals) or len(set(goals)) != len(goals):
            raise ValueError('goals must be distinct states in the finite domain')
        if (type(variants_per_goal) is not int or not 1 <= variants_per_goal <= 10 or
                type(max_candidates) is not int or not 1 <= max_candidates <= 16):
            raise ValueError('invalid candidate search limits')
        self.discovered = discovered
        self.goals = tuple(goals)
        self.variants_per_goal = variants_per_goal
        self.max_candidates = max_candidates

    def _status(self, status: UnionStatus, detail: str, *, chosen=None, pool=(),
                conflicts=(), available=0, truncated=False, images=(), compatible=0) -> UnionReport:
        d = self.discovered
        return UnionReport(status, self.goals, chosen, tuple(p.word for p in pool),
                           tuple(conflicts), len(pool), available, truncated,
                           tuple(images), compatible, _count(d.old), _count(d.new), detail)

    def _select_candidates(self) -> tuple[tuple[PathRestriction, ...], int, bool]:
        per_goal = []
        for goal in self.goals:
            matching = sorted((p for p in self.discovered.prefixes
                               if p.old_states[-1] == goal),
                              key=lambda p: (len(p.word), p.word))
            per_goal.append([_candidate_from_history(p)
                             for p in matching[:self.variants_per_goal]])
        # Round-robin selection prevents one goal monopolizing the limit.
        ordered, known = [], set()
        for index in range(self.variants_per_goal):
            for options in per_goal:
                if index < len(options) and options[index].word not in known:
                    ordered.append(options[index])
                    known.add(options[index].word)
        available = len(ordered)
        return tuple(ordered[:self.max_candidates]), available, available > self.max_candidates

    def run(self) -> UnionReport:
        """Never performs new edge observations; replay and audit only."""
        d = self.discovered
        # This public zero-read call audits all admitted and rejected histories,
        # and rejects source repins. It cannot finish an unfinished discovery.
        report = d.advance(max_new_edges=0)
        if report.status == 'UNKNOWN_VERSION':
            return self._status('UNKNOWN_VERSION', 'A source was repinned; cannot reuse prior evidence.')
        if report.status == 'WALL_OBSERVATION':
            return self._status('WALL_OBSERVATION', 'The discovery history failed witnessed replay.')
        if report.status not in ('GOAL_CARRIED_WITNESSED', 'GOAL_CARRIED_REMOTE_REPORTED',
                                 'GOAL_OUTSIDE_SEARCH_BOUND'):
            return self._status('DISCOVERY_INCOMPLETE', 'Finish or explicitly resolve the discovery first.')
        try:
            pool, available, truncated = self._select_candidates()
            if not pool:
                return self._status('GOALS_OUTSIDE_CANDIDATES',
                                    'No requested goal occurs in the completed bounded path history.',
                                    available=available)
            # Replay each candidate and verify both laws; no new reads are permitted.
            for p in pool:
                if (_cached_path(d.old, d.old_root, p.word) != p.original_path or
                        _cached_path(d.new, d.new_root, p.word) != p.changed_path):
                    raise ObservationWall('candidate path replay mismatch')

            # Each observation is labeled by the action on that path, and its
            # paired endpoints must cohere under a single partial bijection.
            def join(paths):
                fwd, rev, origins = {}, {}, {}
                edges = {}
                for p in paths:
                    for idx, (old, new) in enumerate(zip(p.original_path.states,
                                                           p.changed_path.states)):
                        previous_old = fwd.get(old)
                        previous_new = rev.get(new)
                        if previous_old is not None and previous_old != new:
                            return None, (origins[('old', old)], p.word[:idx], 'SOURCE_COLLISION')
                        if previous_new is not None and previous_new != old:
                            return None, (origins[('new', new)], p.word[:idx], 'TARGET_COLLISION')
                        fwd[old], rev[new] = new, old
                        origins.setdefault(('old', old), p.word[:idx])
                        origins.setdefault(('new', new), p.word[:idx])
                    for index, action in enumerate(p.word):
                        old_s = p.original_path.states[index]
                        new_s = p.changed_path.states[index]
                        old_t = p.original_path.states[index+1]
                        new_t = p.changed_path.states[index+1]
                        key = (old_s, action)
                        current = (old_s, action, old_t, new_s, new_t)
                        if key in edges and edges[key] != current:
                            raise ObservationWall('same admitted old edge has inconsistent paired results')
                        edges[key] = current
                return (fwd, edges), None

            conflicts = []
            # Pairwise incompatibilities are recorded even if another winning
            # subset is found. They constrain this pool, not all possible maps.
            for i, p in enumerate(pool):
                for q in pool[i+1:]:
                    _, obstruction = join((p,q))
                    if obstruction is None:
                        continue
                    left, right, cause = obstruction
                    old_left = _cached_path(d.old, d.old_root, left)
                    old_right = _cached_path(d.old, d.old_root, right)
                    new_left = _cached_path(d.new, d.new_root, left)
                    new_right = _cached_path(d.new, d.new_root, right)
                    witness = WordRelation(left, right, old_left, old_right,
                                           new_left, new_right,
                                           old_left.states[-1] == old_right.states[-1],
                                           new_left.states[-1] == new_right.states[-1])
                    if witness.old_equal == witness.new_equal:
                        raise ObservationWall('candidate collision lacks separating equality witness')
                    conflicts.append(UnionConflict(p.word, q.word, cause, witness))

            best, best_score = None, None
            best_coverage = -1
            goal_image_sets = {goal: set() for goal in self.goals}
            compatible = 0
            # Exact on the bounded, finite candidate pool. Each candidate is a
            # witnessed full path; we never assume arbitrary off-path closure.
            for bits in range(1, 1 << len(pool)):
                paths = [p for j, p in enumerate(pool) if bits & (1 << j)]
                union, _ = join(paths)
                if union is None:
                    continue
                compatible += 1
                mapping, edges = union
                carried = tuple((goal, mapping[goal],
                                 min((p.word for p in paths if p.source_target == goal),
                                     key=lambda w: (len(w), w)))
                                for goal in self.goals if any(p.source_target == goal for p in paths))
                if len(carried) > best_coverage:
                    best_coverage = len(carried)
                    goal_image_sets = {goal: set() for goal in self.goals}
                if len(carried) == best_coverage:
                    for goal, image, _ in carried:
                        goal_image_sets[goal].add(image)
                score = (len(carried), len(edges), len(mapping), -len(paths))
                words = tuple(sorted((p.word for p in paths), key=lambda w: (len(w), w)))
                if best_score is None or score > best_score or (score == best_score and words < best.words):
                    best_score = score
                    best = JoinedRestriction(words,
                        tuple(sorted(mapping.items())),
                        tuple(sorted(edges.values())), carried)

            all_goals = len(best.carried_goals) == len(self.goals)
            is_owned = (d.old.origin_scope == 'LOCAL_OWNER_VERIFIED' and
                        d.new.origin_scope == 'LOCAL_OWNER_VERIFIED')
            status = (('UNION_' if all_goals else 'PARTIAL_UNION_') +
                      ('WITNESSED' if is_owned else 'REMOTE_REPORTED'))
            return self._status(status,
                f'Admitted {len(best.words)} jointly consistent paths; '
                f'carried {len(best.carried_goals)}/{len(self.goals)} requested goals. '
                f'Exact subset comparison over {len(pool)} chosen candidate paths only; '
                'unobserved edges are not claimed, and global maximality is not established.',
                chosen=best, pool=pool, conflicts=conflicts,
                available=available, truncated=truncated, compatible=compatible,
                images=tuple((goal, tuple(sorted(goal_image_sets[goal])))
                             for goal in self.goals))
        except (ObservationWall, ValueError, KeyError) as exc:
            return self._status('WALL_OBSERVATION', f'Path-union replay failed: {exc}')
