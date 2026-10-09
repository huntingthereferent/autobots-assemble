import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program

def pair(env,p,s,label):
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"t":label})
    return env.step(GameAction.ACTION6,data={"x":s[0],"y":s[1]},reasoning={"t":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"t":"start"})

# L0-L2 generic
for _ in range(3):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    p,_=detect_program(a.reshape(64,64))
    for color,slot in zip(p["targets"],p["order"]):
        pair(env,p["tokens"][color],slot,"g")
    b=env.observation_space.levels_completed
    for _ in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"t":"go"})
        if o.levels_completed>b: break
# L3
for p,s in [((10,58),(19,22)),((31,58),(25,22)),((52,58),(31,22)),((45,58),(31,36)),((17,58),(37,36)),((24,58),(37,22)),((38,58),(43,22))]: pair(env,p,s,"l3")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g3"})
# L4
for p,s in [((13,58),(19,22)),((48,58),(25,22)),((55,58),(31,22)),((34,58),(37,22)),((6,58),(43,22)),((41,58),(25,36)),((20,58),(31,36)),((27,58),(37,36))]: pair(env,p,s,"l4")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g4"})
# L5
for p,s in [((52,58),(12,22)),((59,58),(18,22)),((45,58),(24,22)),((3,58),(18,36)),((24,58),(24,36)),((17,58),(44,36)),((38,58),(50,36)),((10,58),(44,22)),((31,58),(50,22))]: pair(env,p,s,"l5")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g5"})
# L6
for p,s in [((6,58),(25,16)),((55,58),(31,16)),((20,58),(37,16)),((13,58),(25,29)),((48,58),(31,29)),((34,58),(37,29)),((27,58),(25,42)),((41,58),(37,42))]: pair(env,p,s,"l6")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g6"})

print("level",env.observation_space.levels_completed)
# L7 mutual call hypothesis
ops=[
    ((27,58),(22,26),"f8_8"),
    ((13,58),(28,26),"f8_11"),
    ((20,58),(34,26),"f8_12"),
    ((54,57),(40,26),"f8_call9"),
    ((34,58),(22,40),"f9_9"),
    ((41,58),(28,40),"f9_14"),
    ((6,58),(34,40),"f9_15"),
    ((47,57),(40,40),"f9_call8"),
]
for p,s,label in ops:
    o=pair(env,p,s,label)
    print(label,o.levels_completed,o.state)
before=env.observation_space.levels_completed
for i in range(6):
    o=env.step(GameAction.ACTION5,data={},reasoning={"t":"g7"})
    print("go",i+1,o.levels_completed,o.state)
    if o.levels_completed>before or str(o.state).endswith("WIN"):
        break
