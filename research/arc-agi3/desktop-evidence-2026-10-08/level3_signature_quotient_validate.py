from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
ACTS=[1,2,3,4,5,7]
e=a.make('ar25');r=None
for z in SOL+MEET:r=e.step(GameAction.from_id(z),data={})
def K(e,r,w):
 x=copy.deepcopy(e);rr=r
 for z in w:rr=x.step(GameAction.from_id(z),data={})
 return rr.levels_completed,rr.state.name,rr.frame[0].tobytes()
def sig(e,r):
 k0=r.frame[0].tobytes()
 return (K(e,r,(3,))[2]==k0,K(e,r,(4,))[2]==k0,K(e,r,(3,))==K(e,r,(4,)),
 K(e,r,(3,4))==K(e,r,(1,2)),len({K(e,r,(z,7)) for z in [1,2,3,4]})==1,K(e,r,(2,))==K(e,r,(1,7,7)))
labels={(1,1,1,0,0,1):'A',(1,1,1,0,0,0):'B',(0,0,0,1,1,0):'C',(0,0,0,1,1,1):'D'}
seen={r.frame[0].tobytes():()}
q=deque([((),copy.deepcopy(e),r)])
trans=defaultdict(lambda:defaultdict(set)); counts=defaultdict(int); unknown=defaultdict(int)
while q:
 h,e0,r0=q.popleft()
 if len(h)>3:continue
 s=sig(e0,r0); lab=labels.get(tuple(map(int,s)),'X'+str(s));counts[lab]+=1
 if len(h)==3:continue
 for z in ACTS:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.levels_completed>2: print("SOLVED",h+(z,));raise SystemExit
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  s2=sig(ee,rr); lab2=labels.get(tuple(map(int,s2)),'X'+str(s2))
  trans[lab][z].add(lab2)
  k=rr.frame[0].tobytes()
  if k not in seen:
   seen[k]=h+(z,);q.append((h+(z,),copy.deepcopy(ee),rr))
print("WHOLE_STATES",len(seen),"SIGNATURE_COUNTS",dict(counts))
for lab in sorted(trans):
 print("FROM",lab)
 for z in ACTS: print(" ",z,"->",sorted(trans[lab][z]))
