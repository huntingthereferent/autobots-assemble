from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
seq=[3]*5+[2]*10
frames=[]
for i in seq:
 o=e.step(GameAction.from_id(i),data={}); frames.append(o.frame[0].copy())
# Compare final two states of earned L1 transition: what exact relation changed at closure?
for k in [13,14]:
 b=frames[k]
 print('STATE',k+1,'level', 'pre' if k==13 else 'closure')
 for c in [0,4,5,11]:
  ys,xs=np.where(b==c); pts=[(int(x),int(y)) for y,x in zip(ys,xs) if x<63 and y<63 and not (29<=x<=33)]
  if pts: print(c,len(pts),(min(x for x,y in pts),max(x for x,y in pts),min(y for x,y in pts),max(y for x,y in pts)))
 print()
