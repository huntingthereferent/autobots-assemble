from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# A/B: returned output is next input. No naming/selection layer.
# Build the two exact late outputs already earned, then apply the same witness contract directly.
parents={
 'A':([3]*13+[4]*21)*2+[7]*59,
 'B':([4]*9+[3]*21)*2+[7]*47,
}
for name,p in parents.items():
 print("\nRETURN",name)
 for act in [1,2,3,4,5,7]:
  e=a.make('ar25')
  for z in pre+p:o=e.step(GameAction.from_id(z),data={})
  x=o.frame[0].copy()
  o=e.step(GameAction.from_id(act),data={}); y=o.frame[0].copy()
  print(act,np.count_nonzero(x!=y),o.levels_completed,o.state)
  if o.levels_completed>1:
   print("SOLVED",name,act); raise SystemExit
