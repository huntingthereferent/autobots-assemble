from collections import Counter,defaultdict
import numpy as np
import arc_agi
from arc_agi import OperationMode

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def components(g):
    h,w=g.shape; seen=np.zeros((h,w),bool); raw=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); st=[(y,x)]; seen[y,x]=1; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            raw.append(dict(color=c,size=len(pts),x0=min(xs),x1=max(xs),y0=min(ys),y1=max(ys),
                            cx2=min(xs)+max(xs),cy2=min(ys)+max(ys),
                            w=max(xs)-min(xs)+1,h=max(ys)-min(ys)+1))
    dom=max(range(len(raw)),key=lambda i:raw[i]["size"])
    return [c for i,c in enumerate(raw) if i!=dom]

def rows(cs):
    groups=defaultdict(list)
    for c in cs:
        groups[(c["cy2"],c["size"],c["w"],c["h"])].append(c)
    out=[]
    for k,v in groups.items():
        if 3<=len(v)<=10:
            vv=sorted(v,key=lambda c:c["cx2"])
            out.append(dict(key=k,y=k[0],colors=[c["color"] for c in vv],
                            xs=[c["cx2"]//2 for c in vv], comps=vv))
    return out

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
rs=rows(components(grid(env.observation_space)))
print("ROWS")
for i,r in enumerate(rs):
    print(i,r["key"],r["colors"],r["xs"])

print("HYPOTHESES")
for i,a in enumerate(rs):
    for j,b in enumerate(rs):
        if j<=i or len(a["colors"])!=len(b["colors"]): continue
        if Counter(a["colors"])!=Counter(b["colors"]): continue
        n=len(a["colors"])
        if len(set(a["colors"]))<max(2,n-1): continue
        lo,hi=sorted((a["y"],b["y"]))
        for k,s in enumerate(rs):
            if k in (i,j) or len(s["colors"])!=n: continue
            if not (lo<s["y"]<hi): continue
            if len(set(s["colors"]))!=1: continue
            print("PAIR",i,j,"slots",k,"A",a["colors"],"B",b["colors"],"S",s["colors"])
