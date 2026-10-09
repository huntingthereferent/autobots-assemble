import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import perceive,effect,grid

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("vc33")
s=perceive(env.observation_space)
print("AVAILABLE",env.observation_space.available_actions)
print("SMALL OBJECTS")
cands=[]
for i,o in enumerate(s.objects):
    if o.size<=128:
        xy=(o.center2[0]//2,o.center2[1]//2)
        print(i,"color",o.color,"size",o.size,"box",(o.x0,o.y0,o.x1,o.y1),"xy",xy)
        cands.append((i,xy,o))
print("CENSUS")
for i,(x,y),o in cands:
    env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
    before=env.observation_space
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    after=env.step(a,data={"x":x,"y":y},reasoning={"probe":"component_census"})
    e=effect(before,after)
    print(i,(x,y),"c",o.color,"n",o.size,"=>",e.class_name,e.changed_pixels,e.bbox,"level",after.levels_completed,"state",after.state)
