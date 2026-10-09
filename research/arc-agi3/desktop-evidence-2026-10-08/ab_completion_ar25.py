from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
from collections import deque

A=Arcade(operation_mode=OperationMode.NORMAL)
SOLVE=[3]*5+[2]*10
ENTRY=SOLVE+[7,5]+[2]*4
ACTS=(1,2,3,4,5,7)

def run(seq):
 e=A.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
def h(b): return hashlib.sha256(b.tobytes()).hexdigest()[:16]

root,ro=run(ENTRY)
# Child space is not arbitrary histories: relation-bearing returned states.
# A distinction is the whole-board transition signature + internal cross-color
# replacement + marker representation.  Oscillate a complete frontier, then
# close if another frontier contributes no new distinction.
orig_navy=root==11
seen={h(root):()}
frontier=[()]
dist=set()
round_no_new=0
for layer in range(1,12):
 nxt=[]; newdist=0
 print('LAYER',layer,'frontier',len(frontier),'known',len(seen))
 for hist in frontier:
  before,_=run(ENTRY+list(hist))
  for z in ACTS:
   after,o=run(ENTRY+list(hist)+[z])
   k=h(after)
   # evidence-bearing diagnostic; board remains referent
   internal11to4=int(np.sum((before==11)&(after==4)&(~np.indices(after.shape)[1].astype(bool)*False)))
   # Exclude resource edge explicitly from cross-color diagnostic only.
   yy,xx=np.indices(after.shape)
   cross=int(np.sum((before==11)&(after==4)&(xx!=63)))
   rev=int(np.sum((before==4)&(after==11)&(xx!=63)))
   marker=int(np.sum(after==0))
   sig=(cross,rev,marker)
   if sig not in dist:
    dist.add(sig);newdist+=1
    print(' NEW',hist+(z,),'sig',sig,'lvl',o.levels_completed)
   if o.levels_completed>1:
    print('SOLVED',ENTRY+list(hist)+[z]);raise SystemExit
   if k not in seen:
    seen[k]=hist+(z,);nxt.append(hist+(z,))
 print('RETURN-CHECK layer',layer,'new distinctions',newdist,'new states',len(nxt))
 if newdist==0:
  round_no_new+=1
 else: round_no_new=0
 if round_no_new>=1:
  print('SPACE_COMPLETE layer',layer,'states',len(seen),'distinctions',sorted(dist))
  break
 frontier=nxt
 if not frontier:
  print('SPACE_COMPLETE exhausted',layer);break
