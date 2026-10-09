import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
def click(env,xy):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"verify"})
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
print("start",env.observation_space.levels_completed)
for s,t in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,s);click(env,t)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
print("after",o.levels_completed,o.state)
