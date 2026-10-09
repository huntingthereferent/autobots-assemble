import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def arr(env):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"p":"r"})
for color,slot in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    pos={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}[color]
    env.step(GameAction.ACTION6,data={"x":pos[0],"y":pos[1]},reasoning={"p":"s"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"a"})
env.step(GameAction.ACTION5,data={},reasoning={"p":"n"})
g=arr(env)
print("level",env.observation_space.levels_completed)
for y in range(15,44):
    print(f"{y:02d}","".join(format(int(v),"x") for v in g[y,14:50]))
