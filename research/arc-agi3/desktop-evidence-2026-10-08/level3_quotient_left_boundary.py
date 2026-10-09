from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import deque

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
A=[1,2,3,4,5,7]
BASE=a.make('ar25'); O=None
for z in SOL: O=BASE.step(GameAction.from_id(z),data={})
root=copy.deepcopy(BASE)
seen={O.frame[0].tobytes():((),root)}
q=deque([((),root)]);edges=0
while q and edges<100:
    h,e0=q.popleft()
    for z in A:
        e=copy.deepcopy(e0);r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy();edges+=1
        if r.levels_completed>2: print('CLOSE_REBUILD',h+(z,));raise SystemExit
        k=B.tobytes()
        if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and k not in seen:
            seen[k]=(h+(z,),copy.deepcopy(e));q.append((h+(z,),copy.deepcopy(e)))
        if edges>=100:break

def trans(e0,w):
    e=copy.deepcopy(e0);r=None
    for z in w:r=e.step(GameAction.from_id(z),data={})
    return r.frame[0].copy(),r

fails=[]
for h,e0 in seen.values():
    B1,r1=trans(e0,(2,1,7));B2,r2=trans(e0,(2,2,7))
    if not np.array_equal(B1,B2):fails.append(('12',h,(2,1,7),(2,2,7),r1.levels_completed,r2.levels_completed))
    B3,r3=trans(e0,(4,3,7));B4,r4=trans(e0,(4,4,7))
    if not np.array_equal(B3,B4):fails.append(('34',h,(4,3,7),(4,4,7),r3.levels_completed,r4.levels_completed))
print('FAILS',len(fails))
for f in fails:print('FAIL',f)

# Does one more 7 restore the quotient at those exact exceptions?
for tag,h,w1,w2,l1,l2 in fails:
    e0=next(e for hh,e in seen.values() if hh==h)
    for tail in [(),(7,),(5,),(1,),(2,),(3,),(4,)]:
        B1,r1=trans(e0,w1+tail);B2,r2=trans(e0,w2+tail)
        print('RECOVER',tag,'H',h,'TAIL',tail,'EQ',np.array_equal(B1,B2),'L',r1.levels_completed,r2.levels_completed)

# Compare whether the two exceptional source histories denote the same higher
# action orbit under one-step continuation.
for tag,h,*_ in fails:
    print('SOURCE',tag,h)
