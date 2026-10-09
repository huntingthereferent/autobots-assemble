from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1)
GEN=[1,5,7]
PRES=[1,2,3,4,7]

e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e);rootk=r.frame[0].tobytes()

seen={rootk:((),root,0)}
q=deque([((),root,0)])
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
print('PHASE_SIZES',{p:len(v) for p,v in byphase.items()})

def out(e0,w):
 e=copy.deepcopy(e0);r=None
 for z in w:r=e.step(GameAction.from_id(z),data={})
 return r.frame[0].tobytes(),r.levels_completed,r.state.name

# matrix: for each phase p and a,b, count exact a5 == 5b
for p in range(3):
 print('\nPHASE',p,'TRANSPORT a5=5b')
 vals=byphase[p]
 for aa in PRES:
  scores=[]
  for bb in PRES:
   eq=0
   for h,e0 in vals:
    A=out(e0,(aa,5));B=out(e0,(5,bb))
    eq += (A==B)
   scores.append((eq,bb))
  scores.sort(reverse=True)
  print('A',aa,'BEST',scores[:5])

# reverse transport 5a = b5
for p in range(3):
 print('\nPHASE',p,'REVERSE 5a=b5')
 vals=byphase[p]
 for aa in PRES:
  scores=[]
  for bb in PRES:
   eq=0
   for h,e0 in vals:
    A=out(e0,(5,aa));B=out(e0,(bb,5))
    eq += (A==B)
   scores.append((eq,bb))
  scores.sort(reverse=True)
  print('A',aa,'BEST',scores[:5])
