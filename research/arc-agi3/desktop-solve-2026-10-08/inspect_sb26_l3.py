import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(int)

def click(env,p,label):
    a=GameAction.ACTION6;a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":label})

def settle(env):
    for _ in range(7): click(env,(63,63),"settle")

def do_level(env,moves,label):
    for src,dst in moves:
        click(env,src,label+"s");click(env,dst,label+"p");settle(env)
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":label+"eval"})

def comps(g):
    seen=np.zeros((64,64),bool);out=[]
    for y in range(64):
      for x in range(64):
        if seen[y,x]:continue
        c=int(g[y,x]);st=[(y,x)];seen[y,x]=1;pts=[]
        while st:
          cy,cx=st.pop();pts.append((cy,cx))
          for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=cy+dy,cx+dx
            if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==c:
              seen[ny,nx]=1;st.append((ny,nx))
        if len(pts)<=320:
          ys=[p[0] for p in pts];xs=[p[1] for p in pts]
          out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return sorted(out)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# l0
o=do_level(env,[((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))],"l0")
print("after l0",o.levels_completed)
# l1
o=do_level(env,[((32,58),(22,22)),((18,58),(28,22)),((10,58),(22,36)),((46,58),(28,36)),((24,58),(34,36)),((52,58),(40,36)),((38,58),(40,22))],"l1")
print("after l1",o.levels_completed)
# l2
o=do_level(env,[((52,58),(20,24)),((18,58),(20,36)),((24,58),(26,36)),((32,58),(32,24)),((46,58),(38,36)),((38,58),(44,36)),((10,58),(44,24))],"l2")
print("after l2",o.levels_completed,"state",o.state,"avail",o.available_actions)
for row in comps(grid(o)):
    print(row)
