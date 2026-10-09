from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
parents={
 'A':([3]*13+[4]*21)*2+[7]*59,
 'B':([4]*9+[3]*21)*2+[7]*47,
}
# Directly recurse newly witnessed x --(3/4)--> x' --7--> x''.
for name,p in parents.items():
 for first in [3,4]:
  seq=p+[first,7]
  e=a.make('ar25')
  for z in pre+seq:o=e.step(GameAction.from_id(z),data={})
  x=o.frame[0].copy()
  print("\nRETURN",name,first,"7",o.levels_completed,o.state)
  if o.levels_completed>1:
   print("SOLVED",name,first,7); raise SystemExit
  for act in [1,2,3,4,5,7]:
   ee=a.make('ar25')
   for z in pre+seq:oo=ee.step(GameAction.from_id(z),data={})
   b=oo.frame[0].copy(); oo=ee.step(GameAction.from_id(act),data={}); c=oo.frame[0].copy()
   print(" next",act,"diff",np.count_nonzero(b!=c),"lvl",oo.levels_completed,oo.state)
   if oo.levels_completed>1:
    print("SOLVED",name,first,7,act); raise SystemExit
