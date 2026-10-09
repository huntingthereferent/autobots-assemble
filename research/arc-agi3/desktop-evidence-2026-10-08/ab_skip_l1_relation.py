from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); L1=[3]*5+[2]*10
# A/B skip: carry the solved L1 relation one layer up, not the lower action algebra.
# Re-expression first (7 is in the earned common first-step class), then test only symmetry images
# of the already-solved orthogonal 5/10 relation.
pairs=[(3,2),(4,2),(3,1),(4,1),(2,3),(2,4),(1,3),(1,4)]
for p,q in pairs:
 e=a.make('ar25')
 for x in L1:o=e.step(GameAction.from_id(x),data={})
 o=e.step(GameAction.ACTION7,data={})
 for x in [p]*5+[q]*10:
  o=e.step(GameAction.from_id(x),data={})
  if o.levels_completed>1 or 'GAME_OVER' in str(o.state): break
 print('carry',p,q,'=>',o.levels_completed,o.state)
 if o.levels_completed>1:
  print('SOLVED L2', [7]+[p]*5+[q]*10); break
