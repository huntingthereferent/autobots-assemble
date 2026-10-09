from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Search only earned returned trajectories for the L1 closure-bearing exchange 11->4.
# Four straight relation families from B8, record exact steps where 11->4 appears.
families=[("up",1,24),("down",2,24),("in",3,24),("out",4,8)]
candidates=[]
for name,act,N in families:
 e,o,A=run(BASE)
 for n in range(1,N+1):
  pre=A.copy();q=e.step(GameAction.from_id(act),data={});post=q.frame[0];m=pre!=post
  tr=Counter(zip(pre[m].tolist(),post[m].tolist()))
  if tr[(11,4)] or tr[(4,11)]:
   print("EXCHANGE",name,n,"11>4",tr[(11,4)],"4>11",tr[(4,11)],"diff",int(m.sum()),"lvl",q.levels_completed)
   candidates.append((name,act,n,tr[(11,4)],tr[(4,11)]))
  if q.levels_completed>1: print("SOLVED",BASE+[act]*n);raise SystemExit
  if np.array_equal(pre,post): break
  A=post;o=q
print("CANDIDATES",candidates)
# At each earned exchange state, test all simple continuations independently.
for name,act,n,x,y in candidates:
 P=BASE+[act]*n
 for z in [1,2,3,4,5,7]:
  e,o,A=run(P);q=e.step(GameAction.from_id(z),data={})
  print("W",name,n,z,"diff",int(np.sum(A!=q.frame[0])),"lvl",q.levels_completed,q.state)
  if q.levels_completed>1: print("SOLVED_BRANCH",P+[z]);raise SystemExit
