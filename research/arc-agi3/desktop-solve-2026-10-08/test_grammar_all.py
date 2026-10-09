import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from grammar import solve_visible_program

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"test":"fresh"})

total=0
for step in range(10):
    lvl=env.observation_space.levels_completed
    if str(env.observation_space.state).endswith("WIN"):
        break
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    g=a.reshape(64,64)
    plan,why=solve_visible_program(g)
    print("LEVEL",lvl,"MODE",None if plan is None else plan.get("mode"),"WHY",why)
    if plan is None:
        break
    print("TARGET",plan.get("target"))
    print("EXPANSION",plan.get("expansion"))
    print("PAIRS",plan["click_pairs"])
    for sel,slot in plan["click_pairs"]:
        env.step(GameAction.ACTION6,data={"x":sel[0],"y":sel[1]},reasoning={"test":"select"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"test":"assign"})
        total+=2
    before=env.observation_space.levels_completed
    o=env.step(GameAction.ACTION5,data={},reasoning={"test":"execute"})
    total+=1
    print("AFTER",o.levels_completed,o.state,"ACTIONS",total)
    if o.levels_completed==before and not str(o.state).endswith("WIN"):
        break

print("FINAL",env.observation_space.levels_completed,env.observation_space.state,"TOTAL",total)
