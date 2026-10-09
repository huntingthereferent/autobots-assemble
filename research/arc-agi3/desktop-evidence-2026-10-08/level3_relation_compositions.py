from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import deque,Counter,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
ACTS=[1,2,3,4,5,7]
PAIRS=[(1,2),(2,1),(5,5),(5,1),(1,5),(5,2),(2,5),(7,5),(5,7),(3,4),(4,3),(3,3),(4,4)]

BASE=a.make('ar25'); BASE_O=None
for z in SOL: BASE_O=BASE.step(GameAction.from_id(z),data={})
BASE_FRAME=BASE_O.frame[0].copy()

def run(h):
    e=copy.deepcopy(BASE); o=None
    for z in h: o=e.step(GameAction.from_id(z),data={})
    return e,o,(o.frame[0].copy() if o is not None else BASE_FRAME.copy())

def a5sig(h):
    e,o,A=run(h)
    r=e.step(GameAction.from_id(5),data={}); B=r.frame[0].copy()
    D=np.argwhere(A!=B)
    tr=Counter((int(A[tuple(p)]),int(B[tuple(p)])) for p in D)
    return tuple(sorted((p,n) for p,n in tr.items() if p!=(11,12)))

# same witnessed 55-state frontier
_,_,R=run(())
seen={R.tobytes():()}
q=deque([()])
edges=0
while q and edges<100:
    h=q.popleft()
    for z in ACTS:
        e,o,A=run(h); r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy(); edges+=1
        if r.levels_completed>2:
            print('CLOSE_REBUILD',h+(z,)); raise SystemExit
        if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and B.tobytes() not in seen:
            seen[B.tobytes()]=h+(z,); q.append(h+(z,))
        if edges>=100: break

states=list(seen.values())
classes=defaultdict(list)
for h in states: classes[a5sig(h)].append(h)
ordered=sorted(classes,key=lambda c:(-len(classes[c]),repr(c)))
cid={c:i for i,c in enumerate(ordered)}
print('BASE_CLASSES',len(ordered),'STATES',len(states))
for c in ordered: print('C',cid[c],'N',len(classes[c]),c)

# pair-action relation on source class: destination A5 signatures reached after pair
raw={}
all_sigs=set(ordered)
for c in ordered:
    i=cid[c]
    for p in PAIRS:
        out=Counter()
        for h in classes[c]:
            e,o,A=run(h)
            ok=True; hh=list(h)
            for z in p:
                r=e.step(GameAction.from_id(z),data={}); hh.append(z)
                if r.levels_completed>2:
                    out['CLOSE']+=1; ok=False; break
                if r.state.name!='NOT_FINISHED' or r.levels_completed!=2:
                    out['STOP']+=1; ok=False; break
            if ok:
                s=a5sig(tuple(hh)); all_sigs.add(s); out[s]+=1
        raw[(i,p)]=out

extras=sorted(all_sigs-set(ordered),key=repr)
allordered=ordered+extras
allcid={c:i for i,c in enumerate(allordered)}
print('PAIR_REACHED_CLASSES',len(allordered),'NEW',len(extras))
for c in extras: print('NEW',allcid[c],c)

# encode each pair by its full behavior across the original 10 source classes
pair_sigs={}
for p in PAIRS:
    rows=[]
    for c in ordered:
        i=cid[c]
        enc=[]
        for k,n in raw[(i,p)].items():
            kk=k if isinstance(k,str) else allcid[k]
            enc.append((str(kk),n))
        rows.append((i,tuple(sorted(enc))))
    pair_sigs[p]=tuple(rows)

groups=defaultdict(list)
for p,s in pair_sigs.items(): groups[s].append(p)
print('\nPAIR_RELATION_CLASSES',len(groups))
for j,(sig,ps) in enumerate(groups.items()):
    print('PR',j,'PAIRS',ps)
    for row in sig: print(' ',row)

# compare selected pairs directly for exact whole-board equality, source-by-source.
print('\nEXACT_BOARD_EQ')
checks=[((1,2),(2,1)),((3,4),(4,3)),((3,3),(4,4)),((5,1),(1,5)),((5,2),(2,5)),((7,5),(5,7))]
for p,q2 in checks:
    eq=neq=other=0
    for h in states:
        ep,op,Bp=run(h+p)
        eq2,oq,Bq=run(h+q2)
        if op is None or oq is None: other+=1
        elif np.array_equal(Bp,Bq): eq+=1
        else: neq+=1
    print(p,'VS',q2,'EQ',eq,'NEQ',neq,'OTHER',other)
