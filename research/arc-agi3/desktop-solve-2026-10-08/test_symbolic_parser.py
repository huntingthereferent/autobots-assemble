import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from symbolic import detect_program

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"test":"start"})

for loop in range(6):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    g=a.reshape(64,64)
    plan,why=detect_program(g)
    print("LEVEL",env.observation_space.levels_completed,"PLAN",plan,"WHY",why)
    if plan is None:
        break
    before=env.observation_space.levels_completed
    for color,slot in zip(plan["targets"],plan["order"]):
        p=plan["tokens"][color]
        env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"test":"select"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"test":"assign"})
    for i in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"test":"advance"})
        if o.levels_completed>before or str(o.state).endswith("WIN"):
            break
    print("AFTER",env.observation_space.levels_completed,env.observation_space.state)
    if env.observation_space.levels_completed==before:
        break
