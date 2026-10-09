import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(int)

def click(env,p):
    a=GameAction.ACTION6;a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"advance_l0"})

# solve l0 from visible relation
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for src,dst in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,src); click(env,dst)
    for _ in range(7): click(env,(63,63))
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval_l0"})
g=grid(o)

# print middle region 14:49 x 14:45 as run-length rows for colors != background 4
for y in range(14,46):
    spans=[]
    x=0
    while x<64:
        c=int(g[y,x]); x0=x
        while x+1<64 and int(g[y,x+1])==c: x+=1
        if c!=4 and x>=14 and x0<=49:
            spans.append((max(x0,14),min(x,49),c))
        x+=1
    if spans:
        print(y,spans)
