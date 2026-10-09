import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(int)

def click(env,p,label):
    a=GameAction.ACTION6; a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":label})

def delta(a,b):
    ys,xs=np.where(a!=b)
    return len(xs), None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
g0=grid(env.observation_space)
o1=click(env,(35,58),"select_bottom_9")
g1=grid(o1)
print("select delta",delta(g0,g1),"levels",o1.levels_completed)
o2=click(env,(22,29),"place_middle_slot0")
g2=grid(o2)
print("place immediate",delta(g1,g2),"levels",o2.levels_completed,"state",o2.state)
# advance with harmless ACTION5 calls to see animation settle
prev=g2
for i in range(1,12):
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"advance_animation","i":i})
    cur=grid(o)
    print("advance",i,"delta",delta(prev,cur),"levels",o.levels_completed,"state",o.state)
    prev=cur
