from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque,Counter,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]; acts=[1,2,3,4,5,7]
def run(h):
 e=a.make('ar25');o=None
 for z in SOL+list(h):o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
_,_,R=run(())
# rebuild exact 100-edge frontier
seen={R.tobytes():()};q=deque([()]);edges=0
while q and edges<100:
 h=q.popleft()
 for z in acts:
  e,o,A=run(h);r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();edges+=1
  if r.levels_completed>2: print("SOLVED",SOL+list(h)+[z]);raise SystemExit
  if r.state.name=="NOT_FINISHED" and B.tobytes() not in seen:seen[B.tobytes()]=h+(z,);q.append(h+(z,))
  if edges>=100:break
# Factor only the varying part of each state's own A5 rewrite, with 11->12 removed as witnessed invariant.
classes=defaultdict(list)
for k,h in seen.items():
 e,o,A=run(h);r=e.step(GameAction.from_id(5),data={});B=r.frame[0].copy()
 D=np.argwhere(A!=B); tr=Counter((int(A[tuple(p)]),int(B[tuple(p)])) for p in D)
 var=tuple(sorted((p,n) for p,n in tr.items() if p!=(11,12)))
 classes[var].append(h)
print("VAR_CLASSES",len(classes),"STATES",len(seen))
for i,(v,hs) in enumerate(sorted(classes.items(),key=lambda x:-len(x[1]))):
 print("V",i,"N",len(hs),"TRANS",v,"REPS",hs[:6])
# 100 walls: recurse from most recurrent varying classes, but whole boards remain states.
ordered=sorted(classes.items(),key=lambda x:-len(x[1]))
seeds=[]
for v,hs in ordered:
 if len(hs)>=2: seeds.extend(hs)
walls=0; outcomes=defaultdict(lambda:Counter())
for h in seeds:
 # parent varying signature
 e,o,A=run(h);rr=e.step(GameAction.from_id(5),data={});C=rr.frame[0].copy()
 D=np.argwhere(A!=C); pt=Counter((int(A[tuple(p)]),int(C[tuple(p)])) for p in D)
 pv=tuple(sorted((p,n) for p,n in pt.items() if p!=(11,12)))
 for z in acts:
  e,o,A=run(h);r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();walls+=1
  if r.levels_completed>2:
   print("SOLVED_L3",SOL+list(h)+[z],"WALL",walls);raise SystemExit
  if r.state.name=="NOT_FINISHED":
   e2,o2,X=run(h+(z,));r2=e2.step(GameAction.from_id(5),data={});Y=r2.frame[0].copy()
   DD=np.argwhere(X!=Y);tt=Counter((int(X[tuple(p)]),int(Y[tuple(p)])) for p in DD)
   nv=tuple(sorted((p,n) for p,n in tt.items() if p!=(11,12)))
   outcomes[pv][nv]+=1
  if walls>=100:break
 if walls>=100:break
print("WALLS",walls,"PARENT_CLASSES_TESTED",len(outcomes))
for pv,c in outcomes.items():print("MAP",pv,"=>",c.most_common(8))
