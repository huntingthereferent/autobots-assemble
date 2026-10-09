from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import Counter
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
# Positive L1 closing transition is our color witness.
p,_=run([3]*5+[2]*9); q,_=run([3]*5+[2]*10)
D=p!=q; target=Counter(zip(p[D].tolist(),q[D].tolist()))
print("TARGET",target)
# At each L2 descent layer test each simple action by exact color transition multiset.
# Report distance from positive transition only diagnostically; stop if exact/subset structural color relation appears.
for k in range(12):
 A,_=run(BASE+[2]*k)
 for act in [1,2,3,4,5,7]:
  B,o=run(BASE+[2]*k+[act]); M=A!=B
  tr=Counter(zip(A[M].tolist(),B[M].tolist()))
  # focus positive closure's directed color edges
  sig=tuple(tr[x] for x in [(11,4),(4,9),(5,9),(9,5),(0,9),(9,0)])
  rev=tuple(tr[x] for x in [(4,11),(9,4),(9,5),(5,9),(9,0),(0,9)])
  print("K",k,"A",act,"lvl",o.levels_completed,"SIG",sig,"REV",rev,"ALL",dict(tr))
  if o.levels_completed>1: print("SOLVED",k,act);raise SystemExit
