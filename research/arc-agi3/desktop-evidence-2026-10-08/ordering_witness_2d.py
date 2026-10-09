from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]; P=[1,2]
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame: break
 return o
# recurse the ordering witness: compare P^n 5^m vs 5^m P^n.
for m in [1,2,3,4,5,6]:
 print('M',m)
 for n in [1,2,3,4,5,6]:
  L=run(P*n+[5]*m); R=run([5]*m+P*n)
  if not L.frame or not R.frame:
   print(n,'terminal'); continue
  A,B=L.frame[0],R.frame[0]; ys,xs=np.where(A!=B)
  pts=list(zip(xs.tolist(),ys.tolist()))
  print('n',n,'diff',len(xs),'bbox',None if not len(xs) else (min(xs),max(xs),min(ys),max(ys)),'L',L.levels_completed,R.levels_completed)
