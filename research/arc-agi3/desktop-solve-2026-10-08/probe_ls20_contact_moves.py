import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64)
def bbox_color(a,c):
 ys,xs=np.where(a==c)
 return None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()),len(xs))
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for act in [GameAction.ACTION3,GameAction.ACTION4,GameAction.ACTION2,GameAction.ACTION1]:
 env=arc.make("ls20")
 o=env.observation_space
 for _ in range(6): o=env.step(GameAction.ACTION1,data={},reasoning={"probe":"contact"})
 b=grid(o)
 o2=env.step(act,data={},reasoning={"probe":"from_contact"})
 a=grid(o2)
 ys,xs=np.where(a!=b)
 print(act.name,"levels",o2.levels_completed,"state",o2.state,
       "delta",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),
       "c12",bbox_color(a,12),"c9",bbox_color(a,9))
