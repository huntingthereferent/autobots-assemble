import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import objects

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)
def click(env,xy,why):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# level 0
for s,d in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,s,"L0");click(env,d,"L0")
env.step(GameAction.ACTION5,data={},reasoning={"probe":"L0 eval"})
# level 1
ref=[12,15,8,9,14,11,6]
source={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
order=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
for c,d in zip(ref,order):
    click(env,source[c],"L1");click(env,d,"L1")
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"L1 eval"})
print("LEVEL",o.levels_completed,"avail",o.available_actions)
g=arr(o)
for x in sorted(objects(g),key=lambda z:(z.y0,z.x0,z.color,z.size)):
    if x.size<=450:
        print({"color":x.color,"size":x.size,"box":(x.x0,x.y0,x.x1,x.y1),"center":(x.cx2/2,x.cy2/2)})
print("CROP")
chars="0123456789ABCDEF"
for y in range(12,48):
    print(f"{y:02d} "+"".join(chars[int(v)] if int(v)<16 else "?" for v in g[y,8:56]))
