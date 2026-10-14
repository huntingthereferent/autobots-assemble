"""CP-28: share one freshly audited owner-bound route across independent tasks.

An audit is reused only inside one synchronous invocation, and only for the
identical in-process selected route and exact pinned fingerprint. Task obligations
are evaluated independently. No cached result becomes proof on its own.
"""
from __future__ import annotations
from dataclasses import dataclass
from ab_chatbot_multi_task_dependency import (MultiRouteTaskDependencies,
    TaskDependencyEntry, TaskDependencyReport)
from ab_chatbot_route_bound_task import (BoundRouteTaskReport, _route_evidence,
    _route_structure, _PROVED)
from ab_chatbot_joint_evidence_task import ObligationResult, ROOT


@dataclass(frozen=True)
class RouteAudit:
    status: str
    certificate: object
    before: tuple
    after: tuple


def audit_route(t):
    """Two-pass selected-route audit; no task obligations are evaluated here."""
    chain=t._route
    scopes=(chain.first.donor,chain.first.recipient,chain.final)
    counts=lambda: tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in scopes)
    before=counts()
    if (t._comparison is not t.refresh.comparison or
        getattr(t._comparison,t.route_name,None) is not chain or
        t._comparison.expected[0 if t.route_name=='left' else 1]!=t.expected or
        _route_structure(chain)!=t._structure):
        return RouteAudit('ROUTE_DECLARATION_CHANGED',None,before,counts())
    evidence_before=_route_evidence(chain)
    first=chain.advance()
    second=chain.advance()
    evidence_after=_route_evidence(chain)
    if evidence_before!=evidence_after or _route_structure(chain)!=t._structure:
        return RouteAudit('SOURCE_MOVED_DURING_AUDIT',None,before,counts())
    if first.status!=_PROVED or second.status!=_PROVED:
        return RouteAudit(second.status if second.status!=_PROVED else
                          'ROUTE_EVIDENCE_WITHDRAWN',None,before,counts())
    if first.fingerprint!=t.expected or second.fingerprint!=t.expected or first!=second:
        return RouteAudit('WITNESS_FINGERPRINT_MISMATCH',None,before,counts())
    return RouteAudit('TWO_HOP_CHAIN_WITNESSED',second,before,counts())


def consume(t,audit):
    """Check one bound task against its own obligations; never union tasks."""
    cert=audit.certificate
    def report(status,checks=()):
        return BoundRouteTaskReport(status,t.route_name,t.expected,
            getattr(cert,'fingerprint',None),t.task_fingerprint,tuple(checks),
            cert,t.refresh.historical,audit.before,audit.after,
            'CP-28 shared fresh route audit; task obligations checked independently.')
    if audit.status!='TWO_HOP_CHAIN_WITNESSED':
        return report(audit.status)
    # The route/audit provenance must still agree for this exact task.
    if (t.status!='TASK_ACCEPTED' or t._route is None or
        t._comparison is not t.refresh.comparison or
        getattr(t._comparison,t.route_name,None) is not t._route or
        t.expected!=cert.fingerprint or _route_structure(t._route)!=t._structure):
        return report('ROUTE_DECLARATION_CHANGED')
    pairs=dict(cert.state_pairs)
    admitted={(s,a):(target,ns,nt) for s,a,target,ns,nt in cert.admitted_edges}
    q=t.task
    checks=[]
    for goal in q.goals:
        good=goal in pairs
        checks.append(ObligationResult('GOAL',(goal,),good,
            (goal,pairs[goal]) if good else (), 'Paired in selected route.' if good
            else 'Goal unproved on selected route.'))
    for s,a in q.edges:
        edge=admitted.get((s,a));good=edge is not None
        checks.append(ObligationResult('EDGE',(s,a),good,
            (s,a,*edge) if good else (), 'Selected route admits exact labeled edge.' if good
            else 'Edge absent from selected route, even if another route knows it.'))
    for word,old_end,new_end in q.paths:
        s=ns=ROOT;visited=[];valid=True
        for a in word:
            edge=admitted.get((s,a))
            if edge is None or pairs.get(s)!=ns or edge[1]!=ns:
                valid=False;break
            visited.append((s,a,*edge));s,ns=edge[0],edge[2]
        good=valid and (s,ns)==(old_end,new_end)
        checks.append(ObligationResult('PATH',(word,old_end,new_end),good,
            tuple(visited) if good else (), 'All word steps replayed in selected route.' if good
            else 'Full rooted path not admitted by selected route.'))
    for s,ns in q.destinations:
        good=pairs.get(s)==ns
        checks.append(ObligationResult('DESTINATION',(s,ns),good,
            (s,ns) if good else (), 'Exact image admitted by selected route.' if good
            else 'Required image unproved on selected route.'))
    return report('TASK_COMPLETED_ON_SELECTED_ROUTE' if all(x.admitted for x in checks)
                  else 'ROUTE_TASK_REQUIREMENTS_UNPROVED',checks)


class SharedRouteTaskPortfolio(MultiRouteTaskDependencies):
    """CP-27 dependency selection; CP-28 per-invocation route audit coalescing."""
    def advance(self, *, changed_sources=(), force_tasks=()):
        self._validate_selection(changed_sources,self._source_pairs,'changed_sources')
        self._validate_selection(force_tasks,self.named,'force_tasks')
        before=self._capture();observations_before=self._counts()
        changed=set(changed_sources)|{sid for sid in self._source_pairs
            if self._stamps[sid]!=before[sid]}
        structure={n:self._task_structure(t) for n,t in self.named.items()}
        drift={n for n in self.named if structure[n]!=self._structure[n]}
        targets={n for n,deps in self._depend.items() if changed.intersection(deps)}
        targets.update(force_tasks);targets.update(drift);targets.update(self._dirty)
        audits={};entries=[];audited=[];cached=[]
        for name,t in self.named.items():
            if name not in targets:
                cached.append(name);prior=self._last[name]
                entries.append(TaskDependencyEntry(name,'CACHED_NOT_REPLAYED',
                    prior.status,False,self._depend[name],prior,'Historical only.'))
                continue
            audited.append(name)
            if name in drift:
                result=self._declaration_changed(t)
            else:
                # Route identity + expected fingerprint are both required. A
                # different chain object never consumes this route's audit.
                key=(id(t._route),t.expected)
                if key not in audits:
                    try:audits[key]=audit_route(t)
                    except (ValueError,TypeError,AttributeError,KeyError,IndexError):
                        audits[key]=RouteAudit('TASK_AUDIT_EXCEPTION',None,(),())
                try:result=consume(t,audits[key])
                except (ValueError,TypeError,AttributeError,KeyError,IndexError):
                    result=BoundRouteTaskReport('TASK_AUDIT_EXCEPTION',t.route_name,
                        t.expected,None,t.task_fingerprint,(),None,
                        t.refresh.historical,(),(),
                        'Malformed task or evidence failed closed.')
            self._last[name]=result
            entries.append(TaskDependencyEntry(name,'REPLAYED',result.status,
                name not in drift and result.status!='SOURCE_MOVED_DURING_AUDIT',
                self._depend[name],result,'Shared route certificate; independent task check.'))
        after=self._capture()
        late={sid for sid in self._source_pairs if before[sid]!=after[sid]}
        late_drift={n for n,t in self.named.items() if self._task_structure(t)!=structure[n]}
        affected={n for n,deps in self._depend.items() if late.intersection(deps)}|late_drift
        # A route might move within its two-pass audit and settle back to a
        # stable end stamp; all tasks sharing that failed audit still need replay.
        moved_sources={sid for e in entries if e.mode=='REPLAYED'
                       and e.status=='SOURCE_MOVED_DURING_AUDIT'
                       for sid in e.source_ids}
        affected.update(n for n,deps in self._depend.items()
                        if moved_sources.intersection(deps))
        self._dirty=affected
        if affected:
            entries=[TaskDependencyEntry(e.name,e.mode,
                'SOURCE_MOVED_DURING_AUDIT' if e.name in affected and e.mode=='REPLAYED'
                    else e.status,False if e.name in affected else e.fresh,
                e.source_ids,e.result,'Source moved; proof withheld.'
                    if e.name in affected else e.reason) for e in entries]
        self._stamps=after
        if affected:status='SOURCE_MOVED_DURING_AUDIT'
        elif any(e.mode=='REPLAYED' and e.status!='TASK_COMPLETED_ON_SELECTED_ROUTE'
                 for e in entries):status='TASKS_WITHDRAWN_OR_UNPROVED'
        elif audited:status='TASKS_SELECTIVELY_REAUDITED'
        else:status='TASKS_CACHED_NOT_REPLAYED'
        record=TaskDependencyReport(status,
            tuple(s for s in self._source_pairs if s in changed),tuple(audited),
            tuple(cached),tuple(entries),observations_before,self._counts(),len(self.history))
        self.history.append(record)
        self.last_route_audits=len(audits)
        return record
