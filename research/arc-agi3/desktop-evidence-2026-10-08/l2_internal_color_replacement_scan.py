from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import Counter
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
# Scan witnessed L2 parent states for INTERNAL cross-color replacement, excluding x=63 counter.
# We care especially 11<->4, 11<->5, 4<->5, and marker interactions.
for k in range(12):
 A,_=run(BASE+[2]*k)
 for act in [1,2,3,4,5,7]:
  B,o=run(BASE+[2]*k+[act]);D=A!=B
  pairs=Counter(zip(A[D].tolist(),B[D].tolist()))
  internal={}
  for p in [(11,4),(4,11),(11,5),(5,11),(4,5),(5,4),(0,4),(4,0),(0,11),(11,0),(0,5),(5,0)]:
   yy,xx=np.where((A==p[0])&(B==p[1])&(np.indices(A.shape)[1]<63))
   if len(xx): internal[p]=[(int(x),int(y)) for x,y in zip(xx,yy)]
  if internal:
   print('K',k,'A',act,'lvl',o.levels_completed,'INTERNAL', {p:len(v) for p,v in internal.items()},'pts',internal)
  if o.levels_completed>1: print('SOLVED',k,act);raise SystemExit
print('DONE')
