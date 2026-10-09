from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque,Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]; acts=[1,2,3,4,5,7]
def run(h):
 e=a.make('ar25');o=None
 for z in SOL+list(h): o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# x0 and the witnessed relation: A5 causes exactly one 11->12 transition.
_,_,R=run(())
seen={R.tobytes():()}; q=deque([()]); walls=0; kept=0; rejected=0; identities=0
while q and walls<100:
 h=q.popleft()
 e,o,A=run(h)
 for z in acts:
  ee,oo,P=run(h); r=ee.step(GameAction.from_id(z),data={}); B=r.frame[0].copy(); walls+=1
  if r.levels_completed>2:
   print("SOLVED_L3",SOL+list(h)+[z],"WALL",walls,"REL_KEPT",kept); raise SystemExit
  if r.state.name!="NOT_FINISHED":
   rejected+=1
  else:
   # audit returned state by its own A5 witness; do not replace B with this diagnostic.
   e2,o2,C=run(h+(z,)); rr=e2.step(GameAction.from_id(5),data={}); D=rr.frame[0].copy()
   idx=np.argwhere(C!=D); tr=Counter((int(C[tuple(p)]),int(D[tuple(p)])) for p in idx)
   rel=(tr.get((11,12),0)==1)
   if np.array_equal(P,B): identities+=1
   if rel:
    kept+=1
    k=B.tobytes()
    if k not in seen:
     seen[k]=h+(z,); q.append(h+(z,))
   else: rejected+=1
  print("W",walls,"depth",len(h)+1,"h",h,"a",z,"REL",rel if r.state.name=="NOT_FINISHED" else False,"lvl",r.levels_completed)
  if walls>=100: break
print("BOUNDARY",walls,"whole_states",len(seen),"frontier",len(q),"relation_kept_edges",kept,"nonrelation_or_terminal",rejected,"identity_edges",identities,"maxdepth",max(map(len,seen.values())))
