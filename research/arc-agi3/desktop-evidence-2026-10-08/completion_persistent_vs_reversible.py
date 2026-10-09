from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
def trans(pre,post):
 m=pre!=post; return Counter(zip(pre[m].tolist(),post[m].tolist()))
# Positive L1 closure signature, then compare reversibility one step after each candidate L2 crossing.
e,o,A=run([3]*5+[2]*9); q=e.step(GameAction.from_id(2),data={}); T=trans(A,q.frame[0])
print("L1",T)
# earned crossing states: base and outward-saturated, at down5.
for label,H in [('C8',[]),('C16',[4])]:
 P=BASE+H+[2]*5
 e,o,A=run(P)
 _,_,pre=run(P[:-1]); print(label,"CROSS",trans(pre,A))
 # test whether alternative action at crossing converts reversible exchange into persistent rewrite
 for z in [1,2,3,4,5,7]:
  e,o,A=run(P); q=e.step(GameAction.from_id(z),data={}); B=q.frame[0]
  t=trans(A,B)
  print(label,"A",z,"lvl",q.levels_completed,"11>4",t[(11,4)],"4>11",t[(4,11)],"11>5",t[(11,5)],"4>9",t[(4,9)],"diff",sum(t.values()))
  if q.levels_completed>1: print("SOLVED",P+[z]);raise SystemExit
  # recurse same returned relation one more step only where state changed
  if not np.array_equal(A,B):
   qq=e.step(GameAction.from_id(z),data={})
   if qq.levels_completed>1: print("SOLVED2",P+[z,z]);raise SystemExit
print("DONE")
