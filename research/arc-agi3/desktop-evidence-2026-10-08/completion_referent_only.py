from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
def get(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0].copy(),o
# ONLY completion referent: compare every pre-step in solved L1 and isolate what is unique at closing step.
seq=[3]*5+[2]*10
e=a.make('ar25'); states=[]; obs=[]
# initial frame via first? capture returned states after actions and compare final A2 against earlier A2s.
for i,z in enumerate(seq):
 before = obs[-1].frame[0].copy() if obs else None
 o=e.step(GameAction.from_id(z),data={}); obs.append(o)
 if z==2:
  B=o.frame[0]
  # locate 5 black cells and 5 yellow? print bboxes/colors and pairwise geometry
  y0,x0=np.where(B==0); y4,x4=np.where(B==4)
  print("A2#",sum(1 for q in seq[:i+1] if q==2),"idx",i+1,"lvl",o.levels_completed,
        "blackbbox",(x0.min(),x0.max(),y0.min(),y0.max()) if len(x0) else None,
        "yellowbbox",(x4.min(),x4.max(),y4.min(),y4.max()) if len(x4) else None,
        "black",list(zip(x0.tolist(),y0.tolist())))
