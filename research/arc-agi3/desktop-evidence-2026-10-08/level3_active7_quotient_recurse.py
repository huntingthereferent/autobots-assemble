from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
Q=(2,2,2,1,1,5,1,7)
ACTS=[1,2,3,4,5,7]

e=a.make('ar25');r=None
for z in SOL+list(Q):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e);rootk=r.frame[0].tobytes()
print('Q_START_L',r.levels_completed,r.state.name,flush=True)

seen={rootk:()}
q=deque([((),root)])
walls=0;returns=[]
while q and walls<500:
 h,e0=q.popleft()
 for z in ACTS:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={});walls+=1
  nh=h+(z,)
  if rr.levels_completed>2:
   print('SOLVED_L3','Q_SUFFIX',nh,'FULL',SOL+list(Q)+list(nh),'WALL',walls,flush=True)
   raise SystemExit
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=rr.frame[0].tobytes()
  if k==rootk:returns.append(nh)
  if k not in seen:
   seen[k]=nh;q.append((nh,copy.deepcopy(ee)))
  if walls>=500:break
print('NO_CLOSE','WALLS',walls,'STATES',len(seen),'RETURNS',returns[:30],flush=True)

# exact one-step/two-step collisions rooted at quotient return
items=list(seen.items())
# only display shortest alternative histories to same state encountered through local BFS
rev={}
coll=[]
qq=deque([((),root)])
while qq and len(coll)<50:
 h,e0=qq.popleft()
 if len(h)>=4:continue
 for z in ACTS:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  nh=h+(z,);k=rr.frame[0].tobytes()
  if k in rev and rev[k]!=nh:coll.append((rev[k],nh))
  elif k not in rev:
   rev[k]=nh;qq.append((nh,copy.deepcopy(ee)))
print('COLLISIONS',len(coll),flush=True)
for x,y in coll[:50]:print('EQ',x,y,flush=True)
