"""Explicit typed finite obligations with independent witness contracts.

A required edge, a rooted path history and a destination state image are NOT
interchangeable.  Evidence is scoped to pinned A/B finite generator systems.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any

from ab_chatbot_task_contract import _parse_state
from ab_chatbot_multi_required import MultiTaskSession, read_multi_task
from ab_chatbot_post_extension_portfolio import PostExtensionPortfolio, PortfolioReport
from ab_chatbot_evidence_prefilter import inspect_required_edge
from ab_chatbot_rule_change import _version, _cached_path
from ab_chatbot_language_bridge import ObservationWall


@dataclass(frozen=True)
class PathObligation:
    word: str
    old_destination: tuple
    new_destination: tuple


@dataclass(frozen=True)
class DestinationObligation:
    source: tuple
    image: tuple


@dataclass(frozen=True)
class MixedContract:
    goals: tuple
    required_edges: tuple
    required_paths: tuple[PathObligation, ...]
    required_destinations: tuple[DestinationObligation, ...]
    declared_by: str
    original_input: str
    fingerprint: str


@dataclass(frozen=True)
class Intake:
    status: str
    contract: MixedContract | None
    detail: str


@dataclass(frozen=True)
class ObligationResult:
    kind: str
    obligation: object
    satisfied: bool
    detail: str


@dataclass(frozen=True)
class MixedOutcome:
    status: str
    contract: MixedContract | None
    report: PortfolioReport | None
    obligations: tuple[tuple[tuple[str, ...], tuple[ObligationResult, ...]], ...]
    detail: str


def read_mixed_task(data: Any) -> Intake:
    """Exact schema only; prose is UNKNOWN_TASK rather than inferred mathematics.

    Mixed tasks must explicitly contain at least one path or destination.
    Existing edge-only task schemas are handled by MultiTaskSession unchanged.
    """
    if type(data) is str:
        legacy=read_multi_task(data)
        return Intake('NOT_MIXED',None,'Route to the unchanged text-task intake.') if legacy.contract is not None else Intake(legacy.status,None,legacy.explanation)
    if type(data) is not dict:
        return Intake('UNKNOWN_TASK', None, 'Mixed task requires an explicit structured declaration.')
    if not any(k in data for k in ('required_paths','required_destinations')):
        legacy=read_multi_task(data)
        return Intake('NOT_MIXED',None,'Route to unchanged goal/edge task intake.') if legacy.contract is not None else Intake(legacy.status,None,legacy.explanation)
    allowed = {'goals', 'required_edges', 'required_paths', 'required_destinations'}
    if set(data) - allowed or 'goals' not in data:
        return Intake('UNSUPPORTED_TASK', None, 'Unknown or missing typed task field.')
    if type(data['goals']) not in (list, tuple):
        return Intake('INVALID_TASK', None, 'goals must be a state array.')
    goals=tuple(_parse_state(s) for s in data['goals'])
    if not 1 <= len(goals) <= 8 or None in goals or len(set(goals)) != len(goals):
        return Intake('INVALID_TASK', None, 'Supply 1..8 distinct finite source goals.')
    if any(type(data.get(field, [])) not in (list, tuple) for field in ('required_edges','required_paths','required_destinations')):
        return Intake('INVALID_TASK', None, 'Typed obligation collections must be arrays.')
    edges=[]
    for item in data.get('required_edges', []):
        if type(item) is not dict or set(item) != {'state', 'action'}:
            return Intake('INVALID_TASK', None, 'required_edges entries must have state and action.')
        s=_parse_state(item['state']); a=item['action']
        if s is None or type(a) is not str or a not in ('A','B'):
            return Intake('INVALID_TASK', None, 'Invalid explicit edge.')
        edges.append((s,a))
    if not 0 <= len(edges) <= 8 or len(set(edges)) != len(edges):
        return Intake('INVALID_TASK', None, 'At most eight distinct required edges.')
    paths=[]
    for item in data.get('required_paths', []):
        if type(item) is not dict or set(item) != {'word','old_destination','new_destination'}:
            return Intake('INVALID_TASK', None, 'A path needs word, old_destination, new_destination.')
        w=item['word']; old=_parse_state(item['old_destination']); new=_parse_state(item['new_destination'])
        if type(w) is not str or not 1 <= len(w) <= 8 or any(a not in 'AB' for a in w) or old is None or new is None:
            return Intake('INVALID_TASK', None, 'Invalid finite rooted path history.')
        paths.append(PathObligation(w,old,new))
    if len(paths) > 8 or len({p.word for p in paths}) != len(paths):
        return Intake('INVALID_TASK', None, 'At most eight distinct rooted path words.')
    dest=[]
    for item in data.get('required_destinations', []):
        if type(item) is not dict or set(item) != {'source','image'}:
            return Intake('INVALID_TASK', None, 'Destination needs source and image.')
        s=_parse_state(item['source']); n=_parse_state(item['image'])
        if s is None or n is None:
            return Intake('INVALID_TASK', None, 'Invalid finite destination image.')
        dest.append(DestinationObligation(s,n))
    if len(dest) > 8 or len({d.source for d in dest}) != len(dest):
        return Intake('INVALID_TASK', None, 'At most eight distinct destination sources.')
    if not paths and not dest:
        return Intake('INVALID_TASK', None, 'Mixed task needs an explicit path or destination obligation.')
    # Reject inconsistent declarations without querying the mathematical sources.
    assertions={}; reverse={}
    for d in dest:
        if d.image in reverse and reverse[d.image] != d.source:
            return Intake('INCONSISTENT_TASK', None, 'Two different sources demand one target image.')
        assertions[d.source]=d.image;reverse[d.image]=d.source
    for p in paths:
        if p.old_destination in assertions and assertions[p.old_destination] != p.new_destination:
            return Intake('INCONSISTENT_TASK', None, 'Path endpoint and destination requirement disagree.')
        if p.new_destination in reverse and reverse[p.new_destination] != p.old_destination:
            return Intake('INCONSISTENT_TASK', None, 'Different source endpoints require the same destination image.')
        assertions[p.old_destination]=p.new_destination
        reverse[p.new_destination]=p.old_destination
    normalized={
        'goals': [list(g) for g in goals],
        'required_edges': [{'state': list(s), 'action':a} for s,a in sorted(edges)],
        'required_paths': [{'word':p.word, 'old_destination':list(p.old_destination),
                            'new_destination':list(p.new_destination)} for p in sorted(paths,key=lambda p:p.word)],
        'required_destinations': [{'source':list(d.source),'image':list(d.image)} for d in sorted(dest,key=lambda d:d.source)]}
    digest=hashlib.sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    raw=json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    contract=MixedContract(goals,tuple(edges),tuple(paths),tuple(dest),'EXPLICIT_MIXED_SCHEMA',raw,digest)
    return Intake('TASK_ACCEPTED',contract,'Typed task declared, no mathematical assertion yet proved.')


class MixedObligationPortfolio(PostExtensionPortfolio):
    """Optional edge prefilter followed by each obligation's native replay.

    Never substitutes an endpoint identity for a complete admitted path history.
    """
    def __init__(self,old,new,contract:MixedContract,**kwargs):
        if not isinstance(contract,MixedContract):
            raise TypeError('accepted mixed task contract required')
        super().__init__(old,new,contract.goals,**kwargs)
        self.contract=contract
        self.before_filter=None
        self.exclusions=[]
        self._excluded_selections={}
        self.obligation_results=()
        self._pinned=(self.discovered.old.snapshot,self.discovered.new.snapshot,
                      _version(self.discovered.old),_version(self.discovered.new))

    def _current(self):
        a,b=self.discovered.old,self.discovered.new
        return a.snapshot is self._pinned[0] and b.snapshot is self._pinned[1] and _version(a)==self._pinned[2] and _version(b)==self._pinned[3]

    def _discover_selections(self):
        status=super()._discover_selections()
        if status is not None or not self.selections: return status
        self.before_filter=len(self.selections)
        included=[]
        for selection in self.selections:
            conflicts=[]
            for edge in self.contract.required_edges:
                check=inspect_required_edge(self.discovered.old,self.discovered.new,selection,edge)
                if check.verdict=='CONTRADICTED': conflicts.append((selection.words,edge,check.certificate))
            if conflicts:
                self._excluded_selections[selection.words]=selection
                self.exclusions.extend(conflicts)
            else:included.append(selection)
        self.selections=tuple(included)
        return None

    def _check(self,ext):
        """Call only after the extension's zero-read audit succeeds."""
        fwd=ext.forward;edges=ext.edges;old=ext.old;new=ext.new
        results=[]
        for edge in self.contract.required_edges:
            results.append(ObligationResult('EDGE',edge,edge in edges,
                          'Admitted labeled transition' if edge in edges else 'Not admitted by this pairing'))
        for d in self.contract.required_destinations:
            success=fwd.get(d.source)==d.image and d.source in ext.words
            results.append(ObligationResult('DESTINATION',d,success,
                          'Mapped state and rooted history agree' if success else 'Destination pairing absent or different'))
        for p in self.contract.required_paths:
            s=ext.discovered.old_root;ns=ext.discovered.new_root
            ok=True
            for action in p.word:
                record=edges.get((s,action))
                if record is None or record[3]!=ns or fwd.get(s)!=ns:
                    ok=False;break
                s,ns=record[2],record[4]
            if ok:
                old_path=_cached_path(old,ext.discovered.old_root,p.word)
                new_path=_cached_path(new,ext.discovered.new_root,p.word)
                ok=(old_path.states[-1]==p.old_destination and new_path.states[-1]==p.new_destination
                    and s==p.old_destination and ns==p.new_destination and
                    all(fwd.get(x)==y for x,y in zip(old_path.states,new_path.states)))
            results.append(ObligationResult('PATH',p,ok,
                          'Every path edge and both endpoint identities replayed' if ok else
                          'Complete required rooted path is not admitted by this pairing'))
        return tuple(results)

    def advance(self,*,max_new_edges=108):
        if not self._current():
            return self._report('UNKNOWN_VERSION','Pinned observation version changed.')
        try:
            for words,edge,cert in self.exclusions:
                check=inspect_required_edge(self.discovered.old,self.discovered.new,
                                            self._excluded_selections[words],edge)
                if check.verdict!='CONTRADICTED' or check.certificate!=cert:
                    raise ObservationWall('previous exclusion certificate no longer replays')
        except (ObservationWall,KeyError,ValueError) as exc:
            return self._report('WALL_OBSERVATION',f'Mixed contract exclusion replay failed: {exc}')
        parent=super().advance(max_new_edges=max_new_edges)
        if parent.status in ('SEARCHING','EVALUATING','UNKNOWN_BUDGET','UNKNOWN_VERSION',
                             'WALL_OBSERVATION','DISCOVERY_INCOMPLETE'):
            return parent
        if not hasattr(self,'_extenders') or len(self._extenders)!=len(self.finished):
            return replace(parent,status='REQUIREMENTS_UNPROVED',selected=None,possible_goal_images=(),
                           detail='No completed candidate to prove typed requirements in the bounded search.')
        try:
            checks=tuple((trial.words,self._check(ext)) for trial,ext in zip(self.finished,self._extenders))
        except (ObservationWall,ValueError,KeyError) as exc:
            return self._report('WALL_OBSERVATION',f'Typed obligation replay failed: {exc}')
        self.obligation_results=checks
        eligible=[trial for trial, (_,result) in zip(self.finished,checks) if all(o.satisfied for o in result)]
        if not eligible:
            return replace(parent,status='REQUIREMENTS_UNPROVED',selected=None,possible_goal_images=(),
                           detail='No finished bounded candidate witnesses every typed obligation together.')
        best=max(eligible,key=lambda t:(len(t.carried),t.admitted_edges,t.paired_states,
                                  -t.excluded_edges,tuple((-len(w),w) for w in t.words)))
        local=all(t.status.endswith('_WITNESSED') for t in self.finished)
        prefix='GOALS_CARRIED_' if len(best.carried)==len(self.goals) else 'PARTIAL_GOALS_'
        images=tuple((g,tuple(sorted({image for t in eligible for goal,image,_ in t.carried if goal==g})))
                     for g in self.goals)
        return replace(parent,status=prefix+('WITNESSED' if local else 'REMOTE_REPORTED'),
                       selected=best,possible_goal_images=images,
                       detail='Selected only one replayed pairing satisfying every edge, path, and destination obligation.')


class MixedTaskSession:
    def __init__(self,old,new,task_input:Any,**kwargs):
        self.intake=read_mixed_task(task_input)
        self.agent=None
        self.legacy=None
        if self.intake.status=='NOT_MIXED':
            self.legacy=MultiTaskSession(old,new,task_input,**kwargs)
            return
        if self.intake.contract is not None:
            self.agent=MixedObligationPortfolio(old,new,self.intake.contract,**kwargs)

    def advance(self,*,max_new_edges=108):
        if self.legacy is not None:
            return self.legacy.advance(max_new_edges=max_new_edges)
        if self.agent is None:
            return MixedOutcome(self.intake.status,None,None,(),self.intake.detail)
        report=self.agent.advance(max_new_edges=max_new_edges)
        return MixedOutcome(report.status,self.intake.contract,report,
                            tuple(self.agent.obligation_results) if report.selected is not None or report.status=='REQUIREMENTS_UNPROVED' else (),
                            report.detail)
