from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Completion referent: horizontal separation controls 11->4 exchange.
# Explore the only earned outward direction to its wall, then down-crossing steps 4..7.
# No combinatorial histories: each endpoint follows returned relation.
walls=0
for outn in range(0,7):
 H=BASE+[4]*outn
 _,ho,hA=run(H)
 # detect horizontal wall; still record returned state
 print("OUT",outn,"lvl",ho.levels_completed)
 for dn in range(4,8):
  P=H+[2]*dn
  e,o,A=run(P)
  _,_,pre=run(P[:-1]);m=pre!=A;tr=Counter(zip(pre[m].tolist(),A[m].tolist()))
  print("X",outn,dn,"11>4",tr[(11,4)],"4>11",tr[(4,11)],"11>5",tr[(11,5)],"lvl",o.levels_completed,"state",o.state)
  if o.levels_completed>1: print("SOLVED_ENDPOINT",P);raise SystemExit
  # only at actual exchange states test all continuations
  if tr[(11,4)] or tr[(4,11)]:
   for z in [1,2,3,4,5,7]:
    e,o,A=run(P);q=e.step(GameAction.from_id(z),data={});walls+=1
    if q.levels_completed>1:
     print("SOLVED",P+[z],"walls",walls);raise SystemExit
print("WALLS",walls)
