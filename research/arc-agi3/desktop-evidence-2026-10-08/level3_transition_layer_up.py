from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import deque,Counter,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
ACTS=[1,2,3,4,5,7]
BASE=a.make('ar25'); BASE_O=None
for z in SOL:
    BASE_O=BASE.step(GameAction.from_id(z),data={})
BASE_FRAME=BASE_O.frame[0].copy()

def run(h):
    e=copy.deepcopy(BASE); o=None
    for z in h:
        o=e.step(GameAction.from_id(z),data={})
    return e,o,(o.frame[0].copy() if o is not None else BASE_FRAME.copy())

def a5class(h):
    e,o,A=run(h)
    r=e.step(GameAction.from_id(5),data={}); B=r.frame[0].copy()
    D=np.argwhere(A!=B)
    tr=Counter((int(A[tuple(p)]),int(B[tuple(p)])) for p in D)
    return tuple(sorted((p,n) for p,n in tr.items() if p!=(11,12)))

# Rebuild same 100-edge / 55-whole-state frontier.
_,_,R=run(())
seen={R.tobytes():()}
q=deque([()])
edges=0
while q and edges<100:
    h=q.popleft()
    for z in ACTS:
        e,o,A=run(h)
        r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy()
        edges+=1
        if r.levels_completed>2:
            print('SOLVED_DURING_REBUILD',SOL+list(h)+[z]); raise SystemExit
        if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and B.tobytes() not in seen:
            seen[B.tobytes()]=h+(z,); q.append(h+(z,))
        if edges>=100: break

states=list(seen.values())
classes=defaultdict(list)
for h in states: classes[a5class(h)].append(h)
ordered=sorted(classes,key=lambda c:(-len(classes[c]),repr(c)))
cid={c:i for i,c in enumerate(ordered)}
print('WHOLE_STATES',len(states),'A5_CLASSES',len(ordered))
for c in ordered:
    print('C',cid[c],'N',len(classes[c]),c)

# Promote class transitions to the new objects.
# First collect raw destination signatures, including classes not present in
# the original 55-state frontier. Do not force closure onto the old vocabulary.
RAW={}
allclasses=set(ordered)
for c in ordered:
    for z in ACTS:
        out=Counter()
        for h in classes[c]:
            e,o,A=run(h)
            r=e.step(GameAction.from_id(z),data={})
            if r.levels_completed>2:
                out['CLOSE']+=1
            elif r.state.name=='NOT_FINISHED' and r.levels_completed==2:
                nh=h+(z,)
                dc=a5class(nh); allclasses.add(dc); out[dc]+=1
            else:
                out['STOP']+=1
        RAW[(c,z)]=out

# Keep the original ten IDs stable; append newly reached classes.
extras=sorted(allclasses-set(ordered),key=repr)
allordered=ordered+extras
cid={c:i for i,c in enumerate(allordered)}
print('REACHED_CLASSES',len(allordered),'NEW',len(extras))
for c in extras: print('NEW_C',cid[c],c)

T={}
for c in ordered:
    for z in ACTS:
        out=Counter()
        for k,n in RAW[(c,z)].items():
            out[k if isinstance(k,str) else cid[k]]+=n
        T[(cid[c],z)]=out

print('\nCLASS_ACTION_MAP')
for c in ordered:
    i=cid[c]
    print('SRC',i,'N',len(classes[c]))
    for z in ACTS:
        print(' ',z,'=>',dict(T[(i,z)]))

# One layer higher again: action-row shape, forgetting multiplicity scale but
# preserving which destination classes coexist under each action.
row_groups=defaultdict(list)
for c in ordered:
    i=cid[c]
    row=[]
    for z in ACTS:
        dest=tuple(sorted(str(k) for k in T[(i,z)].keys()))
        row.append((z,dest))
    row_groups[tuple(row)].append(i)

print('\nROW_CLASSES',len(row_groups))
for j,(sig,members) in enumerate(sorted(row_groups.items(),key=lambda kv:(-len(kv[1]),kv[1]))):
    print('R',j,'MEMBERS',members,'SIG',sig)

# Collapse destination classes by row-class and iterate once more.
r_of={}
for j,(sig,members) in enumerate(sorted(row_groups.items(),key=lambda kv:(-len(kv[1]),kv[1]))):
    for i in members:r_of[i]=j

higher=defaultdict(list)
for c in ordered:
    i=cid[c]
    sig=[]
    for z in ACTS:
        outs=[]
        for k,n in T[(i,z)].items():
            kk=k if isinstance(k,str) else r_of[k]
            outs.append((str(kk),n))
        sig.append((z,tuple(sorted(outs))))
    higher[tuple(sig)].append(i)

print('\nHIGHER_CLASSES',len(higher))
for j,(sig,members) in enumerate(sorted(higher.items(),key=lambda kv:(-len(kv[1]),kv[1]))):
    print('H',j,'MEMBERS',members)
    for x in sig: print(' ',x)
