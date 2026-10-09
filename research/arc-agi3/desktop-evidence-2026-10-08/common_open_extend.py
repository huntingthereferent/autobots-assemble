from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10+[7]
for u in ([3,7],[4,7],[3,5],[5,3],[4,5],[5,4]):
 e=a.make('ar25'); o=None
 for z in PRE:o=e.step(GameAction.from_id(z),data={})
 print("\nOPEN",u)
 for n in range(1,100):
  for z in u:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",u,n,z,o.levels_completed,o.state); raise SystemExit
   if 'GAME_OVER' in str(o.state):
    print("WALL GAME_OVER",n,z); break
  if 'GAME_OVER' in str(o.state): break
 else: print("OPEN100")
