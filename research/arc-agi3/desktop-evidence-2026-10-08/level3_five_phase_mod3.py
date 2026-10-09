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
root=copy.deepcopy(e);rootk=r.frame[0].tobytes()

# unique states reachable by reduced generators to depth 6
seen={rootk:((),root)}
q=deque([((),root)])
while q:
 h,e0=q.popleft()
 if len(h)>=6:continue
 for z in GEN:
  ee=copy.deepcopy(e0);rr=ee.step(GameAction.from_id(z),data={})
  if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:continue
  k=rr.frame[0].tobytes()
  if k not in seen:
   seen[k]=(h+(z,),copy.deepcopy(ee));q.append((h+(z,),copy.deepcopy(ee)))

rows=[]
bad=[]
for k,(h,e0) in seen.items():
 e3=copy.deepcopy(e0);r3=e3.step(GameAction.from_id(3),data={});k3=r3.frame[0].tobytes()
 e4=copy.deepcopy(e0);r4=e4.step(GameAction.from_id(4),data={});k4=r4.frame[0].tobytes()
 typ='D' if k3==k and k4==k else ('E' if k3==k4 else 'S')
 phase=h.count(5)%3
 rows.append((phase,typ,h))
 # candidate: phase0 dormant, phase1/2 split
 expect='D' if phase==0 else 'S'
 if typ!=expect:bad.append((h,phase,typ))

C=Counter((p,t) for p,t,h in rows)
print('STATES',len(rows),'PHASE_TYPE_COUNTS',dict(C),'MISMATCH',len(bad))
for x in bad[:30]:print('BAD',x)

# Pure 5 powers: exact phase orbit and whether 3/4 are identity/same/split.
print('\nPURE5')
e0=copy.deepcopy(root)
for n in range(13):
 k=(r.frame[0].tobytes() if n==0 else cur.frame[0].tobytes())
 e3=copy.deepcopy(e0);r3=e3.step(GameAction.from_id(3),data={})
 e4=copy.deepcopy(e0);r4=e4.step(GameAction.from_id(4),data={})
 typ='D' if r3.frame[0].tobytes()==k and r4.frame[0].tobytes()==k else ('E' if r3.frame[0].tobytes()==r4.frame[0].tobytes() else 'S')
 print('N',n,'MOD3',n%3,'TYPE',typ,'ROOT',k==rootk)
 ee=copy.deepcopy(e0);cur=ee.step(GameAction.from_id(5),data={});e0=ee
