import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def getg():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:
        a=a[-1]
    return a.reshape(64,64).copy()

def do_click(x,y,label):
    before=getg()
    out=env.step(GameAction.ACTION6,data={"x":x,"y":y},reasoning={"probe":label})
    after=getg()
    ys,xs=np.where(before!=after)
    print(label,"n",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),"levels",out.levels_completed)
    if len(xs):
        print([(int(xx),int(yy),int(before[yy,xx]),int(after[yy,xx])) for yy,xx in zip(ys[:24],xs[:24])])

env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
for i in range(4):
    do_click(43,58,"same"+str(i+1))

env.step(GameAction.RESET,data={},reasoning={"probe":"reset2"})
for i,(x,y) in enumerate([(43,58),(35,58),(27,58),(19,58)]):
    do_click(x,y,"slot"+str(i+1))
