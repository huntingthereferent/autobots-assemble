from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
base=[3]*5+[2]*10+[5]
# One layer above invariant: compare commuting square A_i then A5 vs A5 then A_i.
# If equal, A5 residual is independent. If not, the commutator is the distinction carried by the whole state.
for act in [1,2,3,4]:
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 o=e.step(GameAction.from_id(act),data={}); o=e.step(GameAction.ACTION5,data={}); x=o.frame[0].copy()
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 o=e.step(GameAction.ACTION5,data={}); o=e.step(GameAction.from_id(act),data={}); y=o.frame[0].copy()
 ys,xs=np.where(x!=y)
 print('A',act,'commutator',len(xs),'L',o.levels_completed,'bbox',None if len(xs)==0 else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
