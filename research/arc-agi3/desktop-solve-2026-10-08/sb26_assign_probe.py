import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64)

def diff(a,b):
 ys,xs=np.where(a!=b)
 return {"n":int(len(xs)),"bbox":None if len(xs)==0 else [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
         "pts":[[int(x),int(y),int(a[y,x]),int(b[y,x])] for y,x in zip(ys,xs)][:80]}

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# bottom color 14 (teal) at (20,58); top gray slot centers x20,27,34,41 y3
out=[]
for sx in [20,27,34,41]:
 env.step(GameAction.RESET,data={},reasoning={"p":"r"})
 base=g(env.observation_space)
 a=GameAction.ACTION6;a.set_data({"x":20,"y":58})
 o=env.step(a,data={"x":20,"y":58},reasoning={"p":"palette"})
 after_palette=g(o)
 b=GameAction.ACTION6;b.set_data({"x":sx,"y":3})
 z=env.step(b,data={"x":sx,"y":3},reasoning={"p":"slot"})
 out.append({"slot_x":sx,"palette":diff(base,after_palette),"slot_click":diff(after_palette,g(z)),"total":diff(base,g(z)),
             "levels":int(z.levels_completed),"state":str(z.state)})
print(json.dumps(out,indent=2))
