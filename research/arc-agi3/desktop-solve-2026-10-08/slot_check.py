import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for sx in [20,27,34,41]:
 env.step(GameAction.RESET,data={},reasoning={"r":"r"})
 a=GameAction.ACTION6;a.set_data({"x":20,"y":58})
 o=env.step(a,data={"x":20,"y":58},reasoning={"r":"p"})
 b=GameAction.ACTION6;b.set_data({"x":sx,"y":3})
 before=g(o).copy()
 z=env.step(b,data={"x":sx,"y":3},reasoning={"r":"s"})
 print(sx,int(np.sum(before!=g(z))),z.levels_completed,str(z.state))
