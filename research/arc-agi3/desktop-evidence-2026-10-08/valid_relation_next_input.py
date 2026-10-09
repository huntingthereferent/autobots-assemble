from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
def mk(seq=[]):
 e=a.make('ar25');o=None
 for z in PRE+seq:o=e.step(GameAction.from_id(z),data={})
 return e,o
# Entry relation is already valid. Test whether "do nothing/confirm" family (7,6)
# can itself close it; and whether 6 is coordinate-independent confirmation at entry.
e,o=mk([])
print("ENTRY",o.levels_completed,o.state)
for act in [7]:
 e,o=mk([])
 for n in range(1,20):
  old=o.frame[0].copy(); o=e.step(GameAction.from_id(act),data={})
  print("A7",n,"diff",np.count_nonzero(old!=o.frame[0]),"lvl",o.levels_completed)
  if o.levels_completed>1: print("SOLVED A7",n); raise SystemExit
# Click/confirm at representative structural points, then wait/confirm.
pts=[(4,46),(52,46),(31,31),(63,14),(30,0)]
for p in pts:
 for tail in ([7],[7,7],[6],[6,7]):
  e,o=mk([])
  o=e.step(GameAction.from_id(6),data={'x':p[0],'y':p[1]})
  ok=True
  for z in tail:
   if z==6:o=e.step(GameAction.from_id(6),data={'x':p[0],'y':p[1]})
   else:o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",p,tail,o.levels_completed); raise SystemExit
  print("WALL",p,tail,o.levels_completed,o.state)
