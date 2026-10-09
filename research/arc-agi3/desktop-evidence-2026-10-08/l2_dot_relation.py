from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
# Exact board shows paired 9x9 Ls: gray contains black dots; yellow contains navy dots.
# Dot patterns are mirror-opposed: left dots top arm+right leg, right dots top arm+left leg.
# Test the earned horizontal relation: ACTION4 moves them toward each other (left structure right, right structure left).
for n in range(1,9):
 o=e.step(GameAction.ACTION4,data={}); print(n,o.levels_completed,o.state)
 if o.levels_completed>1: break
