import runpy
ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ar25_generic_ab_fixed_point.py")
nodes=ns["nodes"];classes=ns["classes"];split=ns["split"];ACTIONS=ns["ACTIONS"]

def first_difference(p,q):
    a=nodes[p];b=nodes[q]
    for z in ACTIONS:
        x=next(t for t in a["immediate"] if t[0]==z)
        y=next(t for t in b["immediate"] if t[0]==z)
        if x[1:]!=y[1:]:
            return (z,)
    candidates=[]
    for z in ACTIONS:
        cp=a["children"].get(z);cq=b["children"].get(z)
        if cp in nodes and cq in nodes:
            tail=first_difference(cp,cq)
            if tail is not None:candidates.append((z,)+tail)
    return min(candidates,key=len) if candidates else None

print("DELAYED")
for obs in split:
    members=[p for p,n in nodes.items() if n["obs"]==obs]
    immediate_var=False
    for z in ACTIONS:
        vals={next(t for t in nodes[p]["immediate"] if t[0]==z)[1:] for p in members}
        if len(vals)>1:
            immediate_var=True
            break
    if immediate_var:continue
    pair=None
    for i,p in enumerate(members):
        for q in members[i+1:]:
            if classes[p]!=classes[q]:
                pair=(p,q);break
        if pair:break
    if pair:
        print(obs,pair,first_difference(*pair))
