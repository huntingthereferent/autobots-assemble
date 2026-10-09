import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

# Derived only from visible frame:
# top sequence colors = [9,14,11,15]
# bottom selectable centers by matching color:
steps=[(35,58),(19,58),(43,58),(27,58)]

for i,(x,y) in enumerate(steps,1):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    out=env.step(a,data=a.action_data.model_dump(),reasoning={"probe":"visible_relation_select","i":i})
    print("select",i,"levels",out.levels_completed,"state",out.state)
    out=env.step(GameAction.ACTION5,data={},reasoning={"probe":"visible_relation_submit","i":i})
    print("submit",i,"levels",out.levels_completed,"state",out.state,"win_levels",out.win_levels)
    if out.levels_completed>0 or "WIN" in str(out.state):
        break
