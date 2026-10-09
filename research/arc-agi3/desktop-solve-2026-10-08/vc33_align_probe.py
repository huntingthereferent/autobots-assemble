import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import perceive

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("vc33")

def click(x,y,label):
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    o=env.step(a,data={"x":x,"y":y},reasoning={"probe":label})
    print(label,"levels",o.levels_completed,"state",o.state)
    for ob in perceive(o).objects:
        if ob.color in (4,11) and ob.y0>=40:
            print("  sprite",ob.color,ob.size,(ob.x0,ob.y0,ob.x1,ob.y1))
    return o

for i in range(1,5):
    o=click(61,33,f"left_{i}")
    if o.levels_completed>0: break
