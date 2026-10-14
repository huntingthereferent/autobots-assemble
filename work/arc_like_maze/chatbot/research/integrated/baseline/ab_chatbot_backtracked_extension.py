"""Bounded branch/backtrack-to-witness, followed by goal-preserving union extension.

Uses the existing BranchDiscoverer -> PathUnionAgent -> UnionEdgeExtender
contracts. This is a selected rooted partial mathematical correspondence, not
an assertion of globally maximal pairing, unrestricted agency or physical A/B.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_branch_discovery import BranchDiscoverer, BranchReport
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_union_extension import UnionEdgeExtender, ExtensionReport
from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_rule_change import _count

BacktrackStatus = Literal[
    'SEARCHING', 'EXTENDING', 'GOAL_CARRIED_WITNESSED',
    'GOAL_CARRIED_REMOTE_REPORTED', 'GOAL_OUTSIDE_SEARCH_BOUND',
    'UNKNOWN_BUDGET', 'UNKNOWN_VERSION', 'WALL_OBSERVATION',
]

@dataclass(frozen=True)
class BacktrackReport:
    status: BacktrackStatus
    goal: State
    mapped_goal: State | None
    goal_word: str | None
    selected_paths: tuple[str, ...]
    branch_alternatives: int
    branch_rejections: int
    paired_states: int
    admitted_edges: int
    excluded_edges: int
    old_observed_edges: int
    new_observed_edges: int
    depth_limit: int
    detail: str


class BacktrackedGoalExtender:
    """Branch among alternative A/B path histories before extending a union.

    A contradiction rejects one proposed prefix without discarding other
    prefixes. The bounded history is checked by the existing branch replay;
    the selected union is subsequently extended with UnionEdgeExtender.
    Calls are resumable on a fixed pinned source and shared edge budget.
    The goal word is discovered, not a constructor parameter.
    """

    def __init__(self, old, new, goal: State, *, max_depth: int = 6,
                 variants_per_goal: int = 4, max_candidates: int = 12):
        if goal not in DOMAIN_SET:
            raise ValueError('goal outside finite domain')
        if type(max_depth) is not int or not 0 <= max_depth <= 8:
            raise ValueError('max_depth must be an integer 0..8')
        self.branch = BranchDiscoverer(old, new, goal, max_depth=max_depth)
        self.goal = goal
        self.variants_per_goal = variants_per_goal
        self.max_candidates = max_candidates
        self.union: PathUnionAgent | None = None
        self.extender: UnionEdgeExtender | None = None
        self.last_branch: BranchReport | None = None
        self.last_extension: ExtensionReport | None = None
        self.selected_paths: tuple[str, ...] = ()

    def _report(self, status: BacktrackStatus, detail: str) -> BacktrackReport:
        r = self.last_extension
        pairs = dict(r.state_pairs) if r is not None else {}
        carried = self.goal in pairs and self.extender is not None and self.goal in self.extender.words
        return BacktrackReport(
            status, self.goal, pairs[self.goal] if carried else None,
            self.extender.words[self.goal] if carried else None,
            self.selected_paths,
            len(self.last_branch.alternatives) if self.last_branch else 0,
            len(self.last_branch.rejected) if self.last_branch else 0,
            len(r.state_pairs) if r else 0,
            len(r.admitted_edges) if r else 0,
            len(r.rejected) if r else 0,
            _count(self.branch.old), _count(self.branch.new),
            self.branch.max_depth, detail)

    def advance(self, *, max_new_edges: int = 8) -> BacktrackReport:
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('max_new_edges must be an integer 0..108')
        used_before = _count(self.branch.old) + _count(self.branch.new)
        # Recheck the *whole* branch history every call, including after
        # completion, so source revision and tampered caches cannot be hidden
        # behind a prior success.
        b = self.branch.advance(max_new_edges=max_new_edges)
        self.last_branch = b
        for marker in ('UNKNOWN_VERSION', 'WALL_OBSERVATION', 'UNKNOWN_BUDGET'):
            if b.status == marker:
                return self._report(marker, 'Branch evidence cannot currently be reused: '+b.detail)
        if b.status == 'CONTINUING':
            return self._report('SEARCHING', b.detail)
        if b.status == 'GOAL_OUTSIDE_SEARCH_BOUND':
            return self._report('GOAL_OUTSIDE_SEARCH_BOUND', b.detail)
        if self.extender is None:
            self.union = PathUnionAgent(self.branch, (self.goal,),
                                        variants_per_goal=self.variants_per_goal,
                                        max_candidates=self.max_candidates)
            union_report = self.union.run()
            if union_report.status in ('UNKNOWN_VERSION','WALL_OBSERVATION'):
                return self._report(union_report.status, union_report.detail)
            if union_report.selected is None:
                return self._report('WALL_OBSERVATION',
                                    'No reusable selected path union; no extension initiated.')
            self.selected_paths = union_report.selected.words
            self.extender = UnionEdgeExtender(self.union)
        remaining = max(0, max_new_edges - (_count(self.branch.old) +
                                             _count(self.branch.new) - used_before))
        e = self.extender.advance(max_new_edges=remaining)
        self.last_extension = e
        if e.status == 'CONTINUING':
            return self._report('EXTENDING',e.detail)
        if e.status in ('UNKNOWN_BUDGET','UNKNOWN_VERSION','WALL_OBSERVATION'):
            return self._report(e.status,e.detail)
        if self.goal not in dict(e.state_pairs) or self.goal not in self.extender.words:
            return self._report('WALL_OBSERVATION','Previously admitted goal lost its rooted witness.')
        owned = e.status.endswith('WITNESSED') and b.status.endswith('WITNESSED')
        return self._report('GOAL_CARRIED_WITNESSED' if owned else
                            'GOAL_CARRIED_REMOTE_REPORTED',
                            'Branch-selected rooted goal, then checked every missing edge '
                            'from its admitted extension; incompatible edges remain excluded. '
                            'This does not prove maximum correspondence or whole-system equivalence.')
