from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib
from collections import deque,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]; acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
_,o,R=run(SOL); seen={R.tobytes():()}; q=deque([()]); walls=0; eq=0; term=0
while q and walls<100:
 h=q.popleft()
 e,o,A=run(SOL+list(h))
 for z in acts:
  # replay parent for independent edge
  ee,oo,P=run(SOL+list(h)); r=ee.step(GameAction.from_id(z),data={}); B=r.frame[0].copy(); walls+=1
  if r.levels_completed>2:
   sol=SOL+list(h)+[z]
   print("SOLVED_L3",sol,"WALL",walls,"DEPTH",len(h)+1); raise SystemExit
  k=B.tobytes()
  if k in seen: eq+=1
  elif r.state.name=="NOT_FINISHED":
   seen[k]=h+(z,); q.append(h+(z,))
  else: term+=1
  print("W",walls,"D",len(h)+1,"H",h,"A",z,"DIFF",int(np.count_nonzero(P!=B)),"EQ",k in seen and seen[k]!=(h+(z,)),"LVL",r.levels_completed,"STATE",r.state.name)
  if walls>=100:break
print("BOUNDARY walls",walls,"states",len(seen),"frontier",len(q),"equal_returns",eq,"terminal",term,"maxdepth",max(map(len,seen.values())))
