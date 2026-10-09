from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy, hashlib
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
A=[1,2,3,4,5,7]
BASE=a.make('ar25'); O=None
for z in SOL: O=BASE.step(GameAction.from_id(z),data={})
BF=O.frame[0].copy()

def run(h):
    e=copy.deepcopy(BASE); o=None
    for z in h:o=e.step(GameAction.from_id(z),data={})
    return e,o,(o.frame[0].copy() if o is not None else BF.copy())

# witnessed 55
_,_,R=run(())
seen={R.tobytes():()};q=deque([()]);edges=0
while q and edges<100:
    h=q.popleft()
    for z in A:
        e,o,X=run(h);r=e.step(GameAction.from_id(z),data={});Y=r.frame[0].copy();edges+=1
        if r.levels_completed>2: print('CLOSE',h+(z,));raise SystemExit
        if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and Y.tobytes() not in seen:
            seen[Y.tobytes()]=h+(z,);q.append(h+(z,))
        if edges>=100:break
states=list(seen.values())
print('STATES',len(states))

# For each fixed suffix s, group prefixes x by exact transform x;s.
print('\nRIGHT_COLLAPSE (x then suffix)')
for s in A:
    groups=defaultdict(list)
    for x in A:
        sig=[]
        for h in states:
            _,o,B=run(h+(x,s))
            sig.append((o.levels_completed,o.state.name,hashlib.sha256(B.tobytes()).hexdigest()))
        groups[tuple(sig)].append(x)
    print('SUFFIX',s,'GROUPS',list(groups.values()))

# For each fixed prefix p, group suffixes x by exact transform p;x.
print('\nLEFT_CONTEXT (prefix then x)')
for p in A:
    groups=defaultdict(list)
    for x in A:
        sig=[]
        for h in states:
            _,o,B=run(h+(p,x))
            sig.append((o.levels_completed,o.state.name,hashlib.sha256(B.tobytes()).hexdigest()))
        groups[tuple(sig)].append(x)
    print('PREFIX',p,'GROUPS',list(groups.values()))

# Test whether the 7-induced quotient survives arbitrary following action.
# 1;7 == 2;7 and 3;7 == 4;7 already witnessed. Append every action z.
print('\nQUOTIENT_SURVIVAL_AFTER_7')
for z in A:
    eq12=eq34=0
    for h in states:
        _,_,B1=run(h+(1,7,z)); _,_,B2=run(h+(2,7,z))
        _,_,B3=run(h+(3,7,z)); _,_,B4=run(h+(4,7,z))
        eq12 += np.array_equal(B1,B2)
        eq34 += np.array_equal(B3,B4)
    print('APPEND',z,'12',eq12,'/55','34',eq34,'/55')

# Test whether prefixing an action before the collapsed relation preserves it.
print('\nQUOTIENT_SURVIVAL_BEFORE')
for z in A:
    eq12=eq34=0
    for h in states:
        _,_,B1=run(h+(z,1,7)); _,_,B2=run(h+(z,2,7))
        _,_,B3=run(h+(z,3,7)); _,_,B4=run(h+(z,4,7))
        eq12 += np.array_equal(B1,B2)
        eq34 += np.array_equal(B3,B4)
    print('PREFIX',z,'12',eq12,'/55','34',eq34,'/55')
