import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
choices=[(36,58),(20,58),(44,58),(28,58)]
for i,(x,y) in enumerate(choices,1):
 a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
 obs=env.step(a,data={"x":x,"y":y},reasoning={"t":"s"})
 b=GameAction.ACTION5
 obs=env.step(b,data={},reasoning={"t":"a5"})
 row=g(obs)[53,:]
 nz=[(j,int(v)) for j,v in enumerate(row) if int(v)!=2]
 print(i,nz,"levels",obs.levels_completed,"state",obs.state)
