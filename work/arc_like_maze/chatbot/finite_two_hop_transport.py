"""Two successive selected-edge squares among three PAIRS of finite laws.

Independent law-level replay; unlike the integrated source this neither observes
remote owners nor authenticates pins. No unobserved edge is transported.
"""
from dataclasses import dataclass
from finite_goal_priority import Law
from finite_cross_pin_join import join
from finite_cross_scope_transport import transport

@dataclass(frozen=True)
class Chain:
    status: str
    links: tuple
    state_pairs: tuple
    admitted_edges: tuple
    obstruction: tuple | None


def chain(donor, intermediate, final, donor_words, middle_words, final_words,
          selected, first_old_map, first_new_map, second_old_map, second_new_map):
    """Scope pairs are (old Law,new Law); maps are ordered endpoint pairs."""
    for pair in (donor,intermediate,final):
        if type(pair) is not tuple or len(pair)!=2 or not all(isinstance(x,Law) for x in pair):
            raise ValueError('three explicitly declared source pairs required')
    first=transport(*intermediate,*donor,middle_words,donor_words,selected,
                    first_old_map,first_new_map)
    if first.status!='CROSS_SCOPE_SQUARE_WITNESSED':
        return Chain('FIRST_LINK_'+first.status,(),(),(),first.obstruction)
    selected_edge=next((e for e in first.admitted_edges if e[:2]==
                       (dict(first_old_map)[selected[0]],selected[1])),None)
    if selected_edge is None:return Chain('INTERMEDIATE_EDGE_UNPROVED',(),(),(),None)
    ds,a,dt,dns,dnt=selected_edge
    oldmap,newmap=dict(second_old_map),dict(second_new_map)
    if (set(oldmap)!={ds,dt} or set(newmap)!={dns,dnt} or
         len(set(oldmap.values()))!=2 or len(set(newmap.values()))!=2):
        return Chain('SECOND_MAPPING_INCOMPLETE',(first.square,),(),(),None)
    rs,rt,rns,rnt=oldmap[ds],oldmap[dt],newmap[dns],newmap[dnt]
    base=join(*final,final_words)
    if base.status!='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED':
        return Chain('FINAL_BASE_UNPROVED',(first.square,),(),(),base.contradiction)
    f=dict(base.state_pairs)
    if f.get(rs)!=rns:
        return Chain('SECOND_PREFIX_UNPROVED',(first.square,),(),(),(rs,rns))
    observed_old,observed_new=final[0].step(rs,a),final[1].step(rns,a)
    square=(selected_edge,(rs,a,observed_old,rns,observed_new),(rs,rt,rns,rnt))
    if (observed_old,observed_new)!=(rt,rnt):
        return Chain('SECOND_INTERTWINING_CONFLICT',(first.square,square),(),(),
                     (rt,observed_old,rnt,observed_new))
    inv={v:k for k,v in f.items()}
    if (rt in f and f[rt]!=rnt) or (rnt in inv and inv[rnt]!=rt):
        return Chain('SECOND_PAIR_CONFLICT',(first.square,square),(),(),(rt,rnt))
    edges=set(base.admitted_edges)
    edges.add((rs,a,rt,rns,rnt)); f[rt]=rnt
    assert all(f[s]==ns and f[t]==nt and final[0].step(s,k)==t and
               final[1].step(ns,k)==nt for s,k,t,ns,nt in edges)
    return Chain('TWO_HOP_CHAIN_WITNESSED',(first.square,square),
                 tuple(sorted(f.items())),tuple(sorted(edges)),None)

if __name__=='__main__':
    d=(Law((0,0,1)),Law((1,0,1)))
    m=(Law((0,0,0)),Law((0,1,2)))
    f=(Law((2,0,0)),Law((2,2,1)))
    report=chain(d,m,f,('AB','B'),('A','BAA'),('A','BAA'),((1,0,0),'B'),
        (((1,0,0),(1,0,0)),((1,2,0),(1,2,0))),
        (((1,0,0),(1,0,0)),((1,2,1),(1,2,0))),
        (((1,0,0),(1,0,0)),((1,2,0),(1,2,2))),
        (((1,0,0),(1,0,0)),((1,2,0),(1,2,2))))
    print(report.status,len(report.links),len(report.state_pairs),len(report.admitted_edges))
