import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,xy):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"loopcheck"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
print("initial",env.observation_space.levels_completed,env.observation_space.state)
r=env.step(GameAction.RESET,data={},reasoning={"probe":"first reset"})
print("reset",r.levels_completed,r.state)
for i,(s,t) in enumerate([((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]):
    a=click(env,s);b=click(env,t)
    print("pair",i,a.levels_completed,b.levels_completed,b.state)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
print("after eval",o.levels_completed,o.state)
