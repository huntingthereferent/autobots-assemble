from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1); GEN=[1,5,7]; PRES=[1,2,3,4,7]

e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e);rootk=r.frame[0].tobytes()

seen={rootk:((),root,0)};q=deque([((),root,0)])
while q:
 h,e0,p=q.popleft()
 if len(h)>=6:continue
 for z in GEN:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=rr.frame[0].tobytes();np=(p+(z==5))%3
  if k not in seen:
   seen[k]=(h+(z,),copy.deepcopy(ee),np);q.append((h+(z,),copy.deepcopy(ee),np))
byphase=defaultdict(list)
for k,(h,e,p) in seen.items():byphase[p].append((h,e,k))

def dest(e0,a):
 if a=='E': return None
 e=copy.deepcopy(e0);rr=e.step(GameAction.from_id(a),data={})
 return rr.frame[0].tobytes()

for p in range(3):
 vals=byphase[p]
 print('\nPHASE',p,'N',len(vals))
 symbols=['E']+PRES
 # equality matrix across all witnesses; identity is current key
 for i,a1 in enumerate(symbols):
  for a2 in symbols[i+1:]:
   eq=0
   for h,e0,k in vals:
    d1=k if a1=='E' else dest(e0,a1)
    d2=k if a2=='E' else dest(e0,a2)
    eq += (d1==d2)
   if eq:
    print(a1,'=',a2,eq,'/',len(vals))
