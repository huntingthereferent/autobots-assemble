import numpy as np
import arc_agi
from arc_agi import OperationMode
from latent import objects

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64)
for o in sorted(objects(g), key=lambda z:(z.y0,z.x0,z.color,z.size)):
    if o.size<=400:
        print({"color":o.color,"size":o.size,"box":(o.x0,o.y0,o.x1,o.y1),"center":(o.cx2/2,o.cy2/2)})
