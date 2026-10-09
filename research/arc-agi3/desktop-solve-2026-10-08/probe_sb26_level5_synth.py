import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program

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
        env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":"select"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"t":"assign"})
    before=env.observation_space.levels_completed
    for _ in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"t":"advance"})
        if o.levels_completed>before: break

# level 3
term={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58)}
ops=[(term[11],(19,22)),(term[8],(25,22)),((52,58),(31,22)),(term[9],(31,36)),(term[6],(37,36)),(term[12],(37,22)),(term[15],(43,22))]
for q,s in ops:
    env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":"s3"})
    env.step(GameAction.ACTION6,data={"x":s[0],"y":s[1]},reasoning={"t":"a3"})
env.step(GameAction.ACTION5,data={},reasoning={"t":"g3"})

print("level",env.observation_space.levels_completed)
# level 4: child9=[14,8,8], parent=[6,C9,C9,11,15]
ops=[
    ((13,58),(19,22),"p1=6"),
    ((48,58),(25,22),"p2=c9"),
    ((55,58),(31,22),"p3=c9"),
    ((34,58),(37,22),"p4=11"),
    ((6,58),(43,22),"p5=15"),
    ((41,58),(25,36),"c1=14"),
    ((20,58),(31,36),"c2=8"),
    ((27,58),(37,36),"c3=8"),
]
for q,s,label in ops:
    env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":label})
    o=env.step(GameAction.ACTION6,data={"x":s[0],"y":s[1]},reasoning={"t":label})
    print(label,o.levels_completed)
before=env.observation_space.levels_completed
for i in range(4):
    o=env.step(GameAction.ACTION5,data={},reasoning={"t":"g4"})
    print("go",i+1,o.levels_completed,o.state)
    if o.levels_completed>before: break
