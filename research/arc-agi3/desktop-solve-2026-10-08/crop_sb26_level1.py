import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def click(env,x,y):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"probe":"advance"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
moves=[((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]
for s,d in moves:
    click(env,*s); click(env,*d)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
g=arr(o)
print("levels",o.levels_completed)
# print middle crop, sampled exactly, using hex-ish chars
chars="0123456789ABCDEF"
for y in range(16,43):
    row="".join(chars[int(v)] if int(v)<16 else "?" for v in g[y,16:48])
    print(f"{y:02d} {row}")
