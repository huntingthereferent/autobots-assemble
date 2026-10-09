import json, numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

trace=json.load(open(r"C:\Users\teepa\arc3\solve\m0r0_oracle_trace.json"))

def frame(env):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def comps(env,color):
    g=frame(env); seen=np.zeros_like(g,dtype=bool); out=[]
    for y in range(64):
        for x in range(64):
            if seen[y,x] or int(g[y,x])!=color: continue
            st=[(y,x)];seen[y,x]=1;pts=[]
            while st:
                cy,cx=st.pop();pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==color:
                        seen[ny,nx]=1;st.append((ny,nx))
            ys=[p[0] for p in pts];xs=[p[1] for p in pts]
            out.append((min(xs),min(ys),max(xs),max(ys),len(pts)))
    return sorted(out)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)

def state_after_first_switch():
    env=arc.make("m0r0")
    for t in trace[:39]:
        aid=t[0]; action=getattr(GameAction,"ACTION"+str(aid)); data={"x":t[1],"y":t[2]} if aid==6 else {}
        env.step(action,data=data,reasoning={"p":"prefix"})
    return env

for side,xy in [("left",(23,47)),("right",(39,47))]:
    for aname in ["ACTION3","ACTION4"]:
        env=state_after_first_switch()
        print("BASE",side,aname,"inactive",comps(env,1),"active10",comps(env,10),"cursor11",comps(env,11))
        o=env.step(GameAction.ACTION6,data={"x":xy[0],"y":xy[1]},reasoning={"p":"reactivate_"+side})
        print("REACT",comps(env,10))
        o=env.step(getattr(GameAction,aname),data={},reasoning={"p":"horiz"})
        print("MOVE",side,aname,comps(env,10),"level",o.levels_completed)
