import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
print("start",obs.levels_completed,obs.state,obs.available_actions)

# Derived solely from visible initial frame:
# top sequence colors: 9,14,11,15
# matching bottom token centers: 9@(36,58),14@(20,58),11@(44,58),15@(28,58)
for color,(x,y) in [(9,(36,58)),(14,(20,58)),(11,(44,58)),(15,(28,58))]:
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    obs=env.step(a,data={"x":x,"y":y},reasoning={"hypothesis":"match visible top sequence","color":color})
    print("click",color,"levels",obs.levels_completed,"state",obs.state)
a=GameAction.ACTION5
obs=env.step(a,data={},reasoning={"hypothesis":"evaluate visible sequence match"})
print("evaluate","levels",obs.levels_completed,"win_levels",obs.win_levels,"state",obs.state)
