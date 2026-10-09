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

def settle(env,n=7):
    o=None
    for i in range(n): o=click(env,(63,63),f"settle_{i}")
    return o

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
        if len(pts)<=260:
          ys=[p[0] for p in pts];xs=[p[1] for p in pts]
          out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return sorted(out)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# l0
for src,dst in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,src,"l0s");click(env,dst,"l0p");settle(env)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"l0eval"})
print("after l0",o.levels_completed)
# l1
src={8:(11,58),15:(18,58),14:(25,58),12:(32,58),6:(39,58),9:(46,58),11:(53,58)}
path=[(12,(22,22)),(15,(28,22)),(8,(22,36)),(9,(28,36)),(14,(34,36)),(11,(40,36)),(6,(40,22))]
for c,dst in path:
    click(env,src[c],"l1s");click(env,dst,"l1p");settle(env)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"l1eval"})
print("after l1",o.levels_completed,"state",o.state,"avail",o.available_actions)
g=grid(o)
for row in comps(g):
    print(row)
