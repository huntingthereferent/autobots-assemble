from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque,Counter,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
P=[3]*5+[2]*10+[7,5]+[2]*5+[5]; acts=[1,2,3,4,5,7]
def env(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Exact exchanged support: compare pre-hold to held parent.
_,_,pre=env([3]*5+[2]*10+[7,5]+[2]*4);_,_,root=env(P)
H=set(map(tuple,np.argwhere((pre==11)&(root==4))))
print("HELD",len(H),sorted(H))
# Recurse ONLY through whole states preserving H=yellow. This is the relation, not a score.
seen={root.tobytes():()}; q=deque([()]); walls=0; maxdepth=0
while q and walls<600:
 h=q.popleft(); maxdepth=max(maxdepth,len(h))
 for z in acts:
  e,o,B0=env(P+list(h)); r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy(); walls+=1
  if r.levels_completed>1:
   sol=P+list(h)+[z];print("SOLVED",sol,"WALLS",walls);raise SystemExit
  held=all(int(B[p])==4 for p in H)
  if held and r.state.name=="NOT_FINISHED" and B.tobytes() not in seen:
   nh=h+(z,);seen[B.tobytes()]=nh;q.append(nh)
print("PRESERVED_STATES",len(seen),"EDGES",walls,"MAXDEPTH",maxdepth,"QUEUE",len(q))
# Report exact preserving transitions by shortest histories and terminal boundary.
for h in sorted(seen.values(),key=lambda x:(len(x),x))[:80]:
 print("S",len(h),h)
# For each preserved state classify exits: preserve/restore/gameover and identity.
print("TRANSITIONS")
for h in sorted(seen.values(),key=lambda x:(len(x),x)):
 e,o,A=env(P+list(h))
 out=[]
 for z in acts:
  r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy()
  hs=all(int(B[p])==4 for p in H)
  out.append((z,'P' if hs else 'R',r.state.name,int(np.count_nonzero(A!=B))))
  # rebuild because actions mutate
  e,o,A=env(P+list(h))
 print(h,out)
