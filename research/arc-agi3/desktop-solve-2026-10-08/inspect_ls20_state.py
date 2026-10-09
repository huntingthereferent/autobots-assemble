import numpy as np, json
from collections import Counter, defaultdict
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(int)

def comps(g):
    seen=np.zeros((64,64),bool); out=[]
    for y in range(64):
      for x in range(64):
        if seen[y,x]: continue
        c=int(g[y,x]); st=[(y,x)];seen[y,x]=1;pts=[]
        while st:
          cy,cx=st.pop();pts.append((cy,cx))
          for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==c:
              seen[ny,nx]=1;st.append((ny,nx))
        ys=[p[0] for p in pts];xs=[p[1] for p in pts]
        out.append({"color":c,"size":len(pts),"x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),
                    "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,
                    "cx2":min(xs)+max(xs),"cy2":min(ys)+max(ys)})
    return sorted(out,key=lambda z:(z["size"],z["color"],z["y0"],z["x0"]))

def match(before,after):
    B=comps(before);A=comps(after)
    by=defaultdict(list)
    for j,c in enumerate(A):by[(c["color"],c["size"],c["w"],c["h"])].append((j,c))
    used=set();out=[]
    for b in B:
      sig=(b["color"],b["size"],b["w"],b["h"])
      opts=[]
      for j,a in by.get(sig,[]):
        if j in used:continue
        dist=abs(a["cx2"]-b["cx2"])+abs(a["cy2"]-b["cy2"])
        opts.append((dist,j,a))
      if not opts:continue
      dist,j,a=min(opts,key=lambda z:z[0]);used.add(j)
      dx=a["cx2"]-b["cx2"];dy=a["cy2"]-b["cy2"]
      if dx or dy:out.append((sig,(b["x0"],b["y0"],b["x1"],b["y1"]),(a["x0"],a["y0"],a["x1"],a["y1"]),dx,dy))
    return out

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("ls20")
base=grid(env.observation_space)
print("AVAILABLE",env.observation_space.available_actions)
print("BASE SMALL/MID COMPONENTS")
for c in comps(base):
    if c["size"]<=500:
        print(c)
for act in [GameAction.ACTION1,GameAction.ACTION2,GameAction.ACTION3,GameAction.ACTION4]:
    env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    b=grid(env.observation_space)
    o=env.step(act,data={},reasoning={"probe":"single"})
    a=grid(o)
    ys,xs=np.where(b!=a)
    print("\nACTION",act.name,"delta",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())))
    print("MOTIONS",match(b,a))
    pairs=Counter((int(b[y,x]),int(a[y,x])) for y,x in zip(ys,xs))
    print("PAIRS",dict(pairs))
