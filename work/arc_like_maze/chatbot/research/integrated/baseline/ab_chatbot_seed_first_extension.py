"""Join witnessed path seeds for multiple goals *before* greedy edge extension.

Retains finite source identity, replayed path/edge evidence, honest partial goals
and bounded observations. This does not search all partial correspondences.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_branch_discovery import BranchDiscoverer
from ab_chatbot_path_union import PathUnionAgent, UnionReport
from ab_chatbot_union_extension import UnionEdgeExtender, ExtensionReport
from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_rule_change import _count

SeedFirstStatus = Literal[
    'SEARCHING', 'EXTENDING', 'GOALS_CARRIED_WITNESSED',
    'GOALS_CARRIED_REMOTE_REPORTED', 'PARTIAL_GOALS_WITNESSED',
    'PARTIAL_GOALS_REMOTE_REPORTED', 'GOALS_OUTSIDE_SEARCH_BOUND',
    'UNKNOWN_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]

@dataclass(frozen=True)
class SeedFirstReport:
    status: SeedFirstStatus
    requested_goals: tuple[State, ...]
    carried_goals: tuple[tuple[State, State, str], ...]
    selected_paths: tuple[str, ...]
    path_candidates: int
    available_candidate_paths: int
    candidate_pool_truncated: bool
    path_conflicts: int
    paired_states: int
    admitted_edges: int
    excluded_edges: int
    pending_edges: int
    old_observed_edges: int
    new_observed_edges: int
    detail: str

class SeedFirstGoalExtender:
    """Shared bounded search -> compatible path union -> extension -> goal check.

    A BranchDiscoverer explores the same finite admissible word prefixes even
    though it accepts one goal for reporting. PathUnionAgent selects *all*
    requested goals from those prefixes. No goal words are provided.
    """
    def __init__(self, old, new, goals: tuple[State, ...], *, max_depth: int = 6,
                 variants_per_goal: int = 4, max_candidates: int = 12,
                 action_order: str = 'AB'):
        if (type(goals) is not tuple or not goals or
                any(g not in DOMAIN_SET for g in goals) or len(set(goals)) != len(goals)):
            raise ValueError('nonempty distinct finite goals required')
        if type(max_depth) is not int or not 0 <= max_depth <= 8:
            raise ValueError('max_depth must be integer 0..8')
        if (type(variants_per_goal) is not int or not 1 <= variants_per_goal <= 10 or
                type(max_candidates) is not int or not 1 <= max_candidates <= 16):
            raise ValueError('bounded candidate limits required')
        if action_order not in ('AB','BA'):
            raise ValueError('action order must be AB or BA')
        self.goals = goals
        self.branch = BranchDiscoverer(old, new, goals[0], max_depth=max_depth)
        self.variants_per_goal, self.max_candidates = variants_per_goal, max_candidates
        self.action_order = action_order
        self.union: PathUnionAgent | None = None
        self.extender: UnionEdgeExtender | None = None
        self.last_union: UnionReport | None = None
        self.last_extension: ExtensionReport | None = None

    def _report(self, status: SeedFirstStatus, detail: str) -> SeedFirstReport:
        e = self.last_extension
        selected = self.last_union.selected if self.last_union else None
        pairing = dict(e.state_pairs) if e is not None else {}
        words = self.extender.words if self.extender is not None else {}
        verified = status.endswith(('_WITNESSED', '_REMOTE_REPORTED'))
        carried = tuple((g, pairing[g], words[g]) for g in self.goals
                        if verified and g in pairing and g in words)
        return SeedFirstReport(
            status, self.goals, carried, selected.words if selected else (),
            self.last_union.paths_considered if self.last_union else 0,
            self.last_union.paths_available if self.last_union else 0,
            self.last_union.candidate_pool_truncated if self.last_union else False,
            len(self.last_union.conflicts) if self.last_union else 0,
            len(e.state_pairs) if e else 0,
            len(e.admitted_edges) if e else 0,
            len(e.rejected) if e else 0,
            e.pending if e else 0,
            _count(self.branch.old), _count(self.branch.new), detail)

    def advance(self, *, max_new_edges: int = 8) -> SeedFirstReport:
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be integer 0..108')
        before = _count(self.branch.old) + _count(self.branch.new)
        b = self.branch.advance(max_new_edges=max_new_edges)
        if b.status in ('UNKNOWN_VERSION', 'WALL_OBSERVATION', 'UNKNOWN_BUDGET'):
            return self._report(b.status, 'Path discovery replay/observation: ' + b.detail)
        if b.status == 'CONTINUING':
            return self._report('SEARCHING', b.detail)
        if self.union is None:
            self.union = PathUnionAgent(self.branch, self.goals,
                                        variants_per_goal=self.variants_per_goal,
                                        max_candidates=self.max_candidates)
        u = self.union.run()  # zero-read replay from pinned caches
        self.last_union = u
        if u.status in ('UNKNOWN_VERSION', 'WALL_OBSERVATION'):
            return self._report(u.status, u.detail)
        if u.status in ('DISCOVERY_INCOMPLETE',):
            return self._report('SEARCHING', u.detail)
        if u.status == 'GOALS_OUTSIDE_CANDIDATES' or u.selected is None:
            return self._report('GOALS_OUTSIDE_SEARCH_BOUND', u.detail)
        if self.extender is None:
            self.extender = UnionEdgeExtender(self.union, action_order=self.action_order)
        remaining = max(0, max_new_edges - (_count(self.branch.old) + _count(self.branch.new) - before))
        e = self.extender.advance(max_new_edges=remaining)
        self.last_extension = e
        if e.status == 'CONTINUING':
            return self._report('EXTENDING', e.detail)
        if e.status in ('UNKNOWN_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION'):
            return self._report(e.status, e.detail)
        pairing = dict(e.state_pairs)
        if any(g not in pairing or g not in self.extender.words for g, _, _ in u.selected.carried_goals):
            return self._report('WALL_OBSERVATION', 'A goal carried by the initial seed union lost its rooted witness.')
        carried = sum(g in pairing and g in self.extender.words for g in self.goals)
        owned = e.status.endswith('WITNESSED') and u.status.endswith('WITNESSED')
        return self._report(
            ('GOALS_CARRIED_' if carried == len(self.goals) else 'PARTIAL_GOALS_') +
            ('WITNESSED' if owned else 'REMOTE_REPORTED'),
            f'Carried {carried}/{len(self.goals)} goals from compatible witnessed seeds '
            'and their checked extension; excluded edges remain counterexamples. '
            'Finite, seed-pool-dependent and not globally maximal.')
