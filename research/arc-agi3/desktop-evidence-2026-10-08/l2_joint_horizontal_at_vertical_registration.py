from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
# At vertical registration after A2x8, inspect joint horizontal action:
# Level1 had paired objects on opposite sides divider; L2 actions move yellow and gray/black oppositely horizontally.
# Track yellow vs navy AND gray+black relative to any left/right counterpart after each horizontal step.
for hact in [3,4]:
 e=a.make('ar25');o=None
 for z in BASE+[2]*8:o=e.step(GameAction.from_id(z),data={})
 print('\nH',hact)
 for k in range(1,11):
  o=e.step(GameAction.from_id(hact),data={});A=o.frame[0];Y,X=np.indices(A.shape)
  def box(mask):
   yy,xx=np.where(mask)
   return None if not len(xx) else (int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),len(xx))
  print(k,'lvl',o.levels_completed,'Y',box((A==4)&(X<36)),'K',box(A==0),'Gright',box((A==5)&(X>38)&(Y<63)),'Nleft',box((A==11)&(X<36)),o.state)
  if o.levels_completed>1: print('SOLVED',hact,k);break
