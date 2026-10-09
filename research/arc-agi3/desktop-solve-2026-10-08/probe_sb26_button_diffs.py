import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
buttons=[("c14",19,58),("c15",27,58),("c9",35,58),("c11",43,58)]
for name,x,y in buttons:
    env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    b=grid(env.observation_space)
    a6=GameAction.ACTION6
    a6.set_data({"x":x,"y":y})
    out=env.step(a6,data={"x":x,"y":y},reasoning={"probe":"button"})
    a=grid(out)
    ys,xs=np.where(b!=a)
    print("\n",name,"changed",len(xs))
    for yy,xx in zip(ys,xs):
        print((int(xx),int(yy),int(b[yy,xx]),int(a[yy,xx])))
