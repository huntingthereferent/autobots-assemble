from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10+[5]: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
for c in sorted(np.unique(b)):
 print('\nC',int(c))
 for y in range(64):
  xs=np.where(b[y]==c)[0]
  if len(xs) and c not in [9]:
   print(y,[(int(g[0]),int(g[-1])) for g in np.split(xs,np.where(np.diff(xs)>1)[0]+1)])
