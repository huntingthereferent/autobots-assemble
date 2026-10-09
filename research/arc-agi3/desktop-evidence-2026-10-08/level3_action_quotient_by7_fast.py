from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy, hashlib
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
A=[1,2,3,4,5,7]
BASE=a.make('ar25'); O=None
for z in SOL: O=BASE.step(GameAction.from_id(z),data={})

# Build the same 55-state frontier, but preserve the actual environment at each state.
root=copy.deepcopy(BASE)
seen={O.frame[0].tobytes():((),root)}
q=deque([((),root)])
edges=0
while q and edges<100:
    h,e0=q.popleft()
    for z in A:
        e=copy.deepcopy(e0); r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy();edges+=1
        if r.levels_completed>2: print('CLOSE',h+(z,));raise SystemExit
        k=B.tobytes()
        if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and k not in seen:
            seen[k]=(h+(z,),copy.deepcopy(e)); q.append((h+(z,),copy.deepcopy(e)))
        if edges>=100:break
sources=[e for h,e in seen.values()]
print('STATES',len(sources))

def transform(e0,word):
    e=copy.deepcopy(e0); r=None
    for z in word:r=e.step(GameAction.from_id(z),data={})
    return r.frame[0].copy(),r

print('\nRIGHT_COLLAPSE')
for s in A:
    groups=defaultdict(list)
    for x in A:
        sig=[]
        for e0 in sources:
            B,r=transform(e0,(x,s))
            sig.append((r.levels_completed,r.state.name,hashlib.sha256(B.tobytes()).hexdigest()))
        groups[tuple(sig)].append(x)
    print('SUFFIX',s,'GROUPS',list(groups.values()))

print('\nLEFT_CONTEXT')
for p in A:
    groups=defaultdict(list)
    for x in A:
        sig=[]
        for e0 in sources:
            B,r=transform(e0,(p,x))
            sig.append((r.levels_completed,r.state.name,hashlib.sha256(B.tobytes()).hexdigest()))
        groups[tuple(sig)].append(x)
    print('PREFIX',p,'GROUPS',list(groups.values()))

print('\nQUOTIENT_SURVIVAL_AFTER_7')
for z in A:
    eq12=eq34=0
    for e0 in sources:
        B1,_=transform(e0,(1,7,z)); B2,_=transform(e0,(2,7,z))
        B3,_=transform(e0,(3,7,z)); B4,_=transform(e0,(4,7,z))
        eq12+=np.array_equal(B1,B2);eq34+=np.array_equal(B3,B4)
    print('APPEND',z,'12',eq12,'/55','34',eq34,'/55')

print('\nQUOTIENT_SURVIVAL_BEFORE')
for z in A:
    eq12=eq34=0
    for e0 in sources:
        B1,_=transform(e0,(z,1,7)); B2,_=transform(e0,(z,2,7))
        B3,_=transform(e0,(z,3,7)); B4,_=transform(e0,(z,4,7))
        eq12+=np.array_equal(B1,B2);eq34+=np.array_equal(B3,B4)
    print('PREFIX',z,'12',eq12,'/55','34',eq34,'/55')
