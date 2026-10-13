"""On-demand task completion against ONE declared, independently pinned route.

The selected TwoHopTransport is replayed twice (including owner/source audit),
while its neighbor is not replayed. A previously audited two-route comparison is
historical context, not a prerequisite for a task needing only one route.
A task is never completed using cached route evidence or unobserved edges.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from ab_chatbot_route_selective_refresh import RouteSelectiveRefresh
from ab_chatbot_joint_evidence_task import (JointEvidenceTask, ObligationResult, ROOT)
from ab_chatbot_selective_propagation import _freeze
from ab_chatbot_source_change_propagation import _evidence_digest
from ab_chatbot_rule_change import _version

_PROVED='TWO_HOP_CHAIN_WITNESSED'


def _valid_digest(s):
    return type(s) is str and len(s)==64 and all(x in '0123456789abcdef' for x in s)


def _route_structure(chain):
    """Only selected-route declarations, identity and bindings, never neighbor."""
    first=chain.first
    scopes=(first.donor,first.recipient,chain.final)
    return (id(chain),chain.status,_freeze(chain.expected),
        id(first),first.status,_freeze(first.expected),_freeze(first.edge),
        _freeze(first.old_map),_freeze(first.new_map),
        _freeze(chain.old_map),_freeze(chain.new_map),
        tuple((id(p),id(p.old),id(p.new),id(p.registry),
               id(p.old.snapshot),id(p.new.snapshot),_freeze(p._base._tokens))
              for p in scopes))


def _route_evidence(chain):
    """Cheap local change detection, not a substitute for pinned replay."""
    scopes=(chain.first.donor,chain.first.recipient,chain.final)
    return tuple(((_version(p.old),_version(p.new)),
        tuple((owner.version,owner.digest) if (owner:=b.owner.select()) is not None
              else None for b in (p.old,p.new)),
        tuple(p.registry.verify(t,b) for t,b in zip(p._base._tokens,(p.old,p.new))),
        (_evidence_digest(p.old.snapshot),_evidence_digest(p.new.snapshot)),
        (len(p.old.snapshot.edges),len(p.new.snapshot.edges))) for p in scopes)


@dataclass(frozen=True)
class BoundRouteTaskReport:
    status: str
    route: str
    expected_fingerprint: str | None
    observed_fingerprint: str | None
    task_fingerprint: str | None
    obligations: tuple[ObligationResult, ...]
    route_certificate: object
    historical_comparison: object
    observations_before: tuple
    observations_after: tuple
    detail: str


class RouteBoundTask:
    """Strict task declaration selecting exactly one already-witnessed route."""
    def __init__(self, refresh:RouteSelectiveRefresh, declaration:Any):
        self.refresh=refresh
        self.status='INVALID_TASK'
        self.route_name=''
        self.expected=None
        self.task=None
        self.task_fingerprint=None
        self._structure=None
        self._route=None
        self._comparison=None
        if type(refresh) is not RouteSelectiveRefresh or type(declaration) is not dict:
            return
        if set(declaration)-{'route','route_fingerprint','goals','required_edges',
                             'required_paths','required_destinations'}:
            return
        name=declaration.get('route')
        expected=declaration.get('route_fingerprint')
        if name not in ('left','right') or not _valid_digest(expected):
            return
        cmp=refresh.comparison
        index=0 if name=='left' else 1
        chain=getattr(cmp,name)
        if (cmp.status!='ROUTES_DECLARED' or expected!=cmp.expected[index] or
            chain.status!='CHAIN_DECLARED' or
            refresh.historical.status not in
            ('ROUTES_AGREE_ON_SELECTED_EDGE','ROUTE_COMPOSED_MAP_CONFLICT')):
            return
        task=JointEvidenceTask(chain.final,{k:v for k,v in declaration.items()
                             if k not in ('route','route_fingerprint')})
        self.status=task.status
        if task.status!='TASK_ACCEPTED':return
        self.route_name=name; self.expected=expected;self.task=task
        self._route=chain;self._comparison=cmp
        self._structure=_route_structure(chain)
        contract={'kind':'one-route-task/v1','chain':expected,'side':name,
                  'goals':task.goals,'edges':task.edges,'paths':task.paths,
                  'destinations':task.destinations}
        self.task_fingerprint=sha256(json.dumps(contract,sort_keys=True,
                                       separators=(',',':')).encode()).hexdigest()
        self.status='TASK_ACCEPTED'

    def advance(self):
        if self.status!='TASK_ACCEPTED':
            return BoundRouteTaskReport(self.status,self.route_name,self.expected,None,
                self.task_fingerprint,(),None,
                getattr(self.refresh,'historical',None),(),(),
                'Invalid or inconsistent task cannot use source observations.')
        chain=self._route
        def counts():
            return tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges))
                         for p in (chain.first.donor,chain.first.recipient,chain.final))
        before=counts()
        def report(status,certificate=None,checks=(),detail=''):
            return BoundRouteTaskReport(status,self.route_name,self.expected,
                    certificate.fingerprint if certificate is not None else None,
                    self.task_fingerprint,tuple(checks),certificate,
                    self.refresh.historical,before,counts(),detail)
        # Check the selected route's identity alone, not unrelated middle scope.
        if (self._comparison is not self.refresh.comparison or
            getattr(self._comparison,self.route_name) is not chain or
            self._comparison.expected[0 if self.route_name=='left' else 1]!=self.expected or
            _route_structure(chain)!=self._structure):
            return report('ROUTE_DECLARATION_CHANGED',detail='Selected route or pin binding replaced.')
        before_evidence=_route_evidence(chain)
        first=chain.advance()
        second=chain.advance()
        after_evidence=_route_evidence(chain)
        if _route_structure(chain)!=self._structure or before_evidence!=after_evidence:
            return report('SOURCE_MOVED_DURING_AUDIT',second,
                 detail='A selected-route source moved during the two-pass audit.')
        if first.status!=_PROVED or second.status!=_PROVED:
            return report(second.status if second.status!=_PROVED else 'ROUTE_EVIDENCE_WITHDRAWN',
                second,detail='Selected route lacks a current audited certificate.')
        if first.fingerprint!=self.expected or second.fingerprint!=self.expected or first!=second:
            return report('WITNESS_FINGERPRINT_MISMATCH',second,
                detail='Witness identity or replayed certificate differs from declared route.')
        pairs=dict(second.state_pairs)
        admitted={(s,act):(target,ns,nt)
                  for s,act,target,ns,nt in second.admitted_edges}
        task=self.task
        checks=[]
        for goal in task.goals:
            good=goal in pairs
            checks.append(ObligationResult('GOAL',(goal,),good,
                (goal,pairs[goal]) if good else (),
                'Paired in selected route.' if good else 'Goal unproved on selected route.'))
        for s,a in task.edges:
            edge=admitted.get((s,a));good=edge is not None
            checks.append(ObligationResult('EDGE',(s,a),good,
                (s,a,*edge) if good else (),
                'Selected route admits exact labeled edge.' if good else
                'Edge absent from selected route, even if another route knows it.'))
        for word,old_end,new_end in task.paths:
            s,ns=ROOT,ROOT;visited=[];valid=True
            for a in word:
                edge=admitted.get((s,a))
                if edge is None or pairs.get(s)!=ns or edge[1]!=ns:
                    valid=False;break
                visited.append((s,a,*edge))
                s,ns=edge[0],edge[2]
            good=valid and (s,ns)==(old_end,new_end)
            checks.append(ObligationResult('PATH',(word,old_end,new_end),good,
                tuple(visited) if good else (),
                'All word steps replayed in selected route.' if good else
                'Full rooted path not admitted by selected route.'))
        for s,ns in task.destinations:
            good=pairs.get(s)==ns
            checks.append(ObligationResult('DESTINATION',(s,ns),good,
                (s,ns) if good else (),
                'Exact image admitted by selected route.' if good else
                'Required image unproved on selected route.'))
        # No other route was replayed, and no owner transition was introduced.
        return report('TASK_COMPLETED_ON_SELECTED_ROUTE' if all(x.admitted for x in checks)
            else 'ROUTE_TASK_REQUIREMENTS_UNPROVED',second,checks,
            'Only selected route is current proof; full comparison remains historical.')
