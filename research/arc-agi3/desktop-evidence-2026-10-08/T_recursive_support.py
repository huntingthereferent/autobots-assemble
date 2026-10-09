from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
# Now T is earned equivalence class {12,21,34,43,55}. Ask what survives if T is
# recursively applied to the returned state: exact changed support and transition.
e=a.make('ar25')
for i in base:o=e.step(GameAction.from_id(i),data={})
prev=o.frame[0].copy()
for n in range(1,32):
 for i in [5,5]:o=e.step(GameAction.from_id(i),data={})
 cur=o.frame[0];ys,xs=np.where(prev!=cur)
 trans={}
 for y,x in zip(ys,xs):
  k=(int(prev[y,x]),int(cur[y,x]));trans[k]=trans.get(k,0)+1
 print(n,'stepdiff',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),'trans',trans,'L',o.levels_completed)
 prev=cur.copy()
