from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib
from collections import deque,defaultdict,Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]; acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Rebuild the exact Level3 whole-state frontier to 100 edges.
_,o,R=run(SOL); seen={R.tobytes():()}; q=deque([()]); edges=0
while q and edges<100:
 h=q.popleft()
 for z in acts:
  e,o,A=run(SOL+list(h));r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();edges+=1
  if r.levels_completed>2: print("SOLVED_REBUILD",SOL+list(h)+[z]);raise SystemExit
  if r.state.name=="NOT_FINISHED" and B.tobytes() not in seen:
   seen[B.tobytes()]=h+(z,);q.append(h+(z,))
  if edges>=100:break
# Audit A5 from every witnessed state: coordinate support of small rewrites.
small=[]; support_classes=defaultdict(list)
for k,h in list(seen.items()):
 e,o,A=run(SOL+list(h));r=e.step(GameAction.from_id(5),data={});B=r.frame[0].copy()
 if r.levels_completed>2: print("SOLVED_A5",SOL+list(h)+[5]);raise SystemExit
 D=np.argwhere(A!=B); n=len(D)
 if 0<n<=40:
  coords=tuple(map(tuple,D.tolist())); trans=Counter((int(A[tuple(p)]),int(B[tuple(p)])) for p in D)
  support_classes[(coords,tuple(sorted(trans.items())))].append(h); small.append((h,n,coords,trans))
print("STATES",len(seen),"SMALL_A5",len(small),"EXACT_SUPPORT_CLASSES",len(support_classes))
for i,(key,hs) in enumerate(sorted(support_classes.items(),key=lambda kv:-len(kv[1]))[:12]):
 coords,trans=key
 print("CLASS",i,"Nstates",len(hs),"rewriteN",len(coords),"trans",trans,"rep",hs[0],"bbox", (min(x for x,y in coords),max(x for x,y in coords),min(y for x,y in coords),max(y for x,y in coords)))
# Recurse only through exact returned states whose A5 rewrite belongs to the most recurrent witnessed support class.
if not support_classes: raise SystemExit
target=max(support_classes,key=lambda k:len(support_classes[k]))
seedhs=support_classes[target]
print("TARGET_REPS",seedhs[:10],"COUNT",len(seedhs))
walls=0; checked=set()
for h in seedhs:
 for z in acts:
  e,o,A=run(SOL+list(h));r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();walls+=1
  if r.levels_completed>2:
   print("SOLVED_L3",SOL+list(h)+[z],"WALL",walls);raise SystemExit
print("FOLLOW_WALLS",walls,"NO_CLOSE")
