from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# Divider is not plain: inspect holes and compare their 3-cell phase to embedded-dot rows.
for c in [10]:
 ys,xs=np.where(b==c)
 byrow={y:sorted(xs[ys==y].tolist()) for y in sorted(set(ys.tolist()))}
 print('divider rows 0..62')
 for y in range(63):
  xs=byrow.get(y,[])
  if len(xs)!=3: print('hole-row',y,xs)
# dot row phases
for c in [0,11]:
 ys,xs=np.where(b==c)
 pts=[(int(x),int(y)) for y,x in zip(ys,xs) if x<63]
 print('dots',c,pts,'y mod3',sorted(set(y%3 for x,y in pts)),'x mod3',sorted(set(x%3 for x,y in pts)))
