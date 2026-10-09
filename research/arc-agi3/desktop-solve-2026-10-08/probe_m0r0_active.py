import json, numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

trace=json.load(open(r"C:\Users\teepa\arc3\solve\m0r0_oracle_trace.json"))
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")

def gg():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).copy()

def comps(g,colors):
    seen=np.zeros_like(g,dtype=bool); out=[]
    for y in range(64):
        for x in range(64):
            c=int(g[y,x])
            if seen[y,x] or c not in colors: continue
            st=[(y,x)]; seen[y,x]=1; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return sorted(out)

# Replay through first click (idx38), stop immediately after.
for i,t in enumerate(trace[:39]):
    aid=t[0]
    a=getattr(GameAction,"ACTION"+str(aid))
    data={"x":t[1],"y":t[2]} if aid==6 else {}
    env.step(a,data=data,reasoning={"probe":"oracle_prefix"})

g=gg()
print("LEVEL",env.observation_space.levels_completed)
print("AFTER_CLICK_COMPS",comps(g,{1,9,10,11}))
# Probe each direction from this exact state requires recreate prefix for each.
for aname in ["ACTION1","ACTION2","ACTION3","ACTION4"]:
    env2=arc.make("m0r0")
    for t in trace[:39]:
        aid=t[0]; a=getattr(GameAction,"ACTION"+str(aid)); data={"x":t[1],"y":t[2]} if aid==6 else {}
        env2.step(a,data=data,reasoning={"probe":"prefix"})
    b=np.asarray(env2.observation_space.frame)
    if b.ndim==3:b=b[-1]
    b=b.reshape(64,64).copy()
    o=env2.step(getattr(GameAction,aname),data={},reasoning={"probe":"dir"})
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    a=a.reshape(64,64)
    ys,xs=np.where(b!=a)
    pairs={}
    for yy,xx in zip(ys,xs):
        k=(int(b[yy,xx]),int(a[yy,xx])); pairs[k]=pairs.get(k,0)+1
    print(aname,"n",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),"pairs",pairs)
    print(" comps",comps(a,{1,9,10,11}))
