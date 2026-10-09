from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import deque

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
A=[1,2,3,4,5,7]
IDS=[((1,2),(2,1)),((1,3),(3,1)),((1,4),(4,1)),((2,3),(3,2)),((2,4),(4,2)),((3,4),(4,3)),((1,7),(2,7)),((3,7),(4,7)),((5,7),(7,5))]
BASE=a.make('ar25');O=None
for z in SOL:O=BASE.step(GameAction.from_id(z),data={})
root=copy.deepcopy(BASE)
seen={O.frame[0].tobytes():((),root)};q=deque([((),root)]);edges=0
while q and edges<100:
 h,e0=q.popleft()
 for z in A:
  e=copy.deepcopy(e0);r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();edges+=1
  if r.levels_completed>2:print('CLOSE_REBUILD',h+(z,));raise SystemExit
  k=B.tobytes()
  if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and k not in seen:
   seen[k]=(h+(z,),copy.deepcopy(e));q.append((h+(z,),copy.deepcopy(e)))
  if edges>=100:break
sources=list(seen.values())
print('STATES',len(sources))

def trans(e0,w):
 e=copy.deepcopy(e0);r=None
 for z in w:r=e.step(GameAction.from_id(z),data={})
 return r.frame[0].copy(),r

for lhs,rhs in IDS:
 print('\nID',lhs,'=',rhs)
 totalfail=0
 for p in A:
  fs=[]
  for h,e0 in sources:
   B1,r1=trans(e0,(p,)+lhs);B2,r2=trans(e0,(p,)+rhs)
   if not np.array_equal(B1,B2):fs.append(h)
  totalfail+=len(fs)
  print(' PREFIX',p,'EQ',55-len(fs),'/55','FAIL_H',fs[:8])
 print(' TOTAL_LEFT_FAILURES',totalfail)
