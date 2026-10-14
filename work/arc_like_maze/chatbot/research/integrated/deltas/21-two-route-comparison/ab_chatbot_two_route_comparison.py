"""Compare TWO independently witnessed two-hop routes, without joining them.

Both routes share the exact source and final owner-pinned joins, but have
separate intermediate owner scopes. They may each have legitimate selected
commuting squares while their COMPOSED endpoint maps disagree. Such a conflict
is evidence about the proposed route-independent mapping, not a failure of the
separately witnessed mathematical edges.
"""
from dataclasses import dataclass
from typing import Any
from ab_chatbot_two_hop_transport import TwoHopTransport, TwoHopReport


@dataclass(frozen=True)
class RouteComparison:
    status: str
    left: TwoHopReport | None
    right: TwoHopReport | None
    donor_edge: tuple
    left_composed: tuple
    right_composed: tuple
    disagreement: tuple
    observations_before: tuple
    observations_after: tuple
    detail: str


def _digest(v):
    return type(v) is str and len(v)==64 and all(x in '0123456789abcdef' for x in v)


class TwoRouteComparison:
    """Only detects agreement/conflict for ONE named donor edge; no transfer."""
    def __init__(self,left:TwoHopTransport,right:TwoHopTransport,declaration:Any):
        self.left,self.right=left,right
        self.status='INVALID_ROUTE_COMPARISON';self.expected=();self._scope_objects=()
        if (not isinstance(left,TwoHopTransport) or not isinstance(right,TwoHopTransport)
            or left is right or type(declaration) is not dict or
            set(declaration)!={'left_chain_fingerprint','right_chain_fingerprint'}):
            return
        a,b=declaration['left_chain_fingerprint'],declaration['right_chain_fingerprint']
        if not (_digest(a) and _digest(b)):
            return
        # Strictly same donor and final observer/source objects, two genuinely
        # independent intermediate owner-pinned joins and registries.
        l1,r1=left.first,right.first
        if (l1.donor is not r1.donor or left.final is not right.final or
            l1.recipient is r1.recipient or
            len({id(x) for x in (l1.donor,l1.recipient,r1.recipient,left.final)})!=4 or
            len({id(x.registry) for x in (l1.donor,l1.recipient,r1.recipient,left.final)})!=4 or
            len({id(x) for p in (l1.donor,l1.recipient,r1.recipient,left.final)
                     for x in (p.old,p.new)})!=8):
            return
        if l1.edge!=r1.edge or l1.edge is None:
            return
        self.expected=(a,b)
        self._scope_objects=(l1.donor,l1.recipient,r1.recipient,left.final)
        self.status='ROUTES_DECLARED'

    def _counts(self):
        a=self.left
        pairs=(a.first.donor,a.first.recipient,self.right.first.recipient,a.final)
        return tuple((len(p.old.snapshot.edges),len(p.new.snapshot.edges)) for p in pairs)

    @staticmethod
    def _compose(chain, report):
        # Each pair's old and new maps must be independently certified by
        # this chain's .advance(). Never infer from common state *names*.
        donor_edge=report.links[0][0]
        ds,action,dt,dns,dnt=donor_edge
        fo,gn=chain.first.old_map,chain.first.new_map
        ho,hn=chain.old_map,chain.new_map
        if (set(fo)!={ds,dt} or set(gn)!={dns,dnt} or
            set(ho)!={fo[ds],fo[dt]} or set(hn)!={gn[dns],gn[dnt]}):
            return None
        return ((ds,ho[fo[ds]]),(dt,ho[fo[dt]]),
                (dns,hn[gn[dns]]),(dnt,hn[gn[dnt]]))

    def advance(self):
        before=self._counts() if self.status=='ROUTES_DECLARED' else ()
        def result(status,a=None,b=None,donor=(),ca=(),cb=(),conflict=(),detail=''):
            return RouteComparison(status,a,b,donor,ca,cb,conflict,before,
                                   self._counts() if before else (),detail)
        if self.status!='ROUTES_DECLARED':return result(self.status)
        if ((self.left.first.donor,self.left.first.recipient,
             self.right.first.recipient,self.left.final)!=self._scope_objects or
            self.right.first.donor is not self._scope_objects[0] or
            self.right.final is not self._scope_objects[3]):
            return result('ROUTE_SCOPE_CHANGED',detail='Pinned route scope identity changed after declaration.')
        a=self.left.advance()
        b=self.right.advance()  # Always separately check both; retain each report.
        valid='TWO_HOP_CHAIN_WITNESSED'
        if a.status!=valid or b.status!=valid:
            return result('ROUTE_EVIDENCE_UNPROVED',a,b,detail='Each independent chain must be currently evidenced.')
        if (a.fingerprint,b.fingerprint)!=self.expected:
            return result('ROUTE_FINGERPRINT_MISMATCH',a,b)
        if (len(a.links)!=2 or len(b.links)!=2 or a.links[0][0]!=b.links[0][0]):
            return result('ROUTE_DONOR_EDGE_MISMATCH',a,b)
        ca,cb=self._compose(self.left,a),self._compose(self.right,b)
        if ca is None or cb is None:
            return result('ROUTE_MAPPING_INCOMPLETE',a,b,a.links[0][0])
        disagreement=tuple((index,ca[index],cb[index])
                           for index in range(4) if ca[index]!=cb[index])
        # Audit after comparison as well: no success or contradiction report
        # survives if a pin, version, or owner-backed observation changed.
        again_a=self.left.advance();again_b=self.right.advance()
        if (again_a.status!=valid or again_b.status!=valid or
            (again_a.fingerprint,again_b.fingerprint)!=self.expected):
            return result('ROUTE_EVIDENCE_WITHDRAWN',again_a,again_b,a.links[0][0],ca,cb)
        if disagreement:
            return result('ROUTE_COMPOSED_MAP_CONFLICT',a,b,a.links[0][0],ca,cb,disagreement,
                          'Independently witnessed routes disagree on the same donor endpoint image; neither is discarded.')
        return result('ROUTES_AGREE_ON_SELECTED_EDGE',a,b,a.links[0][0],ca,cb,
                      detail='Only the declared selected donor edge agrees; no additional edges or global equivalence inferred.')
