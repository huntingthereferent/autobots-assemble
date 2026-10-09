import numpy as np
from collections import Counter
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def click(env,x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"probe":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
bottom=[("B14",19,58),("B15",27,58),("B9",35,58),("B11",43,58)]
middle=[("M0",22,29),("M1",28,29),("M2",34,29),("M3",40,29)]
for bn,bx,by in bottom:
    for mn,mx,my in middle:
        env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
        click(env,bx,by,"select")
        before=grid(env.observation_space)
        out=click(env,mx,my,"middle")
        after=grid(out)
        ys,xs=np.where(before!=after)
        changes=Counter((int(before[y,x]),int(after[y,x])) for y,x in zip(ys,xs))
        bbox=None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
        print(bn,mn,"changed",len(xs),"bbox",bbox,"pairs",dict(changes),"level",out.levels_completed)
