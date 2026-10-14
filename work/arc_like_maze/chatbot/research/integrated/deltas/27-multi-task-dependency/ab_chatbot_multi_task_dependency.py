"""Bounded, on-demand dependency propagation across independently bound route tasks.

Source IDs are object-identity scoped *within this ledger*, not claims about
remote provider identity. Owner trust comes only from RouteBoundTask.advance.
A skipped task is historical/cached, never current proof. This layer does not
poll, invent goals, merge route certificates, or observe new transitions.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ab_chatbot_route_bound_task import (RouteBoundTask, BoundRouteTaskReport,
    _route_evidence, _route_structure)
from ab_chatbot_selective_propagation import _freeze


@dataclass(frozen=True)
class TaskDependencyEntry:
    name: str
    mode: str
    status: str
    fresh: bool
    source_ids: tuple[str, ...]
    result: BoundRouteTaskReport | None
    reason: str

    @property
    def proof_for_use(self):
        return self.fresh and self.status=='TASK_COMPLETED_ON_SELECTED_ROUTE'


@dataclass(frozen=True)
class TaskDependencyReport:
    status: str
    changed_sources: tuple[str, ...]
    audited: tuple[str, ...]
    cached: tuple[str, ...]
    entries: tuple[TaskDependencyEntry, ...]
    observations_before: tuple
    observations_after: tuple
    epoch: int


class MultiRouteTaskDependencies:
    """Independent route-task portfolio; only dependent tasks are re-audited.

    Construction performs each task's full two-pass audit once to establish a
    historical baseline. advance() is invoked by a caller after surrounding
    sources move. verify_for_use(name) always replays the chosen task.
    """
    def __init__(self, named: dict[str, RouteBoundTask]):
        if (type(named) is not dict or not 2 <= len(named) <= 16 or
            any(type(n) is not str or not n.strip() or len(n)>80 or
                type(t) is not RouteBoundTask or t.status!='TASK_ACCEPTED'
                for n,t in named.items()) or
            len({id(t) for t in named.values()})!=len(named)):
            raise ValueError('2..16 unique, accepted, named route tasks required')
        self.named=dict(named)
        self._depend: dict[str, tuple[str, ...]]={}
        self._origins={}
        self._source_pairs={}
        self._source_alias={}
        self._structure={}
        ids={}
        for name,t in self.named.items():
            chain=t._route
            sources=(chain.first.donor,chain.first.recipient,chain.final)
            labels=[]
            for i,pair in enumerate(sources):
                key=id(pair)
                if key not in ids:
                    sid=f'source_{len(ids)+1:02d}'
                    ids[key]=sid
                    self._source_pairs[sid]=pair
                    self._origins[sid]=(t,i)
                    self._source_alias[sid]=[]
                sid=ids[key]
                labels.append(sid)
                self._source_alias[sid].append((name,('donor','middle','final')[i]))
            self._depend[name]=tuple(labels)
            self._structure[name]=self._task_structure(t)
        self._source_alias={k:tuple(v) for k,v in self._source_alias.items()}
        self._stamps=self._capture()
        self._last={}
        self.history: list[TaskDependencyReport]=[]
        self._dirty=set()
        # An initial result has actually been replayed, not merely imported.
        base_before=self._counts()
        for name,t in self.named.items():
            self._last[name]=self._safe_advance(t)
        after=self._capture()
        if after!=self._stamps or any(self._task_structure(t)!=self._structure[n]
                                     for n,t in self.named.items()):
            self._dirty=set(self.named)
        self._stamps=after
        records=tuple(TaskDependencyEntry(n,'REPLAYED',r.status,
                n not in self._dirty,self._depend[n],r,
                'Initial independent two-pass task audit.') for n,r in self._last.items())
        self.history.append(TaskDependencyReport('BASELINE_AUDITED',(),
            tuple(self.named),(),records,base_before,self._counts(),0))

    @staticmethod
    def _task_structure(t):
        q=t.task
        return (id(t),id(t.refresh),id(t._comparison),id(t._route),
            t.status,t.route_name,t.expected,t.task_fingerprint,id(q),
            id(getattr(t._comparison,t.route_name,None)),
            _freeze((q.goals,q.edges,q.paths,q.destinations)) if q else None,
            _route_structure(t._route))

    @staticmethod
    def _safe_advance(task):
        try:
            return task.advance()
        except (ValueError,TypeError,AttributeError,KeyError,IndexError) as exc:
            return BoundRouteTaskReport('TASK_AUDIT_EXCEPTION',task.route_name,
                task.expected,None,task.task_fingerprint,(),None,
                task.refresh.historical,(),(),
                f'Failed closed on malformed or moving evidence: {type(exc).__name__}')

    @staticmethod
    def _declaration_changed(task):
        return BoundRouteTaskReport('TASK_DECLARATION_CHANGED',task.route_name,
            task.expected,None,task.task_fingerprint,(),None,
            task.refresh.historical,(),(),
            'The selected task, route binding, or declared obligations differ from admission.')

    def _capture(self):
        # Each bound pair's current pins, owner heads, version and edge digest.
        # These are *change detectors*, not proof of the underlying sources.
        return {sid:_route_evidence(task._route)[i]
                for sid,(task,i) in self._origins.items()}

    def _counts(self):
        return tuple((sid,len(p.old.snapshot.edges),len(p.new.snapshot.edges))
                     for sid,p in self._source_pairs.items())

    def dependencies(self):
        """Return a named, finite, human-readable source/task incidence graph."""
        return tuple((sid,self._source_alias[sid]) for sid in self._source_pairs)

    def _validate_selection(self, selection, pool, name):
        if (type(selection) is not tuple or len(set(selection))!=len(selection)
                or any(type(x) is not str or x not in pool for x in selection)):
            raise ValueError(f'{name} must contain unique known names')

    def advance(self, *, changed_sources=(), force_tasks=()):
        """Re-audit only tasks depending on named or detected changed sources.

        The caller may supply an external notification via changed_sources even
        when cheap local stamps are unchanged. An unchanged task is cached and
        cannot be used as present proof without verify_for_use().
        """
        self._validate_selection(changed_sources,self._source_pairs,'changed_sources')
        self._validate_selection(force_tasks,self.named,'force_tasks')
        before=self._capture()
        observations_before=self._counts()
        changed=set(changed_sources)|{sid for sid in self._source_pairs
             if self._stamps[sid]!=before[sid]}
        current_structure={n:self._task_structure(t) for n,t in self.named.items()}
        drift={n for n in self.named
               if current_structure[n]!=self._structure[n]}
        targets={n for n,deps in self._depend.items() if changed.intersection(deps)}
        targets.update(force_tasks)
        targets.update(drift)
        targets.update(self._dirty)
        entries=[];audited=[];cached=[];results={}
        for n,t in self.named.items():
            if n in targets:
                audited.append(n)
                result=(self._declaration_changed(t) if n in drift
                        else self._safe_advance(t))
                results[n]=result
                self._last[n]=result
                entries.append(TaskDependencyEntry(n,'REPLAYED',result.status,
                    n not in drift,self._depend[n],result,
                    'Bound task re-audited against its selected route only.' if n not in drift
                    else 'Task/route declaration changed; success cannot be carried.'))
            else:
                cached.append(n)
                prior=self._last[n]
                entries.append(TaskDependencyEntry(n,'CACHED_NOT_REPLAYED',prior.status,
                    False,self._depend[n],prior,
                    'Historical only; proof-for-use requires an explicit fresh audit.'))
        after=self._capture()
        late={sid for sid in self._source_pairs if before[sid]!=after[sid]}
        late_drift={n for n,t in self.named.items()
                    if self._task_structure(t)!=current_structure[n]}
        affected_late={n for n,deps in self._depend.items()
                       if late.intersection(deps)}|late_drift
        if affected_late:
            self._dirty=affected_late
            entries=[TaskDependencyEntry(e.name,e.mode,
                     'SOURCE_MOVED_DURING_AUDIT' if e.name in affected_late and e.mode=='REPLAYED'
                       else e.status,
                     False if e.name in affected_late else e.fresh,
                     e.source_ids,e.result,
                     'A dependency moved during portfolio replay; must be re-audited.'
                     if e.name in affected_late else e.reason) for e in entries]
        else:self._dirty.clear()
        self._stamps=after
        if affected_late:status='SOURCE_MOVED_DURING_AUDIT'
        elif any(e.mode=='REPLAYED' and e.status!='TASK_COMPLETED_ON_SELECTED_ROUTE'
                 for e in entries):status='TASKS_WITHDRAWN_OR_UNPROVED'
        elif audited:status='TASKS_SELECTIVELY_REAUDITED'
        else:status='TASKS_CACHED_NOT_REPLAYED'
        report=TaskDependencyReport(status,tuple(s for s in self._source_pairs if s in changed),
            tuple(audited),tuple(cached),tuple(entries),observations_before,
            self._counts(),len(self.history))
        self.history.append(report)
        return report

    def verify_for_use(self, name: str):
        """Freshly replay just one named task; do not return a cached proof."""
        if type(name) is not str or name not in self.named:
            raise ValueError('unknown route-specific task')
        report=self.advance(force_tasks=(name,))
        return next(e for e in report.entries if e.name==name)
