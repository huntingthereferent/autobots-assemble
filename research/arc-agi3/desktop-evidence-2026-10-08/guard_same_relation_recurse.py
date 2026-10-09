from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# Continue only the returned states that remain non-fixed under the same permitted relation.
for act in [3,4,5]:
 e=a.make('ar25')
 for z in pre:o=e.step(GameAction.from_id(z),data={})
 prev=o.frame[0].copy()
 print("\nREL",act,"start",o.levels_completed)
 for n in range(1,65):
  o=e.step(GameAction.from_id(act),data={}); cur=o.frame[0].copy()
  diff=np.count_nonzero(prev!=cur)
  print(n,diff,o.levels_completed,o.state)
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state) or diff==0: break
  prev=cur
