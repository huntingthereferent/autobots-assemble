from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# Print exact occupied rows/cols excluding fixed borders/divider, preserving color relation.
for c in [0,4,5,11]:
 ys,xs=np.where(b==c)
 pts=[(int(x),int(y)) for y,x in zip(ys,xs) if x<63 and y<63 and not (35<=x<=39)]
 if not pts: continue
 print('C',c,'n',len(pts),'bbox',min(x for x,y in pts),max(x for x,y in pts),min(y for x,y in pts),max(y for x,y in pts))
 print(pts)
