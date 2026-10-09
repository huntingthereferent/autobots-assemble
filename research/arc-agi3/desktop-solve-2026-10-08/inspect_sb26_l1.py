import numpy as np
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
        c=int(g[y,x]); st=[(y,x)]; seen[y,x]=1; pts=[]
        while st:
          cy,cx=st.pop(); pts.append((cy,cx))
          for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==c:
              seen[ny,nx]=1; st.append((ny,nx))
        if len(pts)<=220:
          ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
          out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return sorted(out)

def click(env,p):
    a=GameAction.ACTION6;a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"solve_l0"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for src,dst in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,src); click(env,dst)
    for _ in range(7): click(env,(63,63))
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate_l0"})
print("levels",o.levels_completed,"state",o.state,"available",o.available_actions)
g=grid(o)
for row in comps(g):
    print(row)
