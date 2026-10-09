import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
seq=[(9,(36,58)),(14,(20,58)),(11,(44,58)),(15,(28,58))]
print("start",obs.levels_completed,obs.state)
for i,(color,(x,y)) in enumerate(seq,1):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    obs=env.step(a,data={"x":x,"y":y},reasoning={"hypothesis":"select visible target token","step":i,"color":color})
    print("select",i,color,"levels",obs.levels_completed,"state",obs.state)
    b=GameAction.ACTION5
    obs=env.step(b,data={},reasoning={"hypothesis":"commit selected token","step":i,"color":color})
    print("commit",i,color,"levels",obs.levels_completed,"win_levels",obs.win_levels,"state",obs.state)
    if obs.levels_completed>0:
        break
