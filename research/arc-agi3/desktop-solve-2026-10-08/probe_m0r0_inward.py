import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")
env.step(GameAction.RESET,data={},reasoning={"probe":"start"})

def positions():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    g=a.reshape(64,64)
    seen=np.zeros_like(g,dtype=bool); out=[]
    for y in range(64):
        for x in range(64):
            if seen[y,x] or int(g[y,x])!=10: continue
            st=[(y,x)]; seen[y,x]=1; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==10:
                        seen[ny,nx]=1; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append((min(xs),min(ys),max(xs),max(ys),len(pts)))
    return out

print("start",positions(),env.observation_space.levels_completed)
for i in range(5):
    o=env.step(GameAction.ACTION4,data={},reasoning={"probe":"inward"})
    print(i+1,positions(),"level",o.levels_completed,"state",o.state)
    if o.levels_completed>0: break
