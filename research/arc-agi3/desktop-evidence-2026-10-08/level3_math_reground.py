from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib
from collections import defaultdict,Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]; acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
_,o,R=run(SOL)
print("ROOT",o.levels_completed,Counter(R.flatten()))
# Math reground: x0 is whole returned board. Compute x1=action(x0), then quotient ONLY by exact whole-board equality.
classes=defaultdict(list); boards={}
for z in acts:
 e,o,A=run(SOL);r=e.step(GameAction.from_id(z),data={});B=r.frame[0].copy()
 k=hashlib.sha256(B.tobytes()).hexdigest()[:12];classes[k].append(z);boards[z]=B
 print("X1",z,k,"diff",np.count_nonzero(R!=B),"colors",dict(Counter(B.flatten())))
print("X1_EXACT_CLASSES",dict(classes))
# For each exact x1, apply same permitted relations again. Report exact closures/equalities, no semantic map.
seen={}
for z in acts:
 for w in acts:
  e,o,A=run(SOL+[z]);r=e.step(GameAction.from_id(w),data={});B=r.frame[0].copy()
  if r.levels_completed>2:
   print("SOLVED_L3",SOL+[z,w]);raise SystemExit
  k=hashlib.sha256(B.tobytes()).hexdigest()[:12]
  seen.setdefault(k,[]).append((z,w))
print("X2_EXACT_CLASSES",len(seen),"from",len(acts)**2,"histories")
for k,hs in sorted(seen.items(),key=lambda kv:-len(kv[1])):
 if len(hs)>1: print("EQ",k,hs)
