from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# At the unique 11->4 exchange (down5), vary horizontal relation before crossing.
# This tests whether completion needs exchange + simultaneous paired horizontal relation.
walls=0
for hact,hn in [(4,1),(None,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7),(3,8)]:
 P=BASE+(([hact]*hn) if hact else [])+[2]*5
 e,o,A=run(P)
 if o.levels_completed>1: print("SOLVED_ENDPOINT",P);raise SystemExit
 # audit last transition's 11->4 by replaying pre
 _,_,pre=run(P[:-1]);m=pre!=A;tr=Counter(zip(pre[m].tolist(),A[m].tolist()))
 print("H",hact,hn,"exchange",tr[(11,4)],"rev",tr[(4,11)],"diff",int(m.sum()))
 for z in [1,2,3,4,5,7]:
  e,o,A=run(P);q=e.step(GameAction.from_id(z),data={});walls+=1
  if q.levels_completed>1: print("SOLVED",P+[z],"walls",walls);raise SystemExit
print("WALLS",walls)
