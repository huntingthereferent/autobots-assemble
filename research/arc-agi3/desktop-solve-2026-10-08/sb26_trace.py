import numpy as np
from collections import Counter
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(np.int16)

def delta(a,b):
    ys,xs=np.where(a!=b)
    print(" changed",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())))
    pts=[(int(x),int(y),int(a[y,x]),int(b[y,x])) for y,x in zip(ys,xs)]
    print(" pts",pts[:80])

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
prev=grid(obs)
print("START bottom rows 53:63")
print(prev[53:64,:].tolist())
steps=[("c9",GameAction.ACTION6,{"x":36,"y":58}),
       ("c14",GameAction.ACTION6,{"x":20,"y":58}),
       ("c11",GameAction.ACTION6,{"x":44,"y":58}),
       ("c15",GameAction.ACTION6,{"x":28,"y":58}),
       ("A5",GameAction.ACTION5,{})]
for name,a,data in steps:
    if a is GameAction.ACTION6:a.set_data(data)
    obs=env.step(a,data=data,reasoning={"trace":name})
    cur=grid(obs)
    print("\n",name,"levels",obs.levels_completed,"state",obs.state)
    delta(prev,cur)
    print(" bottom53",cur[53,:].tolist())
    print(" bottom56_61",cur[56:62,15:49].tolist())
    prev=cur
