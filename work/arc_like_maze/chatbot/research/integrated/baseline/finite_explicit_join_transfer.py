"""Independent finite-law oracle for explicitly selected witnessed edge transfer.

Full laws are known in this standalone checker; it does not authenticate sources.
The two base joins are separately replayed and never modified.
"""
from dataclasses import dataclass
from finite_cross_pin_join import join
from finite_goal_priority import Law,ROOT

@dataclass(frozen=True)
class FiniteTransfer:
    status: str
    pairs: tuple
    edges: tuple
    cause: tuple | None


def transfer(old:Law,new:Law,recipient_words,donor_words,requested):
    if not (type(requested) is tuple and requested and len(set(requested))==len(requested)
            and all(type(k) is tuple and len(k)==2 and k[1] in ('A','B') for k in requested)):
        raise ValueError('nonempty distinct selected labeled edges required')
    a=join(old,new,tuple(recipient_words))
    b=join(old,new,tuple(donor_words))
    if a.status!='JOINT_PARTIAL_CORRESPONDENCE_WITNESSED' or b.status!=a.status:
        return FiniteTransfer('BASE_WITNESS_UNPROVED',(),(),None)
    f=dict(a.state_pairs);inv={v:k for k,v in f.items()}
    edges={(s,label):(s,label,t,ns,nt) for s,label,t,ns,nt in a.admitted_edges}
    donor={(s,label):(s,label,t,ns,nt) for s,label,t,ns,nt in b.admitted_edges}
    def rooted():
        reached={ROOT}
        queue=[ROOT]
        for s in queue:
            for (u,act),edge in sorted(edges.items()):
                if u==s and edge[2] not in reached:
                    reached.add(edge[2]);queue.append(edge[2])
        return reached
    for key in requested:
        if key not in donor:return FiniteTransfer('EDGE_NOT_WITNESSED',(),(),key)
        s,label,t,ns,nt=donor[key]
        if s not in rooted():return FiniteTransfer('PREFIX_UNWITNESSED',(),(),key)
        if f[s]!=ns or t in f and f[t]!=nt or nt in inv and inv[nt]!=t:
            return FiniteTransfer('INCOMPATIBLE_EDGE',(),(),(key,t,nt,f.get(t),inv.get(nt)))
        edges[key]=(s,label,t,ns,nt)
        f[t]=nt;inv[nt]=t
    assert all(old.step(s,a)==t and new.step(ns,a)==nt and
               f[s]==ns and f[t]==nt for s,a,t,ns,nt in edges.values())
    assert set(f)==rooted()
    return FiniteTransfer('EXPLICIT_TRANSFER_WITNESSED',tuple(sorted(f.items())),
                          tuple(sorted(edges.values())),None)

if __name__=='__main__':
    a,b=Law((0,0,0)),Law((0,1,2))
    for selected in ((((1,0,0),'B'),),(((1,0,0),'B'),((1,2,0),'B'))):
        r=transfer(a,b,('A','BAA'),('B','ABB'),selected)
        print(selected,r.status,len(r.pairs),len(r.edges),r.cause)
