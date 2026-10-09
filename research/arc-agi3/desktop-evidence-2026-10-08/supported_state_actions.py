from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
# A5 once creates the evidence-bearing board. Test the simple permitted actions from exactly this board,
# recording whether they act on the supported L/vertical relation and whether the level closes.
base=[3]*5+[2]*10+[5]
for act in [1,2,3,4,7]:
 ee=a.make('ar25')
 for i in base: oo=ee.step(GameAction.from_id(i),data={})
 p=oo.frame[0].copy(); oo=ee.step(GameAction.from_id(act),data={}); q=oo.frame[0]
 ys,xs=np.where(p!=q)
 print('A',act,'changed',len(xs),'L',oo.levels_completed,'state',oo.state,
       'bbox',None if len(xs)==0 else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
