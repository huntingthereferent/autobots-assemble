import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,xy,why):
    a=GameAction.ACTION6; a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})

def solve_l0(env):
    for s,d in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
        click(env,s,"L0");click(env,d,"L0")
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":"L0 eval"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for label in ["no reset","with reset"]:
    if label=="with reset":
        env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    o=solve_l0(env)
    print(label,o.levels_completed,o.state)
    if label=="no reset":
        env=arc.make("sb26")
