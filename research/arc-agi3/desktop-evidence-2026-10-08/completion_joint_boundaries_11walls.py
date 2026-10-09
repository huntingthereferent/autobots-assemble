from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); B=[3]*5+[2]*10+[7,5]
# Earned walls define rectangle for coupled pair: left wall via A4 once, horizontal opposite pair;
# vertical positions. Test completion-relevant CORNERS/registration of the other half, not grid.
# Four boundary-directed trajectories from B8: left/right walls x, top/bottom walls y, both orders.
units=[
 [4]+[1]*20,[4]+[2]*20,[3]*20+[1]*20,[3]*20+[2]*20,
 [1]*20+[4]*20,[2]*20+[4]*20,[1]*20+[3]*20,[2]*20+[3]*20,
 [4]+[2]*8+[3]*20,[4]+[2]*8+[5],[4]+[2]*8+[7]
]
for j,seq in enumerate(units,1):
 e=a.make('ar25');o=None
 for z in B:o=e.step(GameAction.from_id(z),data={})
 for i,z in enumerate(seq):
  o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>1:
   print("SOLVED",j,seq[:i+1],"LEVEL",o.levels_completed);raise SystemExit
  if 'GAME_OVER' in str(o.state): break
 print("WALL",j,"lvl",o.levels_completed,"state",o.state)
print("NO_CLOSE")
