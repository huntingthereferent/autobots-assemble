from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
# LOOK UP: use the already-earned initial witness A1=upward relation, from the exact returned L2 board.
# Recurse upward directly and audit returned whole boards / closure boundary.
e=a.make('ar25')
for i in solve:o=e.step(GameAction.from_id(i),data={})
prev=o.frame[0].copy()
print('root L',o.levels_completed,o.state)
for n in range(1,30):
 o=e.step(GameAction.ACTION1,data={})
 if not o.frame:
  print('UP',n,'NOFRAME','L',o.levels_completed,o.state);break
 b=o.frame[0].copy();ys,xs=np.where(prev!=b)
 print('UP',n,'diff',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),'L',o.levels_completed,o.state)
 if o.levels_completed>1 or 'GAME_OVER' in str(o.state):break
 prev=b
