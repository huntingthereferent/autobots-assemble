import runpy
ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ar25_full_tree_ab_audit.py")
nodes=ns["nodes"];classes=ns["classes"];split=ns["split"];ACTIONS=ns["ACTIONS"]

def shortest(p,q,seen=None):
    if p not in nodes or q not in nodes:return None
    if seen is None:seen=set()
    key=(p,q)
    if key in seen:return None
    seen.add(key)
    a=nodes[p];b=nodes[q]
    for z in ACTIONS:
        x=next(t for t in a["immediate"] if t[0]==z)
        y=next(t for t in b["immediate"] if t[0]==z)
        if x[1:]!=y[1:]:return (z,)
    best=None
    for z in ACTIONS:
        cp=a["children"].get(z);cq=b["children"].get(z)
        if cp is None or cq is None:continue
        tail=shortest(cp,cq,seen)
        if tail is not None:
            cand=(z,)+tail
            if best is None or len(cand)<len(best):best=cand
    return best

from collections import defaultdict
print("DELAYED_FULL_TREE")
count=0
for obs,sids in split.items():
    members=[p for p,n in nodes.items() if n["obs"]==obs]
    immediate=False
    for z in ACTIONS:
        vals={next(t for t in nodes[p]["immediate"] if t[0]==z)[1:] for p in members}
        if len(vals)>1:
            immediate=True;break
    if immediate:continue
    # find shortest witnessed distinction between different A/B classes
    best=None;pair=None
    for i,p in enumerate(members):
        for q in members[i+1:]:
            if classes[p]==classes[q]:continue
            suf=shortest(p,q)
            if suf is not None and (best is None or len(suf)<len(best)):
                best=suf;pair=(p,q)
    print(obs,"AB",len(sids),"PAIR",pair,"SUFFIX",best)
    if best is not None:count+=1
print("WITNESSED_DELAYED",count)
