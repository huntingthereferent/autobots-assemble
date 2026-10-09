from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import deque

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
ACTS=[1,2,3,4,5,7]
H1=(2,2,2)
H2=(5,5,4)

BASE=a.make('ar25'); O=None
for z in SOL: O=BASE.step(GameAction.from_id(z),data={})

def env_after(h):
    e=copy.deepcopy(BASE); r=None
    for z in h: r=e.step(GameAction.from_id(z),data={})
    return e,r

def bfs(seed,maxdepth=5):
    e0,r0=env_after(seed)
    b0=r0.frame[0].tobytes()
    seen={b0:()}
    envs={b0:copy.deepcopy(e0)}
    q=deque([((),copy.deepcopy(e0))])
    closed=[]
    while q:
        h,e=q.popleft()
        if len(h)>=maxdepth: continue
        for z in ACTS:
            ee=copy.deepcopy(e); rr=ee.step(GameAction.from_id(z),data={})
            nh=h+(z,)
            if rr.levels_completed>2:
                closed.append((nh,rr.levels_completed,rr.state.name))
                continue
            if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:
                continue
            k=rr.frame[0].tobytes()
            if k not in seen:
                seen[k]=nh; envs[k]=copy.deepcopy(ee); q.append((nh,copy.deepcopy(ee)))
    return seen,closed

S1,C1=bfs(H1,5)
S2,C2=bfs(H2,5)
print('B1_STATES',len(S1),'CLOSE',len(C1))
print('B2_STATES',len(S2),'CLOSE',len(C2))
for x in C1[:20]: print('C1',x)
for x in C2[:20]: print('C2',x)

meet=set(S1)&set(S2)
print('MEET',len(meet))
for i,k in enumerate(sorted(meet,key=lambda k:(len(S1[k])+len(S2[k]),S1[k],S2[k]))[:30]):
    print('M',i,'FROM1',S1[k],'FROM2',S2[k],'LEN',len(S1[k]),len(S2[k]))

# Direct mapping: does one boundary source reach the exact other source whole board?
E1,R1=env_after(H1); E2,R2=env_after(H2)
K1=R1.frame[0].tobytes(); K2=R2.frame[0].tobytes()
print('H1_TO_H2',S1.get(K2))
print('H2_TO_H1',S2.get(K1))

# If they meet, test smallest meet as the next shared referent and one-step closure from it.
if meet:
    k=min(meet,key=lambda kk:(len(S1[kk])+len(S2[kk]),len(S1[kk]),S1[kk]))
    w1=S1[k]; w2=S2[k]
    print('BEST_MEET',w1,w2)
    e,_=env_after(H1+w1)
    for z in ACTS:
        ee=copy.deepcopy(e); rr=ee.step(GameAction.from_id(z),data={})
        print('MEET_STEP',z,'L',rr.levels_completed,rr.state.name)
