from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
# L1 closure moved BOTH left gray+black and right yellow down 3 into same y45..53 envelope.
# In L2 B8: yellow at left-middle, gray+black at right-middle, navy receiver left-bottom.
# Test vertical descent of the PAIRED middle objects, tracking both envelopes and completion.
e=a.make('ar25');o=None
for z in BASE:o=e.step(GameAction.from_id(z),data={})
for k in range(1,13):
 o=e.step(GameAction.from_id(2),data={})
 A=o.frame[0]
 def bb(c,region):
  yy,xx=np.where((A==c)&region)
  return None if len(xx)==0 else (int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),len(xx))
 Y,X=np.indices(A.shape)
 left=(X<36)&(Y<63); right=(X>38)&(Y<63)
 print(k,'lvl',o.levels_completed,'yellowL',bb(4,left),'grayR',bb(5,right),'black',bb(0,right),'navyL',bb(11,left),o.state)
 if o.levels_completed>1: print('SOLVED_AT',k);break
