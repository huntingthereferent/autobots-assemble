import numpy as np, arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")

def getg():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).copy()

pts=[("left_player",21,51),("right_player",41,51),("center",31,51),("left_region",5,59),("right_region",58,59),("center_top",31,10)]
for label,x,y in pts:
    env.step(GameAction.RESET,data={},reasoning={"p":"r"})
    b=getg()
    o=env.step(GameAction.ACTION6,data={"x":x,"y":y},reasoning={"p":label})
    a=getg()
    ys,xs=np.where(b!=a)
    pairs={}
    for yy,xx in zip(ys,xs):
        pairs[(int(b[yy,xx]),int(a[yy,xx]))]=pairs.get((int(b[yy,xx]),int(a[yy,xx])),0)+1
    print(label,(x,y),"n",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),"pairs",pairs,"level",o.levels_completed,"state",o.state)
