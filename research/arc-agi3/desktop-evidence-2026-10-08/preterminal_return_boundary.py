from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# Continue from each second reciprocal return (last valid returned input before the
# third same reciprocal application terminates). Ask that exact whole state which
# permitted relations survive; no boundary-type substitution.
parents={
 '34x2':([3]*13+[4]*21)*2,
 '43x2':([4]*9+[3]*21)*2,
}
for name,p in parents.items():
 print("\nPARENT",name)
 e=a.make('ar25')
 for z in pre+p:o=e.step(GameAction.from_id(z),data={})
 print("state",o.levels_completed,o.state)
 for act in [1,2,3,4,5,7]:
  ee=a.make('ar25')
  for z in pre+p:oo=ee.step(GameAction.from_id(z),data={})
  b=oo.frame[0].copy(); oo=ee.step(GameAction.from_id(act),data={}); c=oo.frame[0].copy()
  print(" next",act,"diff",np.count_nonzero(b!=c),"lvl",oo.levels_completed,oo.state)
  if oo.levels_completed>1:
   print("SOLVED",name,act); raise SystemExit
