from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,itertools
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1)
GEN=[1,5,7]; XY=[3,4]

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
for k,(h,e,p) in seen.items():byphase[p].append((h,e,k))

def apply(e0,w):
 e=copy.deepcopy(e0);rr=None
 for z in w:
  rr=e.step(GameAction.from_id(z),data={})
  if rr.levels_completed>2:return None,rr
 return rr.frame[0].tobytes(),rr

WORDS=[]
for n in range(1,7):
 WORDS += list(itertools.product(XY,repeat=n))

for p in range(3):
 vals=byphase[p]; rh,re,rk=vals[0]
 print('\nPHASE',p,'N',len(vals),'REP',rh,flush=True)
 cand=[]; close=[]
 for w in WORDS:
  k,rr=apply(re,w)
  if rr.levels_completed>2: close.append(w)
  elif k==rk:cand.append(w)
 print('REP_ID_WORDS',cand[:80],'COUNT',len(cand),flush=True)
 print('REP_CLOSE_WORDS',close[:30],'COUNT',len(close),flush=True)
 # verify only minimal candidate identities (remove those with identity prefix)
 mins=[]
 for w in sorted(cand,key=lambda x:(len(x),x)):
  if not any(len(v)<len(w) and w[:len(v)]==v for v in cand): mins.append(w)
 print('MIN_ID_CAND',mins[:30],flush=True)
 for w in mins[:30]:
  eq=0; closes=0; fail=[]
  for h,e0,k0 in vals:
   kk,rr=apply(e0,w)
   if rr.levels_completed>2:closes+=1
   elif kk==k0:eq+=1
   elif len(fail)<3:fail.append(h)
  print(' VERIFY',w,'ID',eq,'CLOSE',closes,'/',len(vals),'FAIL',fail,flush=True)
