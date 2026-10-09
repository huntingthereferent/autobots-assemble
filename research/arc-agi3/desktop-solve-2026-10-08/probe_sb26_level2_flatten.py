import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"p":"r"})
# level 0 from visible target
for color,slot in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    p={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"sel0"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"asg0"})
env.step(GameAction.ACTION5,data={},reasoning={"p":"go0"})
print("level",env.observation_space.levels_completed)

target=[12,15,8,9,14,11,6]
tokens={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
order=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
for color,slot in zip(target,order):
    p=tokens[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"sel1"})
    o=env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"asg1"})
    print("assign",color,slot,"lvl",o.levels_completed)
print("before advance",env.observation_space.levels_completed)
for i in range(3):
    o=env.step(GameAction.ACTION5,data={},reasoning={"p":"go1"})
    print("advance",i+1,o.levels_completed,o.state)
    if o.levels_completed>=2:
        break
