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
# select bottom teal/color14, then click each middle red block
for sx in [22,28,34,40]:
 env.step(GameAction.RESET,data={},reasoning={"p":"r"})
 base=g(env.observation_space)
 a=GameAction.ACTION6;a.set_data({"x":20,"y":58})
 o=env.step(a,data={"x":20,"y":58},reasoning={"p":"palette"})
 before=g(o)
 b=GameAction.ACTION6;b.set_data({"x":sx,"y":29})
 z=env.step(b,data={"x":sx,"y":29},reasoning={"p":"middle"})
 print("slot",sx,json.dumps(diff(before,g(z))),"levels",z.levels_completed,"state",z.state)
