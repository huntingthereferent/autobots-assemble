from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
base=[3]*5+[2]*10
# Whole board exposes two boundary endpoints: right edge changes gray->navy at y14; bottom is gray.
# Pair is at y45..53. Level1 closed by moving downward, toward bottom boundary.
# Continue that SAME earned relation on returned board, not arbitrary action search.
e=a.make('ar25')
for i in base: o=e.step(GameAction.from_id(i),data={})
for n in range(1,5):
 o=e.step(GameAction.ACTION2,data={})
 print('down',n,'L',o.levels_completed,o.state)
 if o.levels_completed>1: break
