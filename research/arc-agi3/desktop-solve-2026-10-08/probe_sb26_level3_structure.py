import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program, connected_components

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"t":"start"})
for _ in range(3):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    g=a.reshape(64,64)
    p,w=detect_program(g)
    for color,slot in zip(p["targets"],p["order"]):
        q=p["tokens"][color]
        env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":"s"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"t":"a"})
    before=env.observation_space.levels_completed
    for i in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"t":"g"})
        if o.levels_completed>before: break

a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64)
print("LEVEL",env.observation_space.levels_completed)
for q in sorted(connected_components(g),key=lambda z:(z["y0"],z["x0"],z["color"],z["size"])):
    if 1<q["size"]<350:
        print(q)
print("MID")
for y in range(10,50):
    print(f"{y:02d}","".join(format(int(v),"x") for v in g[y,8:56]))
