import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def g():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).copy()

def step(action,data,label):
    b=g()
    o=env.step(action,data=data,reasoning={"probe":label})
    a=g()
    ys,xs=np.where(b!=a)
    ch=[(int(x),int(y),int(b[y,x]),int(a[y,x])) for y,x in zip(ys,xs)]
    print(label,"n",len(ch),"bbox",None if not len(xs) else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),"levels",o.levels_completed)
    print(ch[:80])

env.step(GameAction.RESET,data={},reasoning={"probe":"r"})
step(GameAction.ACTION6,{"x":35,"y":58},"select_bottom_9")
step(GameAction.ACTION6,{"x":22,"y":29},"click_middle_1")
step(GameAction.ACTION6,{"x":28,"y":29},"click_middle_2")
step(GameAction.ACTION5,{},"execute_once")
