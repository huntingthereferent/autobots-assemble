"""Explicit finite task intake, without inferred mathematical preservation constraints.

A/B remain relational language outside this deliberately scoped 27-state model.
The task contract represents what the caller explicitly declared; the finite
solver later determines what can actually be witnessed on pinned observations.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio, PortfolioReport
from ab_chatbot_evidence_prefilter import RequiredEdgePortfolio

ActionEdge = tuple[State, Literal['A', 'B']]

# A grammar rather than an intent classifier. Everything outside this syntax
# is UNKNOWN: no words such as "keep" or "preserve" are guessed into edges.
_STATE = r'\(\s*[012]\s*,\s*[012]\s*,\s*[012]\s*\)'
_GOAL_RE = re.compile(rf'{_STATE}(?:\s*,\s*{_STATE})*', re.IGNORECASE)
_TASK_RE = re.compile(
    rf'goals\s*:\s*(?P<goals>{_STATE}(?:\s*,\s*{_STATE})*)'
    rf'(?:\s*;\s*require\s*:\s*edge\s+(?P<source>{_STATE})\s+(?P<action>[AB]))?\s*',
    re.IGNORECASE,
)
_STATE_FIND = re.compile(_STATE, re.IGNORECASE)


@dataclass(frozen=True)
class TaskContract:
    goals: tuple[State, ...]
    required_edge: ActionEdge | None
    declared_by: Literal['EXPLICIT_GRAMMAR', 'EXPLICIT_SCHEMA']
    original_input: str
    fingerprint: str


@dataclass(frozen=True)
class TaskIntake:
    status: Literal['TASK_ACCEPTED', 'UNKNOWN_TASK', 'INVALID_TASK', 'UNSUPPORTED_TASK']
    contract: TaskContract | None
    explanation: str


@dataclass(frozen=True)
class TaskOutcome:
    status: str
    contract: TaskContract | None
    report: PortfolioReport | None
    detail: str


def _parse_state(value: Any) -> State | None:
    if (type(value) not in (tuple, list) or len(value) != 3 or
            any(type(x) is not int or x not in (0, 1, 2) for x in value)):
        return None
    return tuple(value)


def _state_from_grammar(text: str) -> State:
    # Only called for strings proven to match the exact finite-state grammar.
    vals = tuple(int(x) for x in re.findall(r'[012]', text))
    assert len(vals) == 3
    return vals


def _build(goals: tuple[State, ...], required: ActionEdge | None,
           declared_by: Literal['EXPLICIT_GRAMMAR', 'EXPLICIT_SCHEMA'],
           raw: str) -> TaskIntake:
    if not goals or len(goals) > 8 or len(set(goals)) != len(goals):
        return TaskIntake('INVALID_TASK', None, 'Supply 1..8 distinct finite goals.')
    if any(g not in DOMAIN_SET for g in goals):
        return TaskIntake('INVALID_TASK', None, 'A goal is outside the declared finite domain.')
    normalized = {'goals': [list(g) for g in goals],
                  'required_edge': None if required is None else
                      {'state': list(required[0]), 'action': required[1]}}
    canonical = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return TaskIntake('TASK_ACCEPTED', TaskContract(goals, required, declared_by, raw, digest),
                      'Explicit task admitted. Mathematical evidence has not been evaluated.')


def read_task(data: Any) -> TaskIntake:
    """Read *only* explicit finite goals and optional explicit required edge.

    Structured input schema:
      {'goals': [[0,1,1], [0,2,0]],
       'required_edge': {'state':[0,0,0], 'action':'B'}}

    Supported exact text grammar:
      goals: (0,1,1), (0,2,0); require: edge (0,0,0) B

    Absent required_edge means NO preservation requirement. Never fill it in.
    A plural/unknown preservation field is unsupported, not truncated.
    """
    if type(data) is str:
        match = _TASK_RE.fullmatch(data.strip())
        if match is None:
            return TaskIntake('UNKNOWN_TASK', None,
                              'Text is not the exact supported finite-task grammar; no requirement inferred.')
        goals = tuple(_state_from_grammar(m.group()) for m in _STATE_FIND.finditer(match['goals']))
        required = None if match['source'] is None else (
            _state_from_grammar(match['source']), match['action'].upper())
        return _build(goals, required, 'EXPLICIT_GRAMMAR', data)

    if type(data) is not dict:
        return TaskIntake('INVALID_TASK', None, 'Task must be a string or explicit schema object.')
    if 'required_edges' in data:
        return TaskIntake('UNSUPPORTED_TASK', None,
                          'Multiple required edges are not supported by this solver; none inferred.')
    if set(data) - {'goals', 'required_edge'}:
        return TaskIntake('UNSUPPORTED_TASK', None,
                          'Unknown task keys are not silently interpreted or ignored.')
    raw_goals = data.get('goals')
    if type(raw_goals) not in (list, tuple):
        return TaskIntake('INVALID_TASK', None, 'goals must be an explicit state array.')
    states = tuple(_parse_state(item) for item in raw_goals)
    if any(g is None for g in states):
        return TaskIntake('INVALID_TASK', None, 'Invalid finite goal state.')
    required = None
    if 'required_edge' in data:
        edge = data['required_edge']
        if type(edge) is not dict or set(edge) != {'state', 'action'}:
            return TaskIntake('INVALID_TASK', None,
                              'required_edge requires exactly state and action.')
        state = _parse_state(edge['state'])
        if state is None or type(edge['action']) is not str or edge['action'] not in ('A', 'B'):
            return TaskIntake('INVALID_TASK', None, 'Invalid required finite action edge.')
        required = (state, edge['action'])
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return _build(states, required, 'EXPLICIT_SCHEMA', raw)


class TaskContractSession:
    """Use existing portfolio unchanged, or opt in to a witnessed required edge.

    No observation occurs during task parsing. The selected agent retains its
    own pinned revisions, budget, owner checks and zero-read audit on re-entry.
    """
    def __init__(self, old, new, task_input: Any, *, max_depth=6,
                 variants_per_goal=4, candidate_limit=7, max_trials=12):
        self.intake = read_task(task_input)
        self.agent = None
        if self.intake.contract is not None:
            contract = self.intake.contract
            params = dict(max_depth=max_depth, variants_per_goal=variants_per_goal,
                          candidate_limit=candidate_limit, max_trials=max_trials)
            if contract.required_edge is None:
                self.agent = PostExtensionPortfolio(old, new, contract.goals, **params)
            else:
                self.agent = RequiredEdgePortfolio(old, new, contract.goals,
                                                   required_edge=contract.required_edge,
                                                   **params)

    def advance(self, *, max_new_edges=108) -> TaskOutcome:
        if self.agent is None:
            return TaskOutcome(self.intake.status, None, None, self.intake.explanation)
        report = self.agent.advance(max_new_edges=max_new_edges)
        return TaskOutcome(report.status, self.intake.contract, report, report.detail)
