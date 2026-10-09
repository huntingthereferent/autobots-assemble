import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import effect

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
pal=[("teal",(19,58)),("orange",(27,58)),("maroon",(35,58)),("white",(43,58))]
slots=[(22,29),(28,29),(34,29),(40,29)]

def click(x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    before=env.observation_space
    after=env.step(a,data={"x":x,"y":y},reasoning={"probe":label})
    e=effect(before,after)
    return after,e

for name,p in pal:
    for si,s in enumerate(slots):
        env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
        _,e1=click(*p,"select_palette")
        after,e2=click(*s,"edit_slot")
        print(name,"slot",si,"select",e1.class_name,e1.changed_pixels,e1.bbox,e1.color_delta,
              "then",e2.class_name,e2.changed_pixels,e2.bbox,e2.color_delta,
              "levels",after.levels_completed)
