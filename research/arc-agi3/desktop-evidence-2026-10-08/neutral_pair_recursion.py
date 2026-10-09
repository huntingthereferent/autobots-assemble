from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
# Opposite compositions commute and leave exactly 2 cells changed. Locate them and see whether repeating
# the neutral pair recursively accumulates toward closure.
for pair in ([1,2],[3,4]):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 root=o.frame[0].copy()
 print('PAIR',pair)
 for n in range(1,13):
  for i in pair:o=e.step(GameAction.from_id(i),data={})
  cur=o.frame[0]; ys,xs=np.where(root!=cur)
  pts=[(int(x),int(y),int(root[y,x]),int(cur[y,x])) for y,x in zip(ys,xs)]
  print(n,'diff',len(xs),'L',o.levels_completed,'state',o.state,'pts',pts[:12])
  if o.levels_completed>1 or str(o.state).endswith('GAME_OVER'): break
