from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
# Continue the earned higher-order operation P=(1,2) until boundary relation closes/changes.
e=a.make('ar25')
for i in base:o=e.step(GameAction.from_id(i),data={})
root=o.frame[0].copy()
for n in range(1,40):
 for i in [1,2]: o=e.step(GameAction.from_id(i),data={})
 cur=o.frame[0]
 ys,xs=np.where(root!=cur)
 # right edge gray/navy split
 edge=cur[:,63]
 gray=np.where(edge==5)[0]; navy=np.where(edge==11)[0]
 print(n,'actions',2*n,'diff',len(xs),'L',o.levels_completed,'state',o.state,
       'grayEdge', (int(gray.min()),int(gray.max()),len(gray)) if len(gray) else None,
       'navyEdge',(int(navy.min()),int(navy.max()),len(navy)) if len(navy) else None)
 if o.levels_completed>1 or 'GAME_OVER' in str(o.state): break
