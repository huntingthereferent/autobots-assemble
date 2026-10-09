from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
e=a.make('ar25')
for z in pre:o=e.step(GameAction.from_id(z),data={})
x=o.frame[0].copy()
print("x0",o.levels_completed,o.state)
# Same W, no inserted representation: evaluate each permitted relation directly from exact x0.
# A movement is carried only if its returned state itself witnesses continuation by exact recurrence.
for act in [1,2,3,4,5,7]:
 ee=a.make('ar25')
 for z in pre: oo=ee.step(GameAction.from_id(z),data={})
 b0=oo.frame[0].copy()
 b1=ee.step(GameAction.from_id(act),data={}).frame[0].copy()
 o2=ee.step(GameAction.from_id(act),data={}); b2=o2.frame[0].copy()
 print("A",act,"d01",np.count_nonzero(b0!=b1),"d12",np.count_nonzero(b1!=b2),
       "fixed_after_return",np.array_equal(b1,b2),"lvl",o2.levels_completed,o2.state)
