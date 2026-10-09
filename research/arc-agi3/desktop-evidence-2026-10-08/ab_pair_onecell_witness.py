from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
base=([3]*13+[4]*21)*2+[7]*59
# Pair return changes one cell: inspect that exact carried witness, not a semantic label.
e=a.make('ar25')
for z in pre+base:o=e.step(GameAction.from_id(z),data={})
prev=o.frame[0].copy()
for n in range(1,6):
 for z in [3,7]: o=e.step(GameAction.from_id(z),data={})
 cur=o.frame[0].copy()
 ys,xs=np.where(prev!=cur)
 print("pair",n,"coords",[(int(x),int(y),int(prev[y,x]),int(cur[y,x])) for y,x in zip(ys,xs)])
 prev=cur
