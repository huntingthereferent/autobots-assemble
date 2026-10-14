"""Goal-sensitive choice between *two witnessed partial* A/B correspondences.

No claim of maximality or complete search over all partial correspondences:
BFS/AB and DFS/BA are just two deterministic constructive strategies.
Their edge observations are shared, but their admitted mappings are separate.
A goal is selected only after both candidates finish and replay their evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_language_bridge import LanguageBridge, PathWitness
from ab_chatbot_restricted_rule_transport import (
    RestrictedRuleTransport, RestrictionReport, RestrictedGoalReport,
)
from ab_chatbot_rule_change import _count, _version

ChoiceStatus = Literal[
    'CONTINUING', 'GOAL_SELECTED_WITNESSED', 'GOAL_SELECTED_REMOTE_REPORTED',
    'GOAL_OUTSIDE_TESTED_RESTRICTIONS', 'UNKNOWN_BUDGET', 'UNKNOWN_VERSION',
    'WALL_OBSERVATION',
]


@dataclass(frozen=True)
class CandidateChoice:
    strategy: str
    restriction_status: str
    paired_states: int
    admitted_edges: int
    excluded_edges: int
    goal_status: str | None
    target_image: State | None
    action_word: str | None


@dataclass(frozen=True)
class ChoiceReport:
    status: ChoiceStatus
    source_target: State
    selected_strategy: str | None
    target_image: State | None
    original_path: PathWitness | None
    changed_path: PathWitness | None
    candidates: tuple[CandidateChoice, ...]
    old_observed_edges: int
    new_observed_edges: int
    detail: str


class GoalSelectedRestrictions:
    """Compare two admitted rooted graphs for a specified goal.

    Selection is deterministic by shortest admitted action word, then word,
    then strategy. This is a ranking of *tested candidates only*, not an
    optimality certificate over all paths, partial maps, or physical systems.
    """

    def __init__(self, old: LanguageBridge, new: LanguageBridge,
                 source_target: State, *,
                 old_root: State = (0, 0, 0), new_root: State = (0, 0, 0)):
        if source_target not in DOMAIN_SET:
            raise ValueError('goal outside the declared 27-state domain')
        self.old, self.new = old, new
        self.target = source_target
        self.old_version, self.new_version = _version(old), _version(new)
        self.strategies = (
            ('BFS_AB', RestrictedRuleTransport(old, new, old_root=old_root,
                 new_root=new_root, frontier_mode='BFS', action_order='AB')),
            ('DFS_BA', RestrictedRuleTransport(old, new, old_root=old_root,
                 new_root=new_root, frontier_mode='DFS', action_order='BA')),
        )
        self._last: dict[str, RestrictionReport] = {}
        self._next = 0

    def _report(self, status: ChoiceStatus, detail: str,
                winning: tuple[str, RestrictedGoalReport] | None = None,
                goals: dict[str, RestrictedGoalReport] | None = None) -> ChoiceReport:
        candidates = []
        goals = goals or {}
        for name, agent in self.strategies:
            r = self._last.get(name)
            goal = goals.get(name)
            candidates.append(CandidateChoice(
                name, r.status if r else 'CONTINUING',
                len(agent.forward), len(agent.admitted), len(agent.excluded),
                goal.status if goal else None,
                goal.target_image if goal else None,
                goal.original_path.word if goal and goal.original_path else None,
            ))
        choice = winning[1] if winning else None
        return ChoiceReport(
            status, self.target, winning[0] if winning else None,
            choice.target_image if choice else None,
            choice.original_path if choice else None,
            choice.changed_path if choice else None,
            tuple(candidates), _count(self.old), _count(self.new), detail,
        )

    def advance(self, *, max_new_edges: int = 4) -> ChoiceReport:
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be 0..108')
        if (_version(self.old) != self.old_version or
                _version(self.new) != self.new_version):
            return self._report('UNKNOWN_VERSION', 'Pinned version changed; no selection.')
        remaining = max_new_edges
        # Alternate observations fairly between strategies. Cached observations
        # can be reused without charging a second query.
        while True:
            statuses = []
            for step in range(len(self.strategies)):
                index = (self._next + step) % len(self.strategies)
                name, agent = self.strategies[index]
                before = _count(self.old) + _count(self.new)
                r = agent.advance(max_new_edges=1 if remaining else 0)
                delta = _count(self.old) + _count(self.new) - before
                if delta > remaining or delta < 0:
                    return self._report('WALL_OBSERVATION', 'Shared observation budget accounting failed.')
                remaining -= delta
                self._last[name] = r
                statuses.append(r.status)
            self._next = (self._next + 1) % len(self.strategies)
            if 'UNKNOWN_VERSION' in statuses:
                return self._report('UNKNOWN_VERSION', 'Pinned version mismatch in a candidate.')
            if 'WALL_OBSERVATION' in statuses:
                return self._report('WALL_OBSERVATION', 'Candidate witness failed replay or owner check.')
            if 'UNKNOWN_BUDGET' in statuses:
                return self._report('UNKNOWN_BUDGET', 'Observer budget exhausted; no selection.')
            if all(s in (
                'RESTRICTED_SUBGRAPH_WITNESSED', 'RESTRICTED_SUBGRAPH_REMOTE_REPORTED',
                'ROOTED_PRESERVED_WITNESSED', 'ROOTED_PRESERVED_REMOTE_REPORTED',
            ) for s in statuses):
                goals: dict[str, RestrictedGoalReport] = {}
                successful: list[tuple[str, RestrictedGoalReport]] = []
                for name, agent in self.strategies:
                    carry = agent.carry_target(self.target)
                    goals[name] = carry
                    if carry.status == 'WALL_OBSERVATION':
                        return self._report('WALL_OBSERVATION',
                                            'Candidate goal witness rejected.', goals=goals)
                    if carry.status == 'UNKNOWN_VERSION':
                        return self._report('UNKNOWN_VERSION',
                                            'Candidate was repinned.', goals=goals)
                    if carry.status.startswith('GOAL_CARRIED_'):
                        successful.append((name, carry))
                if not successful:
                    return self._report('GOAL_OUTSIDE_TESTED_RESTRICTIONS',
                        'Neither tested restriction admits this goal; not global unreachability.',
                        goals=goals)
                chosen = min(successful, key=lambda p: (
                    len(p[1].original_path.word), p[1].original_path.word, p[0]))
                status: ChoiceStatus = (
                    'GOAL_SELECTED_WITNESSED' if chosen[1].status == 'GOAL_CARRIED_WITNESSED'
                    else 'GOAL_SELECTED_REMOTE_REPORTED')
                images = {carry.target_image for _, carry in successful}
                ambiguity = (' Different valid candidate images survive; selection does not '
                             'establish a unique correspondence.' if len(images) > 1 else '')
                return self._report(status,
                    'Shortest admitted route among two explicitly tested partial restrictions; '
                    'not a maximal or universal correspondence.' + ambiguity,
                    chosen, goals)
            if remaining == 0:
                return self._report('CONTINUING', 'Shared per-call observation budget reached; resume.')
