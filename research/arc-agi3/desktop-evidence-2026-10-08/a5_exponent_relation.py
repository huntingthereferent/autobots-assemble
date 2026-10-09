from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]; P=[1,2]
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame:return o
 return o
# Complete A5 exponent relation: support of [P^n,5^m].
for m in range(1,9):
 row=[]
 for n in [1,2,3]:
  L=run(P*n+[5]*m);R=run([5]*m+P*n)
  if not L.frame or not R.frame: row.append(('T',));continue
  A,B=L.frame[0],R.frame[0];ys,xs=np.where(A!=B)
  row.append((len(xs), None if not len(xs) else (int(ys.min()),int(ys.max()))))
 print('m',m,row)
