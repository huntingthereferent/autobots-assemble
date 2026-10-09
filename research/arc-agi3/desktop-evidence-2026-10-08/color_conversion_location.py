from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import Counter
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
# Locate the persistent 11->5 conversion exactly for different actions/states.
BASE=[3]*5+[2]*10+[7,5]
cases=[('B8',BASE),('D4',BASE+[2]*4),('D8',BASE+[2]*8)]
for name,seq in cases:
 A,_=run(seq)
 print('\n',name)
 for act in [1,2,3,4,5,7]:
  B,o=run(seq+[act]); yy,xx=np.where((A==11)&(B==5))
  pts=list(zip(xx.tolist(),yy.tolist()))
  print('A',act,'11to5',pts,'lvl',o.levels_completed)
# Compare L1 successful closing move: where are its 11->4 conversions?
A,_=run([3]*5+[2]*9);B,o=run([3]*5+[2]*10)
yy,xx=np.where((A==11)&(B==4))
print('\nL1_CLOSE_11to4',list(zip(xx.tolist(),yy.tolist())))
