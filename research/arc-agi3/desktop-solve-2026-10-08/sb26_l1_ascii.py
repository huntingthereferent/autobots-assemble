from PIL import Image
import numpy as np
# Load saved level1 ARC image is scaled, so instead use live generation logic from prior script?
# Recreate level1 and print raw crop.
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
def click(x,y):
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    env.step(a,data={"x":x,"y":y},reasoning={"probe":"advance"})
p0={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}
for c,s in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    click(*p0[c]);click(*s)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
a=a.reshape(64,64)
chars="0123456789ABCDEF"
for y in range(14,44):
    print(f"{y:02d} "+"".join(chars[int(v)] for v in a[y,14:50]))
