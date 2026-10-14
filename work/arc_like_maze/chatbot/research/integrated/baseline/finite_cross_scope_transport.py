"""Scoped four-law edge intertwining: evidence must be checked on BOTH source scopes.

Standalone finite reference: knowing each complete Law does not authenticate an owner
or count as observing a transition. The integrated adapter uses pinned observations.
"""
from dataclasses import dataclass
from finite_goal_priority import Law
from finite_cross_pin_join import join

@dataclass(frozen=True)
class FiniteCrossTransport:
    status: str
    state_pairs: tuple
    admitted_edges: tuple
    square: tuple
    obstruction: tuple | None


def transport(recipient_old:Law, recipient_new:Law, donor_old:Law, donor_new:Law,
              recipient_words, donor_words, selected, old_map, new_map):
    """Witness one commuting square of both actions between two finite join spaces.

    Maps are explicit donor-state -> recipient-state correspondences; no inference.
    """
    if (type(selected) is not tuple or len(selected)!=2 or selected[1] not in ('A','B') or
        type(old_map) is not tuple or type(new_map) is not tuple or
        len({s for s,_ in old_map}) != len(old_map) or
        len({s for s,_ in new_map}) != len(new_map)):
        raise ValueError('explicit bounded selected edge and mapping required')
    recipient=join(recipient_old,recipient_new,tuple(recipient_words))
    donor=join(donor_old,donor_new,tuple(donor_words))
    if not recipient.status==donor.status=='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED':
        return FiniteCrossTransport('BASE_JOIN_UNPROVED',(),(),(),None)
    donor_edges={(s,a):(s,a,t,ns,nt) for s,a,t,ns,nt in donor.admitted_edges}
    if selected not in donor_edges:
        return FiniteCrossTransport('DONOR_EDGE_UNPROVED',(),(),(),selected)
    ds,a,dt,dns,dnt=donor_edges[selected]
    fo=dict(old_map);gn=dict(new_map)
    if set(fo)!={ds,dt} or set(gn)!={dns,dnt}:
        return FiniteCrossTransport('MAPPING_INCOMPLETE',(),(),(),selected)
    rs,rt,rns,rnt=fo[ds],fo[dt],gn[dns],gn[dnt]
    f=dict(recipient.state_pairs)
    if f.get(rs)!=rns:
        return FiniteCrossTransport('RECIPIENT_PREFIX_UNPROVED',(),(),(),(rs,rns))
    # The recipient edges must actually be observed on the recipient scope in
    # the integrated layer. This finite reference checks the analogous laws.
    observed_old=recipient_old.step(rs,a)
    observed_new=recipient_new.step(rns,a)
    square=(selected,((ds,dt),(dns,dnt)),((rs,observed_old),(rns,observed_new)))
    if (observed_old!=rt or observed_new!=rnt):
        return FiniteCrossTransport('INTERTWINING_CONFLICT',(),(),square,
                (rt,observed_old,rnt,observed_new))
    inverse={n:s for s,n in f.items()}
    if (rt in f and f[rt]!=rnt) or (rnt in inverse and inverse[rnt]!=rt):
        return FiniteCrossTransport('RECIPIENT_PAIR_CONFLICT',(),(),square,(rt,rnt,f.get(rt),inverse.get(rnt)))
    edges=set(recipient.admitted_edges)
    edges.add((rs,a,rt,rns,rnt));f[rt]=rnt
    assert all(recipient_old.step(s,k)==t and recipient_new.step(ns,k)==nt and
               f[s]==ns and f[t]==nt for s,k,t,ns,nt in edges)
    return FiniteCrossTransport('CROSS_SCOPE_SQUARE_WITNESSED',tuple(sorted(f.items())),
                                tuple(sorted(edges)),square,None)

if __name__=='__main__':
    r=transport(Law((0,0,0)),Law((0,1,2)),Law((0,0,1)),Law((1,0,1)),
        ('A','BAA'),('AB','B'),((1,0,0),'B'),
        (((1,0,0),(1,0,0)),((1,2,0),(1,2,0))),
        (((1,0,0),(1,0,0)),((1,2,1),(1,2,0))))
    print(r.status,len(r.state_pairs),len(r.admitted_edges),r.obstruction)
