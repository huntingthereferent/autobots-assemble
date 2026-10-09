import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:
        a=a[-1]
    return a.reshape(64,64)

def changed(a,b):
    ys,xs=np.where(a!=b)
    if len(xs)==0:
        return [0,None]
    return [int(len(xs)),[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]]

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
tests=[["a",[18,1]],["b",[25,1]],["c",[32,1]],["d",[39,1]]]
res=[]
for name,xy in tests:
    env.step(GameAction.RESET,data={},reasoning={"test":"reset"})
    before=grid(env.observation_space)
    act=GameAction.ACTION6
    act.set_data({"x":xy[0],"y":xy[1]})
    obs=env.step(act,data={"x":xy[0],"y":xy[1]},reasoning={"test":"pixel"})
    res.append([name,xy,changed(before,grid(obs)),int(obs.levels_completed),str(obs.state)])
print(json.dumps(res))
