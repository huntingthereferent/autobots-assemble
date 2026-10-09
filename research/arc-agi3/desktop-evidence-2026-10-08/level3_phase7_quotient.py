from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1); GEN=[1,5,7]; A=[1,2,3,4]

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
for k,(h,e,p) in seen.items():byphase[p].append((h,e))

def out(e0,w):
 e=copy.deepcopy(e0);r=None
 for z in w:r=e.step(GameAction.from_id(z),data={})
 return r.frame[0].tobytes()

for p in range(3):
 vals=byphase[p]
 print('\nPHASE',p,'N',len(vals),flush=True)
 print('PREFIX BEFORE 7: a7=b7')
 for i,a1 in enumerate(A):
  for a2 in A[i+1:]:
   eq=sum(out(e,(a1,7))==out(e,(a2,7)) for h,e in vals)
   if eq:print(a1,a2,eq,'/',len(vals),flush=True)
 print('SUFFIX AFTER 7: 7a=7b')
 for i,a1 in enumerate(A):
  for a2 in A[i+1:]:
   eq=sum(out(e,(7,a1))==out(e,(7,a2)) for h,e in vals)
   if eq:print(a1,a2,eq,'/',len(vals),flush=True)

 # test the known pair-collapse plus one more 7: a77=b77
 print('DOUBLE7: a77=b77')
 for i,a1 in enumerate(A):
  for a2 in A[i+1:]:
   eq=sum(out(e,(a1,7,7))==out(e,(a2,7,7)) for h,e in vals)
   if eq:print(a1,a2,eq,'/',len(vals),flush=True)
