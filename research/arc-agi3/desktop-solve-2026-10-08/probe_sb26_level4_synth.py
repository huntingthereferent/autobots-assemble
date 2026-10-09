import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"t":"start"})
# use generic parser for first 3 levels
for _ in range(3):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    p,w=detect_program(a.reshape(64,64))
    for color,slot in zip(p["targets"],p["order"]):
        q=p["tokens"][color]
        env.step(GameAction.ACTION6,data={"x":q[0],"y":q[1]},reasoning={"t":"select"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"t":"assign"})
    before=env.observation_space.levels_completed
    for i in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"t":"advance"})
        if o.levels_completed>before: break

print("level",env.observation_space.levels_completed)
root=[(19,22),(25,22),(31,22),(37,22),(43,22)]
term={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58)}
call14=(52,58)
assign=[
    (term[11],root[0],"p1=11"),
    (term[8],root[1],"p2=8"),
    (call14,root[2],"p3=call14"),
    (term[9],(31,36),"child2=9"),
    (term[6],(37,36),"child3=6"),
    (term[12],root[3],"p4=12"),
    (term[15],root[4],"p5=15"),
]
for sel,slot,label in assign:
    env.step(GameAction.ACTION6,data={"x":sel[0],"y":sel[1]},reasoning={"t":label})
    o=env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"t":label})
    print(label,"level",o.levels_completed)
before=env.observation_space.levels_completed
for i in range(4):
    o=env.step(GameAction.ACTION5,data={},reasoning={"t":"advance3"})
    print("go",i+1,o.levels_completed,o.state)
    if o.levels_completed>before: break
