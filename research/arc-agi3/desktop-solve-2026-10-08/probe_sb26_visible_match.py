import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    out=env.step(a,data={"x":x,"y":y},reasoning={"probe":label})
    print(label,"levels",out.levels_completed,"state",out.state)
    return out

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# Visible relation:
# target top order = [9,14,11,15]
# bottom token locations initially: 14@19,58 15@27,58 9@35,58 11@43,58
# middle slots: x 22,28,34,40 y29
for sx,sy,tx,ty,label in [
    (35,58,22,29,"place9"),
    (19,58,28,29,"place14"),
    (43,58,34,29,"place11"),
    (27,58,40,29,"place15"),
]:
    click(env,sx,sy,label+"_select")
    click(env,tx,ty,label+"_slot")
out=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate_visible_match"})
print("EVAL","levels",out.levels_completed,"state",out.state)
