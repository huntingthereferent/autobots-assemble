from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10+[5]: o=e.step(GameAction.from_id(i),data={})
def sig(b):
 out=[]
 for c in [0,4,5,10,11]:
  y,x=np.where(b==c)
  out.append((c,len(x),None if not len(x) else (int(x.min()),int(x.max()),int(y.min()),int(y.max()))))
 return out
print('BASE',o.levels_completed,sig(o.frame[0]))
for aid in [1,2,3,4]:
 e2=a.make('ar25')
 for i in [3]*5+[2]*10+[5]: z=e2.step(GameAction.from_id(i),data={})
 z=e2.step(GameAction.from_id(aid),data={})
 print('A',aid,z.levels_completed,sig(z.frame[0]))
