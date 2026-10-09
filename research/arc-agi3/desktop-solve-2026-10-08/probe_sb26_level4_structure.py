import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program, connected_components

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"t":"start"})
# generic first 3
for _ in range(3):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    p,_=detect_program(a.reshape(64,64))
    for color,slot in zip(p["targets"],p["order"]):
        q=p["tokens"][color]
        env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":"s"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"t":"a"})
    b=env.observation_space.levels_completed
    for i in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"t":"g"})
        if o.levels_completed>b: break
# level 3 synth
root=[(19,22),(25,22),(31,22),(37,22),(43,22)]
term={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58)}
ops=[(term[11],root[0]),(term[8],root[1]),((52,58),root[2]),(term[9],(31,36)),(term[6],(37,36)),(term[12],root[3]),(term[15],root[4])]
for q,s in ops:
    env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":"s3"})
    env.step(GameAction.ACTION6,data={"x":s[0],"y":s[1]},reasoning={"t":"a3"})
env.step(GameAction.ACTION5,data={},reasoning={"t":"g3"})

a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64)
print("LEVEL",env.observation_space.levels_completed)
for q in sorted(connected_components(g),key=lambda z:(z["y0"],z["x0"],z["color"],z["size"])):
    if 1<q["size"]<420:
        print(q)
print("MID")
for y in range(10,51):
    print(f"{y:02d}","".join(format(int(v),"x") for v in g[y,4:60]))
