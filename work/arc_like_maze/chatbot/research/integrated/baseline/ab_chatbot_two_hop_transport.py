"""Two selected-edge commuting squares across THREE independently pinned join scopes.

Link 1 is the existing CrossScopeIntertwiningTransfer. Link 2 transports
*only that certified intermediate edge* to the final owner pair, requiring
its OWN independently observed old and new transitions. Does not presume
whole-source equivalence, transfer any other edge, or copy observations.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any
from ab_chatbot_cross_pin_join import CrossPinJoin
from ab_chatbot_cross_scope_transport import CrossScopeIntertwiningTransfer, READY
from ab_chatbot_joint_witness_binding import canonical_digest
from ab_chatbot_language_bridge import EdgeBudgetReached, ObservationWall

ROOT=(0,0,0)

@dataclass(frozen=True)
class TwoHopReport:
    status: str
    fingerprint: str | None
    base_fingerprints: tuple
    links: tuple
    state_pairs: tuple
    admitted_edges: tuple
    obstruction: tuple | None
    observed_by_scope: tuple
    detail: str


def _state(v):
    return type(v) is list and len(v)==3 and all(type(x) is int and x in (0,1,2) for x in v)


def _endpoint_map(entries):
    if type(entries) is not list or len(entries)!=2:return None
    mapping={};inverse={}
    for row in entries:
        if type(row) is not dict or set(row)!={'donor','recipient'} or not _state(row['donor']) or not _state(row['recipient']):return None
        k,v=tuple(row['donor']),tuple(row['recipient'])
        if k in mapping or v in inverse:return None
        mapping[k]=v;inverse[v]=k
    return mapping


class TwoHopTransport:
    def __init__(self,first:CrossScopeIntertwiningTransfer,final:CrossPinJoin,declaration:Any):
        self.first,self.final=first,final
        self.status='INVALID_CHAIN'
        self.expected=None
        self.old_map=self.new_map=None
        if (not isinstance(first,CrossScopeIntertwiningTransfer) or
            not isinstance(final,CrossPinJoin) or type(declaration) is not dict or
            set(declaration)!={'first_link_fingerprint','final_join_fingerprint',
                               'old_state_transport','new_state_transport'}):return
        left,right=declaration['first_link_fingerprint'],declaration['final_join_fingerprint']
        fo,gn=_endpoint_map(declaration['old_state_transport']),_endpoint_map(declaration['new_state_transport'])
        if not (type(left) is str and type(right) is str and len(left)==len(right)==64 and
                all(c in '0123456789abcdef' for c in left+right) and fo is not None and gn is not None):return
        # A chain MUST link three distinct pairs, not covertly re-use a scope.
        d,m,f=first.donor,first.recipient,final
        if len({id(x) for x in (d,m,f)})!=3 or len({id(x) for p in (d,m,f) for x in (p.old,p.new)})!=6:
            return
        if len({id(x.registry) for x in (d,m,f)})!=3:return
        self.expected=left,right
        self.old_map,self.new_map=fo,gn
        self.status='CHAIN_DECLARED'

    def advance(self):
        def counts():
            return tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges))
                         for p in (self.first.donor,self.first.recipient,self.final))
        def result(status,link1=(),link2=(),pairs=(),edges=(),ob=None,digest=None,detail=''):
            return TwoHopReport(status,digest,self.expected or (),tuple(x for x in (link1,link2) if x),
                                tuple(pairs),tuple(edges),ob,counts(),detail)
        if self.status!='CHAIN_DECLARED':return result(self.status)
        first=self.first.advance()
        if first.status!='CROSS_SCOPE_INTERTWINING_WITNESSED':
            return result(first.status,detail='First link has no valid current commuting square.')
        final=self.final.advance(max_new_edges=0)
        if final.status!=READY:
            return result(final.status,detail='Final join lost its separately pinned evidence.')
        if (first.derived_fingerprint,canonical_digest(final))!=self.expected:
            return result('CHAIN_FINGERPRINT_MISMATCH')
        # Only the edge newly certified by link 1 is eligible for link 2.
        ds,a,dt,dns,dnt=first.selected_square[1]
        donor_key=(ds,a)
        edge=(ds,a,dt,dns,dnt)
        if edge not in first.admitted_edges:
            return result('CHAIN_INTERMEDIATE_EDGE_UNPROVED')
        fo,gn=self.old_map,self.new_map
        if set(fo)!={ds,dt} or set(gn)!={dns,dnt}:
            return result('CHAIN_MAPPING_INCOMPLETE')
        rs,rt,rns,rnt=fo[ds],fo[dt],gn[dns],gn[dnt]
        forward=dict(final.state_pairs)
        reverse={v:k for k,v in forward.items()}
        if forward.get(rs)!=rns:
            return result('CHAIN_PREFIX_UNPROVED',ob=(rs,rns))
        old,new=self.final.old,self.final.new
        try:
            actual_old=old.snapshot.step(rs,a)
            actual_new=new.snapshot.step(rns,a)
        except EdgeBudgetReached:
            return result('UNKNOWN_BUDGET')
        except (ObservationWall,ValueError,OSError,KeyError) as exc:
            return result('WALL_OBSERVATION',detail=str(exc))
        square=(edge,(rs,a,actual_old,rns,actual_new),(rs,rt,rns,rnt))
        try:
            verified=(old._scope(old.snapshot)=='LOCAL_OWNER_VERIFIED' and
                      new._scope(new.snapshot)=='LOCAL_OWNER_VERIFIED' and
                      old.snapshot.owner_view is not None and new.snapshot.owner_view is not None and
                      old.snapshot.owner_view.step(rs,a)==actual_old and
                      new.snapshot.owner_view.step(rns,a)==actual_new)
        except (ObservationWall,ValueError,AttributeError,KeyError):verified=False
        if not verified:
            return result('WALL_OBSERVATION',link1=first.selected_square,link2=square)
        if (actual_old,actual_new)!=(rt,rnt):
            return result('CHAIN_INTERTWINING_CONFLICT',link1=first.selected_square,link2=square,
                          ob=((rt,actual_old),(rnt,actual_new)))
        if (rt in forward and forward[rt]!=rnt) or (rnt in reverse and reverse[rnt]!=rt):
            return result('CHAIN_PAIR_CONFLICT',link1=first.selected_square,link2=square,
                          ob=(rt,rnt,forward.get(rt),reverse.get(rnt)))
        derived_edge=(rs,a,rt,rns,rnt)
        edges={(s,k):(s,k,t,ns,nt) for s,k,t,ns,nt in final.admitted_edges}
        if (rs,a) in edges and edges[(rs,a)]!=derived_edge:
            return result('CHAIN_EDGE_CONFLICT',link1=first.selected_square,link2=square)
        forward[rt]=rnt
        edges[rs,a]=derived_edge
        pairs=tuple(sorted(forward.items()))
        admitted=tuple(sorted(edges.values()))
        # All three joins and both intermediate/final independently observed
        # squares must survive the final replay. No result is published early.
        first_again=self.first.advance()
        final_again=self.final.advance(max_new_edges=0)
        if (first_again.status!='CROSS_SCOPE_INTERTWINING_WITNESSED' or
            first_again.derived_fingerprint!=self.expected[0] or
            final_again.status!=READY or canonical_digest(final_again)!=self.expected[1]):
            return result('CHAIN_EVIDENCE_WITHDRAWN')
        try:
            if (old._scope(old.snapshot)!='LOCAL_OWNER_VERIFIED' or
                new._scope(new.snapshot)!='LOCAL_OWNER_VERIFIED' or
                old.snapshot.owner_view.step(rs,a)!=old.snapshot.edges[rs,a] or
                new.snapshot.owner_view.step(rns,a)!=new.snapshot.edges[rns,a]):
                return result('WALL_OBSERVATION')
        except (ObservationWall,AttributeError,KeyError,ValueError):
            return result('WALL_OBSERVATION')
        digest=sha256(json.dumps({'kind':'finite-two-hop-transport/v1','first':self.expected[0],
            'final':self.expected[1], 'maps_old':tuple(sorted(fo.items())),
            'maps_new':tuple(sorted(gn.items())), 'links':(first.selected_square,square),
            'pairs':pairs,'edges':admitted},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        return result('TWO_HOP_CHAIN_WITNESSED',first.selected_square,square,pairs,admitted,digest=digest,
                      detail='Two independently observed recipient-side commuting squares; no off-path edges.')


class TwoHopTask:
    """Consume only a freshly audited chain fingerprint, never extend it."""
    def __init__(self,chain:TwoHopTransport,declaration:Any):
        from ab_chatbot_joint_evidence_task import JointEvidenceTask
        self.chain=chain
        self.status='INVALID_TASK';self.expected=None;self.task=None
        if (not isinstance(chain,TwoHopTransport) or type(declaration) is not dict or
            set(declaration)-{'chain_fingerprint','goals','required_edges','required_paths','required_destinations'}):return
        value=declaration.get('chain_fingerprint')
        if type(value) is not str or len(value)!=64 or any(x not in '0123456789abcdef' for x in value):return
        task=JointEvidenceTask(chain.final,{k:v for k,v in declaration.items() if k!='chain_fingerprint'})
        self.status=task.status
        if task.status=='TASK_ACCEPTED':self.expected=value;self.task=task

    def advance(self):
        r=self.chain.advance()
        if self.task is None:return self.status,r,()
        if r.status!='TWO_HOP_CHAIN_WITNESSED':return r.status,r,()
        if r.fingerprint!=self.expected:return 'WITNESS_FINGERPRINT_MISMATCH',r,()
        pairs=dict(r.state_pairs)
        edges={(s,a):(t,ns,nt) for s,a,t,ns,nt in r.admitted_edges}
        checks=[]
        for s in self.task.goals:checks.append(('GOAL',s,s in pairs))
        for s,a in self.task.edges:checks.append(('EDGE',(s,a),(s,a) in edges))
        for word,old_end,new_end in self.task.paths:
            s=ns=ROOT;valid=True
            for a in word:
                e=edges.get((s,a))
                if e is None or e[1]!=ns:valid=False;break
                s,ns=e[0],e[2]
            checks.append(('PATH',(word,old_end,new_end),valid and (s,ns)==(old_end,new_end)))
        for s,n in self.task.destinations:checks.append(('DESTINATION',(s,n),pairs.get(s)==n))
        return ('TASK_COMPLETED_ON_TWO_HOP_WITNESS' if all(x[2] for x in checks) else
                'TASK_REQUIREMENTS_UNPROVED'),r,tuple(checks)
