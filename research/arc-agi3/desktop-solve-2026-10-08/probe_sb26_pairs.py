import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import effect, objects

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def click(env,x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"probe":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
base=arr(env.observation_space)
obs=objects(base)
candidates=[]; seen=set()
for o in obs:
    if o.size>400: continue
    xy=(o.cx2//2,o.cy2//2)
    if xy in seen: continue
    seen.add(xy)
    candidates.append((xy[0],xy[1],o.color,o.size,o.x0,o.y0,o.x1,o.y1))
sources=[(19,58),(27,58),(35,58),(43,58)]
print("candidate count",len(candidates))
for sx,sy in sources:
    print("\nSOURCE",sx,sy)
    for x,y,color,size,x0,y0,x1,y1 in candidates:
        env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
        o1=click(env,sx,sy,"select")
        before=arr(o1)
        o2=click(env,x,y,"second")
        e=effect(before,arr(o2))
        if e.changed_pixels or o2.levels_completed:
            print("SECOND",{"xy":(x,y),"color":color,"size":size,"box":(x0,y0,x1,y1),"effect":e,"levels":o2.levels_completed})
