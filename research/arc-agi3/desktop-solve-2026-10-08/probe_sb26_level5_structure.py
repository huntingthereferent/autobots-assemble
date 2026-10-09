import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program, connected_components

def clickpair(env,p,s,label):
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"t":label})
    env.step(GameAction.ACTION6,data={"x":s[0],"y":s[1]},reasoning={"t":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"t":"start"})

# L0-L2 generic
for _ in range(3):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    p,_=detect_program(a.reshape(64,64))
    for color,slot in zip(p["targets"],p["order"]):
        clickpair(env,p["tokens"][color],slot,"generic")
    b=env.observation_space.levels_completed
    for i in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"t":"go"})
        if o.levels_completed>b: break

# L3
for p,s in [
    ((10,58),(19,22)),((31,58),(25,22)),((52,58),(31,22)),
    ((45,58),(31,36)),((17,58),(37,36)),((24,58),(37,22)),((38,58),(43,22))
]:
    clickpair(env,p,s,"l3")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g3"})

# L4
for p,s in [
    ((13,58),(19,22)),((48,58),(25,22)),((55,58),(31,22)),
    ((34,58),(37,22)),((6,58),(43,22)),
    ((41,58),(25,36)),((20,58),(31,36)),((27,58),(37,36))
]:
    clickpair(env,p,s,"l4")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g4"})

a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64)
print("LEVEL",env.observation_space.levels_completed)
for q in sorted(connected_components(g),key=lambda z:(z["y0"],z["x0"],z["color"],z["size"])):
    if 1<q["size"]<500:
        print(q)
print("MID")
for y in range(8,52):
    print(f"{y:02d}","".join(format(int(v),"x") for v in g[y,2:62]))
