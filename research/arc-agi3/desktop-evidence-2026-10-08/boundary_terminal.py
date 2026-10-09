from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10+[5]: o=e.step(GameAction.from_id(i),data={})
for n in range(1,34):
 for j,i in enumerate([1,2],1):
  o=e.step(GameAction.from_id(i),data={})
  print('pair',n,'half',j,'act',i,'L',o.levels_completed,'state',o.state,'frames',len(o.frame))
  if len(o.frame)==0 or 'GAME_OVER' in str(o.state) or o.levels_completed>1: raise SystemExit
