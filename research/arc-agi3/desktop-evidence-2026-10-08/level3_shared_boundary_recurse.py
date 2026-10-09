from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from collections import deque

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=(2,2,2,1,1)   # exact same whole state as (5,5,4,5,7,2)
ACTS=[1,2,3,4,5,7]

e=a.make('ar25'); r=None
for z in SOL+list(MEET): r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e)
rootkey=r.frame[0].tobytes()

seen={rootkey:()}
q=deque([((),root)])
walls=0
returns=[]
while q:
    h,e0=q.popleft()
    if len(h)>=6: continue
    for z in ACTS:
        ee=copy.deepcopy(e0); rr=ee.step(GameAction.from_id(z),data={}); walls+=1
        nh=h+(z,)
        if rr.levels_completed>2:
            print('SOLVED_L3','MEET_SUFFIX',nh,'FULL',SOL+list(MEET)+list(nh),'WALL',walls)
            raise SystemExit
        if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2:
            continue
        k=rr.frame[0].tobytes()
        if k==rootkey:
            returns.append(nh)
        if k not in seen:
            seen[k]=nh
            q.append((nh,copy.deepcopy(ee)))

print('NO_CLOSE','WALLS',walls,'STATES',len(seen),'RETURNS_TO_MEET',len(returns))
for h in sorted(returns,key=lambda x:(len(x),x))[:40]:
    print('RETURN',h)

# Show the shortest collisions inside the recursion: different histories returning
# to an already witnessed whole state.
coll=[]
seen2={rootkey:()}
q=deque([((),root)])
while q and len(coll)<40:
    h,e0=q.popleft()
    if len(h)>=5: continue
    for z in ACTS:
        ee=copy.deepcopy(e0); rr=ee.step(GameAction.from_id(z),data={})
        if rr.state.name!='NOT_FINISHED' or rr.levels_completed!=2: continue
        nh=h+(z,); k=rr.frame[0].tobytes()
        if k in seen2 and seen2[k]!=nh:
            coll.append((seen2[k],nh))
        elif k not in seen2:
            seen2[k]=nh;q.append((nh,copy.deepcopy(ee)))
print('COLLISIONS',len(coll))
for a1,b1 in coll[:40]:print('EQ',a1,b1)
