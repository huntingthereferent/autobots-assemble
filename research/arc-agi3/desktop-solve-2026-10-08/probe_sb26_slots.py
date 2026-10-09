import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
pts=[(43,58),(35,58),(27,58),(19,58)]

def g():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).copy()

def showbox(a,x0,x1,y0=54,y1=63):
    return ["".join(format(int(v),"x") for v in a[y,x0:x1+1]) for y in range(y0,y1+1)]

def step(act,data=None,label=""):
    before=g()
    out=env.step(act,data=data or {},reasoning={"probe":label})
    after=g()
    ys,xs=np.where(before!=after)
    changes=[(int(x),int(y),int(before[y,x]),int(after[y,x])) for y,x in zip(ys,xs)]
    print(label,"action",act.name,"n",len(changes),"bbox",None if not len(xs) else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),"levels",out.levels_completed,"state",out.state)
    print(" changes",changes[:40])
    return after

print("=== repeated same control ===")
env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
for i in range(5):
    a=step(GameAction.ACTION6,{"x":43,"y":58},f"same_{i+1}")
    print("box",showbox(a,40,47))

print("=== four controls sequentially ===")
env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
for i,(x,y) in enumerate(pts):
    a=step(GameAction.ACTION6,{"x":x,"y":y},f"slot_{i}")
print("allboxes",showbox(a,16,47))

print("=== commit after four ===")
step(GameAction.ACTION5,{}, "commit_after_four")

print("=== undo ===")
step(GameAction.ACTION7,{}, "undo_after_commit")
