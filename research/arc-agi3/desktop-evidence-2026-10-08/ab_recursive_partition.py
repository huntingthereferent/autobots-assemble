"""Generic recursive A/B partition refinement to witnessed fixed point."""
from collections import defaultdict

def partition(classes):
    b=defaultdict(list)
    for k,v in classes.items():b[v].append(k)
    return frozenset(frozenset(x) for x in b.values())

def renumber(keys):
    table={};out={}
    for k,v in keys.items():
        if v not in table:table[v]=len(table)
        out[k]=table[v]
    return out

def ab_fixed_point(nodes,max_rounds=32):
    # Initial output: current referent + immediate witnessed continuation.
    classes=renumber({
        p:(n["obs"],n["immediate"])
        for p,n in nodes.items()
    })
    history=[partition(classes)]

    for rnd in range(1,max_rounds+1):
        keys={}
        for p,n in nodes.items():
            succ=[]
            children=n.get("children",{})
            for item in n["immediate"]:
                z,no,lc,st=item[:4]
                cp=children.get(z)
                successor=classes.get(cp,("boundary",no,lc,st))
                succ.append((z,no,lc,st,successor))
            keys[p]=(n["obs"],tuple(succ))
        new=renumber(keys)
        part=partition(new)
        history.append(part)
        if part==history[-2]:
            return new,history
        classes=new

    raise RuntimeError("A/B fixed point did not close")
