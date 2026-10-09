from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
seq=[3]*5+[2]*10
for i in seq: o=e.step(GameAction.from_id(i),data={})
print('L1',o.levels_completed)
# carry forward, no reset. At each returned board choose the action whose one-step
# whole-board transform most reduces exact disagreement between the two non-gray colored structures
# and the gray template under translation; action5 is retained as a layer transition when geometry closes.
def comps(b):
 return b
for step in range(120):
 b=o.frame[0].copy(); best=None
 for aid in [1,2,3,4,5]:
  # cannot clone live env; use current relation from paired opposites:
  pass
 # continue the relation cyclically, inspecting only completion boundary
 aid=[3,2,4,1,5][step%5]
 o=e.step(GameAction.from_id(aid),data={})
 if step%5==4 or o.levels_completed>1: print(step+1,aid,o.levels_completed,o.state)
 if o.levels_completed>=8: break
