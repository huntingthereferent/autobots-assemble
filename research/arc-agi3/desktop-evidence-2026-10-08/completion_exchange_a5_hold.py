from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
def tr(A,B):
 m=A!=B;return Counter(zip(A[m].tolist(),B[m].tolist()))
# A5 is the only crossing continuation that does not immediately undo 11->4.
# Follow that returned board, then all simple relations for two recursive layers.
for label,H in [('C8',[]),('C16',[4])]:
 P=BASE+H+[2]*5+[5]
 e,o,A=run(P); print(label,"AFTER5 lvl",o.levels_completed)
 for z in [1,2,3,4,5,7]:
  e,o,A=run(P);q=e.step(GameAction.from_id(z),data={});T=tr(A,q.frame[0])
  print(label,"5+",z,"lvl",q.levels_completed,"11>4",T[(11,4)],"4>11",T[(4,11)],"diff",sum(T.values()))
  if q.levels_completed>1: print("SOLVED",P+[z]);raise SystemExit
  for w in [1,2,3,4,5,7]:
   ee,oo,B=run(P+[z]);qq=ee.step(GameAction.from_id(w),data={})
   if qq.levels_completed>1: print("SOLVED2",P+[z,w]);raise SystemExit
print("NO_CLOSE_72")
