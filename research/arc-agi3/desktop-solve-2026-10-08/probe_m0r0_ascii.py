import numpy as np, arc_agi
from arc_agi import OperationMode
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")
a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64)
chars={5:"#",10:"P",11:".",12:" "}
for y in range(35,64):
    print(f"{y:02d}", "".join(chars.get(int(v),"?") for v in g[y]))
