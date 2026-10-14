"""Multiple explicitly declared finite required edges, preserving each witness.

This opt-in layer composes the existing task intake, seed portfolio, preflight
and edge extender. Mathematical A/B generators are scoped finite models only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re
from typing import Any

from ab_chatbot_task_contract import read_task, TaskContractSession, ActionEdge, _parse_state, _state_from_grammar, _STATE
from ab_chatbot_evidence_prefilter import ExclusionCertificate, inspect_required_edge
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio, PortfolioReport
from ab_chatbot_rule_change import _version
from ab_chatbot_language_bridge import ObservationWall

_EDGE = rf'{_STATE}\s+[AB]'
_GRAMMAR = re.compile(
    rf'goals\s*:\s*(?P<goals>{_STATE}(?:\s*,\s*{_STATE})*)\s*;\s*'
    rf'require\s*:\s*edges\s+(?P<edges>{_EDGE}(?:\s*,\s*{_EDGE})+)',
    re.IGNORECASE,
)
_GOAL_SCAN = re.compile(_STATE, re.IGNORECASE)
_EDGE_SCAN = re.compile(rf'(?P<state>{_STATE})\s+(?P<action>[AB])',re.IGNORECASE)


@dataclass(frozen=True)
class MultiTaskContract:
    goals: tuple
    required_edges: tuple[ActionEdge, ...]
    declared_by: str
    original_input: str
    fingerprint: str


@dataclass(frozen=True)
class MultiIntake:
    status: str
    contract: MultiTaskContract | None
    explanation: str


@dataclass(frozen=True)
class MultiTaskOutcome:
    status: str
    contract: MultiTaskContract | None
    report: PortfolioReport | None
    detail: str


def _admit(goals, edges, channel, raw):
    if not goals or len(goals)>8 or len(set(goals))!=len(goals):
        return MultiIntake('INVALID_TASK', None, 'Supply 1..8 distinct goals.')
    if not 2<=len(edges)<=8 or len(set(edges))!=len(edges):
        return MultiIntake('INVALID_TASK', None, 'Supply 2..8 distinct required edges.')
    normalized = {'goals': [list(s) for s in goals],
                  'required_edges':[{'state':list(s),'action':a} for s,a in sorted(edges)]}
    fingerprint=hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return MultiIntake('TASK_ACCEPTED',MultiTaskContract(goals,tuple(edges),channel,raw,fingerprint),
                       'Explicit requirements admitted; not yet proved by observations.')


def read_multi_task(data: Any) -> MultiIntake:
    """Strict plural edge input; existing no-edge/single-edge intake remains intact."""
    if isinstance(data,str):
        match=_GRAMMAR.fullmatch(data.strip())
        if match:
            goals=tuple(_state_from_grammar(m.group()) for m in _GOAL_SCAN.finditer(match['goals']))
            edges=tuple((_state_from_grammar(m['state']),m['action'].upper())
                        for m in _EDGE_SCAN.finditer(match['edges']))
            return _admit(goals,edges,'EXPLICIT_MULTI_GRAMMAR',data)
    if type(data) is dict and 'required_edges' in data:
        if set(data)!={'goals','required_edges'}:
            return MultiIntake('UNSUPPORTED_TASK',None,'Only goals and required_edges allowed in plural schema.')
        raw_goals=data['goals']; raw_edges=data['required_edges']
        if type(raw_goals) not in (tuple,list) or type(raw_edges) not in (tuple,list):
            return MultiIntake('INVALID_TASK',None,'Goals and required_edges must be arrays.')
        goals=tuple(_parse_state(s) for s in raw_goals)
        if any(g is None for g in goals):
            return MultiIntake('INVALID_TASK',None,'Invalid goal coordinate.')
        edges=[]
        for raw in raw_edges:
            if type(raw) is not dict or set(raw)!={'state','action'}:
                return MultiIntake('INVALID_TASK',None,'Each required edge has exactly state and action.')
            state=_parse_state(raw['state'])
            if state is None or type(raw['action']) is not str or raw['action'] not in ('A','B'):
                return MultiIntake('INVALID_TASK',None,'Invalid required finite edge.')
            edges.append((state,raw['action']))
        raw=json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False)
        return _admit(goals,tuple(edges),'EXPLICIT_MULTI_SCHEMA',raw)
    older=read_task(data)
    if older.contract is None:
        return MultiIntake(older.status,None,older.explanation)
    c=older.contract
    return MultiIntake('TASK_ACCEPTED',MultiTaskContract(c.goals,(() if c.required_edge is None else (c.required_edge,)),
                        c.declared_by,c.original_input,c.fingerprint),older.explanation)


class MultiRequiredEdgePortfolio(PostExtensionPortfolio):
    """Only seed contradictions to EACH required edge may pre-prune a candidate.

    Completion requires EVERY required edge in one verified extension. Distinct
    exclusion certificates are retained and individually replayed on re-entry.
    """
    def __init__(self, old, new, goals, *, required_edges, **kwargs):
        if (type(required_edges) is not tuple or not 2 <= len(required_edges) <= 8 or
            any(type(edge) is not tuple or len(edge)!=2 or
                type(edge[0]) is not tuple or _parse_state(edge[0]) is None or type(edge[1]) is not str or
                edge[1] not in ('A','B') for edge in required_edges) or
            len(set(required_edges)) != len(required_edges)):
            raise ValueError('2..8 distinct finite labeled edges required')
        super().__init__(old,new,goals,**kwargs)
        self.required_edges=required_edges
        self.before_filter=None
        self.exclusions: tuple[tuple[tuple[str,...], ActionEdge, ExclusionCertificate], ...]=()
        self._excluded_selections={}
        self.undecided=0
        self.missing_by_trial=()
        self._pinned=(self.discovered.old.snapshot,self.discovered.new.snapshot,
                      _version(self.discovered.old),_version(self.discovered.new))

    def _current(self):
        a,b=self.discovered.old,self.discovered.new
        return (a.snapshot is self._pinned[0] and b.snapshot is self._pinned[1] and
                _version(a)==self._pinned[2] and _version(b)==self._pinned[3])

    def _discover_selections(self):
        state=super()._discover_selections()
        if state is not None or not self.selections:
            return state
        self.before_filter=len(self.selections)
        included=[];excluded=[];unknown=0
        for selection in self.selections:
            conflicts=[]
            for edge in self.required_edges:
                probe=inspect_required_edge(self.discovered.old,self.discovered.new,selection,edge)
                if probe.verdict=='CONTRADICTED':
                    conflicts.append((selection.words,edge,probe.certificate))
                elif probe.verdict=='UNDECIDED':
                    unknown+=1
            if conflicts:
                self._excluded_selections[selection.words]=selection
                excluded.extend(conflicts)
            else:
                included.append(selection)
        self.selections=tuple(included)
        self.exclusions=tuple(excluded)
        self.undecided=unknown
        return None

    def advance(self, *, max_new_edges=108):
        if not self._current():
            return self._report('UNKNOWN_VERSION','Pinned observations changed; current requirements not witnessed.')
        try:
            for words,edge,certificate in self.exclusions:
                replay=inspect_required_edge(self.discovered.old,self.discovered.new,
                                             self._excluded_selections[words],edge)
                if replay.verdict!='CONTRADICTED' or replay.certificate!=certificate:
                    raise ObservationWall('required-edge conflict certificate changed')
        except (ObservationWall,KeyError,ValueError) as exc:
            return self._report('WALL_OBSERVATION',f'Required-edge replay failed: {exc}')
        result=super().advance(max_new_edges=max_new_edges)
        if result.status in ('SEARCHING','EVALUATING','UNKNOWN_BUDGET','UNKNOWN_VERSION',
                             'WALL_OBSERVATION','DISCOVERY_INCOMPLETE'):
            return result
        if result.status=='GOALS_OUTSIDE_SEARCH_BOUND' and not self.before_filter:
            return result
        if result.status=='GOALS_OUTSIDE_SEARCH_BOUND' and self.before_filter and not self.selections:
            return replace(result,status='REQUIREMENTS_UNPROVED',selected=None,possible_goal_images=(),
                           detail='Every bounded seed candidate contradicted at least one explicit required edge.')
        if not hasattr(self,'_extenders') or len(self.finished)!=len(self._extenders):
            return replace(result,status='REQUIREMENTS_UNPROVED',selected=None,possible_goal_images=(),
                           detail='No completed extension proved the conjunction of required edges.')
        evaluated=tuple((t.words,tuple(edge for edge in self.required_edges if edge not in ext.edges))
                        for t,ext in zip(self.finished,self._extenders))
        self.missing_by_trial=evaluated
        eligible=[t for t,miss in zip(self.finished,(row[1] for row in evaluated)) if not miss]
        if not eligible:
            return replace(result,status='REQUIREMENTS_UNPROVED',selected=None,possible_goal_images=(),
                           detail='None of the completed bounded candidates admitted every required edge.')
        best=max(eligible,key=lambda t:(len(t.carried),t.admitted_edges,t.paired_states,
                    -t.excluded_edges,tuple((-len(w),w) for w in t.words)))
        owned=all(t.status.endswith('_WITNESSED') for t in self.finished)
        status=('GOALS_CARRIED_' if len(best.carried)==len(self.goals) else 'PARTIAL_GOALS_')+(
            'WITNESSED' if owned else 'REMOTE_REPORTED')
        images=tuple((g,tuple(sorted({img for t in eligible for goal,img,_ in t.carried if goal==g})))
                     for g in self.goals)
        return replace(result,status=status,selected=best,possible_goal_images=images,
                       detail='Selected only a fully replayed extension admitting ALL explicitly declared required edges.')


class MultiTaskSession:
    def __init__(self,old,new,task_input: Any,**kwargs):
        self.intake=read_multi_task(task_input)
        self.agent=None
        if self.intake.contract is not None:
            c=self.intake.contract
            if len(c.required_edges)>1:
                self.agent=MultiRequiredEdgePortfolio(old,new,c.goals,
                                    required_edges=c.required_edges,**kwargs)
            else:
                self.agent=TaskContractSession(old,new,task_input,**kwargs).agent

    def advance(self,*,max_new_edges=108):
        if self.agent is None:
            return MultiTaskOutcome(self.intake.status,None,None,self.intake.explanation)
        report=self.agent.advance(max_new_edges=max_new_edges)
        return MultiTaskOutcome(report.status,self.intake.contract,report,report.detail)
