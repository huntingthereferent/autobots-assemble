import json, numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

trace=json.load(open(r"C:\Users\teepa\arc3\solve\m0r0_oracle_trace.json"))
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")

def g():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def cc(a,colors=(1,9,10,11)):
    seen=np.zeros_like(a,dtype=bool); out=[]
    for y in range(64):
        for x in range(64):
            c=int(a[y,x])
            if seen[y,x] or c not in colors: continue
            st=[(y,x)];seen[y,x]=1;pts=[]
            while st:
                cy,cx=st.pop();pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(a[ny,nx])==c:
                        seen[ny,nx]=1;st.append((ny,nx))
            ys=[p[0] for p in pts];xs=[p[1] for p in pts]
            out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return sorted(out)

last=0
for i,t in enumerate(trace):
    before=g().copy()
    before_cc=cc(before)
    aid=t[0]
    action=getattr(GameAction,"ACTION"+str(aid))
    data={"x":t[1],"y":t[2]} if aid==6 else {}
    o=env.step(action,data=data,reasoning={"oracle_geometry":True})
    if o.levels_completed>last:
        print("LEVEL_UP",last,"->",o.levels_completed,"idx",i,"action",t)
        print(" PRE",before_cc)
        print(" POST_STATE",o.state)
        last=o.levels_completed
