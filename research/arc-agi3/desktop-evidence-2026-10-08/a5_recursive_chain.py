from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
prev=o.frame[0].copy()
# Same operation recursively, no intervening choice. Record change and whether level closes.
for n in range(1,16):
 o=e.step(GameAction.ACTION5,data={})
 cur=o.frame[0].copy()
 print(n,'changed',np.count_nonzero(prev!=cur),'L',o.levels_completed,'state',o.state)
 # whole-state equality against prior impossible after overwrite; record divider bbox
 ys,xs=np.where(cur==10)
 print(' divider', (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max()),len(xs)) if len(xs) else None)
 prev=cur
 if o.levels_completed>1 or str(o.state).endswith('GAME_OVER'): break
