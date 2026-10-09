from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); pre=[3]*5+[2]*10
# Correct previous assumption: reciprocal closure is NOT an exact cycle.
# Recurse the same witnessed alternating boundary movement and inspect each returned whole state.
patterns=[('34',[3]*13+[4]*21),('43',[4]*9+[3]*21)]
for name,unit in patterns:
 e=a.make('ar25')
 for z in pre:o=e.step(GameAction.from_id(z),data={})
 prev=o.frame[0].copy()
 print("\nPATTERN",name)
 for k in range(1,20):
  for z in unit:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",name,"repeat",k,"lvl",o.levels_completed,o.state); raise SystemExit
   if 'GAME_OVER' in str(o.state):
    print("GAME_OVER",name,"repeat",k); break
  cur=o.frame[0].copy()
  print("return",k,"diff_from_prior_return",np.count_nonzero(prev!=cur),"lvl",o.levels_completed,o.state)
  if 'GAME_OVER' in str(o.state) or np.array_equal(prev,cur): break
  prev=cur
