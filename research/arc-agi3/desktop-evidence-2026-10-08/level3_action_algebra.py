from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy, hashlib
from collections import deque,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
ACTIONS=[1,2,3,4,5,7]
BASE=a.make('ar25'); O=None
for z in SOL: O=BASE.step(GameAction.from_id(z),data={})
BF=O.frame[0].copy()

def run(h):
    e=copy.deepcopy(BASE); o=None
    for z in h:o=e.step(GameAction.from_id(z),data={})
    return e,o,(o.frame[0].copy() if o is not None else BF.copy())

# same 55-state witnessed frontier
_,_,R=run(())
seen={R.tobytes():()}; q=deque([()]); edges=0
while q and edges<100:
    h=q.popleft()
    for z in ACTIONS:
        e,o,A=run(h); r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy(); edges+=1
        if r.levels_completed>2: print('CLOSE',h+(z,)); raise SystemExit
        if r.state.name=='NOT_FINISHED' and r.levels_completed==2 and B.tobytes() not in seen:
            seen[B.tobytes()]=h+(z,); q.append(h+(z,))
        if edges>=100: break
states=list(seen.values())
print('STATES',len(states))

# fingerprint each length-2 word by exact returned board across all 55 sources.
fps=defaultdict(list)
wordboards={}
for x in ACTIONS:
  for y in ACTIONS:
    w=(x,y); sig=[]; boards=[]
    for h in states:
      e,o,B=run(h+w)
      tag=(o.levels_completed,o.state.name,hashlib.sha256(B.tobytes()).hexdigest())
      sig.append(tag); boards.append(B)
    sig=tuple(sig); fps[sig].append(w); wordboards[w]=boards

print('EXACT_TRANSFORMATION_CLASSES',len(fps),'OF',len(ACTIONS)**2)
for i,(sig,words) in enumerate(sorted(fps.items(),key=lambda kv:(-len(kv[1]),kv[1]))):
    print('T',i,'N',len(words),'WORDS',words)

print('\nCOMMUTATION')
for i,x in enumerate(ACTIONS):
  for y in ACTIONS[i+1:]:
    eq=sum(np.array_equal(a,b) for a,b in zip(wordboards[(x,y)],wordboards[(y,x)]))
    print(x,y,'EQ',eq,'/',len(states))

# powers: identify if a^2 is exactly same transform as any other two-step word.
print('\nPOWERS')
for x in ACTIONS:
  target=None
  for sig,words in fps.items():
    if (x,x) in words: target=words;break
  print(x,'^2 CLASS',target)
