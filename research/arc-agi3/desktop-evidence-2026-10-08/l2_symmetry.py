from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
# Whole-board relation is explicit: same oriented L on opposite sides, one gray template and one yellow.
# Bring them into the same relative relation to divider: paired actions move both, so test closure by symmetry,
# not an action grid. Initial centers approx x=89 and 666 around divider x=378 -> horizontal distances 289/288 already matched.
# y centers approx 594 both -> vertical relation already matched. Thus level2 starts ALIGNED; invoke the layer transition.
for aid in [5,7]:
 o=e.step(GameAction.from_id(aid),data={}); print('transition',aid,'L',o.levels_completed,o.state)
