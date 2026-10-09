from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque,Counter,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1)
GEN=[1,5,7]
ACTS=[1,2,3,4,5,7]

e=a.make('ar25');r=None
for z in SOL+list(MEET):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e);rootk=r.frame[0].tobytes()

# 191 reduced-prefix witness states depth<=6, carrying known phase=count5 mod3.
seen={rootk:((),root,0)}
q=deque([((),root,0)])
while q:
 h,e0,p=q.popleft()
 if len(h)>=6:continue
 for z in GEN:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=rr.frame[0].tobytes();np=(p+(1 if z==5 else 0))%3
  if k not in seen:
   seen[k]=(h+(z,),copy.deepcopy(ee),np);q.append((h+(z,),copy.deepcopy(ee),np))

def dormant(e0):
 # current board key, then actions3/4
 # need current frame: use a harmless extraction by copying object's latest? derive via 3 inverse impossible.
 # caller passes key separately
 raise RuntimeError

def infer_phase(e0,k):
 # phase 0 iff 3 and4 are both identity.
 # otherwise apply one 5; if that reaches dormant => source phase2; else source phase1.
 def isD(ee,kk):
  a3=copy.deepcopy(ee);r3=a3.step(GameAction.from_id(3),data={})
  a4=copy.deepcopy(ee);r4=a4.step(GameAction.from_id(4),data={})
  return r3.frame[0].tobytes()==kk and r4.frame[0].tobytes()==kk
 if isD(e0,k): return 0
 e1=copy.deepcopy(e0);r1=e1.step(GameAction.from_id(5),data={});k1=r1.frame[0].tobytes()
 if isD(e1,k1): return 2
 e2=copy.deepcopy(e1);r2=e2.step(GameAction.from_id(5),data={});k2=r2.frame[0].tobytes()
 if isD(e2,k2): return 1
 return None

# Validate inference against known phases first.
bad=[]
for k,(h,e0,p) in seen.items():
 ip=infer_phase(e0,k)
 if ip!=p:bad.append((h,p,ip))
print('WITNESS_STATES',len(seen),'INFER_BAD',len(bad))
for x in bad[:10]:print('BAD',x)

trans=defaultdict(Counter)
examples=defaultdict(list)
for k,(h,e0,p) in seen.items():
 for z in ACTS:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.levels_completed>2:
   dst='CLOSE'
  elif rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:
   dst='STOP'
  else:
   kk=rr.frame[0].tobytes();dst=infer_phase(ee,kk)
  trans[(p,z)][dst]+=1
  if len(examples[(p,z,dst)])<5:examples[(p,z,dst)].append(h)

print('\nPHASE_ACTION_MAP')
for p in range(3):
 for z in ACTS:
  print('P',p,'A',z,'=>',dict(trans[(p,z)]))
  for dst,n in trans[(p,z)].items():
   if len(trans[(p,z)])>1: print('  EX',dst,examples[(p,z,dst)])
