from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
base=[3]*5+[2]*10+[5]
tests=[[3]*7+[2]*9,[4]*7+[2]*9,[3]*7+[1]*9,[4]*7+[1]*9,[3]*5+[2]*10]
for j,t in enumerate(tests):
 e=a.make('ar25')
 for i in base: o=e.step(GameAction.from_id(i),data={})
 for n,i in enumerate(t,1):
  o=e.step(GameAction.from_id(i),data={})
  if o.levels_completed>1: break
 print(j,t[0] if t else None,'len',n,'L',o.levels_completed)
