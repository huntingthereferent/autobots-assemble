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

# solve first 3 generic
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
for p,s in [
    ((10,58),(19,22)),((31,58),(25,22)),((52,58),(31,22)),
    ((45,58),(31,36)),((17,58),(37,36)),((24,58),(37,22)),((38,58),(43,22))
]:
    pair(env,p,s,"l3")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g3"})
# L4
for p,s in [
    ((13,58),(19,22)),((48,58),(25,22)),((55,58),(31,22)),((34,58),(37,22)),((6,58),(43,22)),
    ((41,58),(25,36)),((20,58),(31,36)),((27,58),(37,36))
]:
    pair(env,p,s,"l4")
env.step(GameAction.ACTION5,data={},reasoning={"t":"g4"})

print("level",env.observation_space.levels_completed)
# L5 grammar
ops=[
    ((52,58),(12,22),"root_call9"),
    ((59,58),(18,22),"root_call12"),
    ((45,58),(24,22),"root_call14"),
    ((3,58),(18,36),"f9_11a"),
    ((24,58),(24,36),"f9_11b"),
    ((17,58),(44,36),"f12_15a"),
    ((38,58),(50,36),"f12_15b"),
    ((10,58),(44,22),"f14_6a"),
    ((31,58),(50,22),"f14_6b"),
]
for p,s,label in ops:
    o=pair(env,p,s,label)
    print(label,o.levels_completed)
before=env.observation_space.levels_completed
for i in range(4):
    o=env.step(GameAction.ACTION5,data={},reasoning={"t":"g5"})
    print("go",i+1,o.levels_completed,o.state)
    if o.levels_completed>before: break
