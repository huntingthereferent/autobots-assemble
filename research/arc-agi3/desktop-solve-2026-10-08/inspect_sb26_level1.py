import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import objects

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)
def click(env,x,y):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"probe":"advance"})
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
moves=[((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]
for src,dst in moves:
    click(env,*src); click(env,*dst)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate"})
print("LEVEL",o.levels_completed,"avail",o.available_actions)
for x in sorted(objects(grid(o)), key=lambda z:(z.y0,z.x0,z.color,z.size)):
    if x.size<=400:
        print({"color":x.color,"size":x.size,"box":(x.x0,x.y0,x.x1,x.y1),"center":(x.cx2/2,x.cy2/2)})
