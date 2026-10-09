import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def summary(g):
    out={}
    for c in [9,11,14,15]:
        ys,xs=np.where(g==c)
        pts=[]
        # group by bottom y>=55 and top y<=7
        for label,mask in [('top',ys<=7),('bottom',ys>=55)]:
            if mask.any():
                xx=xs[mask]; yy=ys[mask]
                pts.append((label,(int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())),int(mask.sum())))
        out[c]=pts
    return out

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
points=[(19,58),(27,58),(35,58),(43,58)]
print("initial",json.dumps(summary(grid(env.observation_space)),sort_keys=True))
for p in points:
    env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    before=grid(env.observation_space)
    a=GameAction.ACTION6
    a.set_data({"x":p[0],"y":p[1]})
    out=env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"single_bottom_click"})
    after=grid(out)
    ys,xs=np.where(before!=after)
    print("click",p,"changed",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),
          "levels",out.levels_completed,"state",out.state,"summary",json.dumps(summary(after),sort_keys=True))

# two-click ordered pairs from reset
pairs=[((19,58),(27,58)),((19,58),(35,58)),((19,58),(43,58)),((27,58),(35,58)),((27,58),(43,58)),((35,58),(43,58))]
for p,q in pairs:
    env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    for z in (p,q):
        a=GameAction.ACTION6; a.set_data({"x":z[0],"y":z[1]})
        out=env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"two_click"})
    print("pair",p,q,"summary",json.dumps(summary(grid(out)),sort_keys=True),"levels",out.levels_completed)
