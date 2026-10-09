from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1)
GEN=[1,5,7]

e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e);rootk=r.frame[0].tobytes()

seen={rootk:()}
q=deque([((),root)])
walls=0
returns=[]
while q:
 h,e0=q.popleft()
 if len(h)>=10:continue
 for z in GEN:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={});walls+=1
  nh=h+(z,)
  if rr.levels_completed>2:
   print('SOLVED_L3','REDUCED_SUFFIX',nh,'FULL',SOL+list(MEET)+list(nh),'WALL',walls)
   raise SystemExit
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=rr.frame[0].tobytes()
  if k==rootk:returns.append(nh)
  if k not in seen:
   seen[k]=nh;q.append((nh,copy.deepcopy(ee)))
print('NO_CLOSE','WALLS',walls,'STATES',len(seen),'RETURNS',len(returns))
for h in sorted(returns,key=lambda x:(len(x),x))[:50]:print('RETURN',h)
