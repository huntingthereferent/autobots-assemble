import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# Visible top order: colors 9,14,11,15.
# Visible bottom positions by color: 14@19, 15@27, 9@35, 11@43.
path=[(35,58),(19,58),(43,58),(27,58)]
print("start levels",env.observation_space.levels_completed)
for i,(x,y) in enumerate(path,1):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    out=env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"visible_sequence","step":i})
    print("click",i,(x,y),"levels",out.levels_completed,"state",out.state)
out=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate_visible_sequence"})
print("after ACTION5 levels",out.levels_completed,"state",out.state,"win_levels",out.win_levels)
