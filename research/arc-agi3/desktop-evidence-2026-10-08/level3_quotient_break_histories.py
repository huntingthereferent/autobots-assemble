from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,defaultdict
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]; ACTS=[1,2,3,4,5,7]
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
amb=defaultdict(list)
while q:
 h,e0,r0=q.popleft()
 if len(h)>3: continue
 s=labels.get(tuple(map(int,sig(e0,r0))),str(sig(e0,r0)))
 if len(h)==3: continue
 for z in ACTS:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2: continue
  s2=labels.get(tuple(map(int,sig(ee,rr))),str(sig(ee,rr)))
  if (s,z) in [('A',7),('B',7),('C',5)]:
   amb[(s,z)].append((h,s2))
  k=rr.frame[0].tobytes()
  if k not in seen:
   seen[k]=h+(z,);q.append((h+(z,),copy.deepcopy(ee),rr))
for key,rows in amb.items():
 print("AMB",key,"N",len(rows))
 by=defaultdict(list)
 for h,s2 in rows: by[s2].append(h)
 for s2,hs in by.items():
  print(" ->",s2,"COUNT",len(hs))
  for h in hs[:30]: print("   ",h)
