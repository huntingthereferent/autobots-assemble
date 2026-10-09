import numpy as np, arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")
env.step(GameAction.RESET,data={},reasoning={"p":"r"})
a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
b=a.reshape(64,64).copy()
o=env.step(GameAction.ACTION4,data={},reasoning={"p":"a4"})
a=np.asarray(o.frame)
if a.ndim==3:a=a[-1]
c=a.reshape(64,64)
ys,xs=np.where(b!=c)
pairs={}
for y,x in zip(ys,xs):
    pairs[(int(b[y,x]),int(c[y,x]))]=pairs.get((int(b[y,x]),int(c[y,x])),0)+1
print("transitions",pairs)
for yy in range(48,55):
    print(yy,"before"," ".join(f"{int(v):02d}" for v in b[yy,14:49]))
    print(yy,"after "," ".join(f"{int(v):02d}" for v in c[yy,14:49]))
