import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def seq(g):
    # bottom four slots by dominant non-bg color in known visible slot boxes, inferred by x bands
    slots=[]
    for x0,x1 in [(17,22),(25,30),(33,38),(41,46)]:
        sub=g[56:62,x0:x1+1]
        vals,counts=np.unique(sub,return_counts=True)
        cand=[(int(n),int(v)) for v,n in zip(vals,counts) if int(v) not in (4,5)]
        slots.append(max(cand)[1] if cand else None)
    return slots

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
points=[(19,58),(27,58),(35,58),(43,58)]
print("initial",seq(grid(env.observation_space)))
for p in points:
    env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    click=GameAction.ACTION6; click.set_data({"x":p[0],"y":p[1]})
    o1=env.step(click,data=click.action_data.model_dump(),reasoning={"probe":"select"})
    before=grid(o1)
    o2=env.step(GameAction.ACTION5,data={},reasoning={"probe":"act_after_select"})
    after=grid(o2)
    ys,xs=np.where(before!=after)
    print("select",p,"after5 seq",seq(after),"changed",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),
          "levels",o2.levels_completed,"state",o2.state)
    # second ACTION5
    before2=after.copy()
    o3=env.step(GameAction.ACTION5,data={},reasoning={"probe":"second_act"})
    after2=grid(o3)
    ys,xs=np.where(before2!=after2)
    print(" second5 seq",seq(after2),"changed",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),
          "levels",o3.levels_completed,"state",o3.state)
