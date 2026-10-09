from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# Returned reciprocal closures, then ask the whole returned state which relations survive.
parents={
 '3*4*':[3]*13+[4]*21,
 '4*3*':[4]*9+[3]*21,
 '3*7*':[3]*13+[7]*13,
 '4*7*':[4]*9+[7]*9,
}
for name,p in parents.items():
 print("\nBOUNDARY",name)
 # exact parent board
 e=a.make('ar25')
 for z in pre+p:o=e.step(GameAction.from_id(z),data={})
 base=o.frame[0].copy()
 print(" parent",o.levels_completed,o.state)
 for act in [1,2,3,4,5,7]:
  ee=a.make('ar25')
  for z in pre+p:oo=ee.step(GameAction.from_id(z),data={})
  b=oo.frame[0].copy(); oo=ee.step(GameAction.from_id(act),data={}); c=oo.frame[0].copy()
  print(" next",act,"diff",np.count_nonzero(b!=c),"lvl",oo.levels_completed,oo.state)
  if oo.levels_completed>1:
   print("SOLVED L2",p+[act]); raise SystemExit
