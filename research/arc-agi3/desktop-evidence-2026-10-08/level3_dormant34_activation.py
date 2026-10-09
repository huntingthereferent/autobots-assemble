from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,Counter,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1)
GEN=[1,5,7]

e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e); rootk=r.frame[0].tobytes()

# build unique reduced-prefix states to depth 4
seen={rootk:((),root)}
q=deque([((),root)])
while q:
 h,e0=q.popleft()
 if len(h)>=4:continue
 for z in GEN:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=rr.frame[0].tobytes()
  if k not in seen:
   seen[k]=(h+(z,),copy.deepcopy(ee));q.append((h+(z,),copy.deepcopy(ee)))

print('PREFIX_STATES',len(seen))
classes=defaultdict(list)
for k,(h,e0) in seen.items():
 # apply 3 and 4 independently
 e3=copy.deepcopy(e0);r3=e3.step(GameAction.from_id(3),data={});k3=r3.frame[0].tobytes()
 e4=copy.deepcopy(e0);r4=e4.step(GameAction.from_id(4),data={});k4=r4.frame[0].tobytes()
 if r3.levels_completed>2: c3='CLOSE'
 elif k3==k:c3='ID'
 else:c3='MOVE'
 if r4.levels_completed>2: c4='CLOSE'
 elif k4==k:c4='ID'
 else:c4='MOVE'
 rel='SAME' if k3==k4 else 'SPLIT'
 classes[(c3,c4,rel)].append(h)

for c,hs in sorted(classes.items(),key=lambda kv:(min(map(len,kv[1])),kv[0])):
 print('CLASS',c,'N',len(hs),'MINDEPTH',min(map(len,hs)),'REPS',sorted(hs,key=lambda x:(len(x),x))[:20])

# first activation edges: parent has both ID, child under g no longer both ID
print('\nFIRST_ACTIVATION')
for k,(h,e0) in seen.items():
 def typ(e00,kk):
  e3=copy.deepcopy(e00);r3=e3.step(GameAction.from_id(3),data={})
  e4=copy.deepcopy(e00);r4=e4.step(GameAction.from_id(4),data={})
  return (r3.frame[0].tobytes()==kk,r4.frame[0].tobytes()==kk,r3.frame[0].tobytes()==r4.frame[0].tobytes())
 pt=typ(e0,k)
 if pt!=(True,True,True):continue
 for z in GEN:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  ck=rr.frame[0].tobytes();ct=typ(ee,ck)
  if ct!=(True,True,True):
   print('ACTIVATE','FROM',h,'BY',z,'TO',h+(z,),'TYPE',ct)
