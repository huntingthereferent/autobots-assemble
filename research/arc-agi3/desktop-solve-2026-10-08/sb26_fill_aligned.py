import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# top colors by x: 9,14,11,15
# bottom palette centers by color
pal={14:(20,58),15:(28,58),9:(36,58),11:(44,58)}
slots=[(22,29),(28,29),(34,29),(40,29)]
target=[9,14,11,15]
obs=env.observation_space
print("start",obs.levels_completed,obs.state)
for i,(color,slot) in enumerate(zip(target,slots),1):
    x,y=pal[color]
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    obs=env.step(a,data={"x":x,"y":y},reasoning={"hyp":"select palette symbol","i":i,"color":color})
    b=GameAction.ACTION6;b.set_data({"x":slot[0],"y":slot[1]})
    obs=env.step(b,data={"x":slot[0],"y":slot[1]},reasoning={"hyp":"write aligned middle slot","i":i,"color":color})
    print(i,color,"levels",obs.levels_completed,"win_levels",obs.win_levels,"state",obs.state)
