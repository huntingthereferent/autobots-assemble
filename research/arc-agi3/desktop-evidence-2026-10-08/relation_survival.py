from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
base=[3]*5+[2]*10+[5]
# Measure which action preserves the recursively exposed 3-lattice relation:
# after each candidate, A5 again; smallest recursive residual is the supported continuation.
for act in [1,2,3,4]:
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 o=e.step(GameAction.from_id(act),data={}); p=o.frame[0].copy()
 o=e.step(GameAction.ACTION5,data={}); q=o.frame[0].copy()
 print('A',act,'then A5 residual',np.count_nonzero(p!=q),'L',o.levels_completed,'state',o.state)
