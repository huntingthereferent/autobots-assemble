from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
# exact 16-replacement state
S=[3]*5+[2]*10+[7,5]+[2]*4+[2,4]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
P,_=run([3]*5+[2]*10+[7,5]+[2]*4)
origN=P==11
# recurse from returned 16 state with each permitted simple action, then second step only if relation survives.
for a1 in [1,2,3,4,5,7]:
 A,o=run(S+[a1])
 ov=int(np.sum(origN&(A==4)))
 print('FIRST',a1,'lvl',o.levels_completed,'overlap',ov)
 for a2 in [1,2,3,4,5,7]:
  B,q=run(S+[a1,a2]); ov2=int(np.sum(origN&(B==4)))
  # internal direct cross-color cells from A->B
  d=A!=B
  vals={}
  for p in [(11,4),(4,11),(5,4),(4,5),(11,5),(5,11),(0,4),(4,0),(0,11),(11,0)]:
   vals[p]=int(np.sum((A==p[0])&(B==p[1])&(np.indices(A.shape)[1]<63)))
  nz={k:v for k,v in vals.items() if v}
  print(' ',a1,a2,'lvl',q.levels_completed,'overlap',ov2,'cross',nz)
  if q.levels_completed>1:
   print('SOLVED',S+[a1,a2]);raise SystemExit
