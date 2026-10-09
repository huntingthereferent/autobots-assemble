from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25');o=None
for z in [3]*5+[2]*10:o=e.step(GameAction.from_id(z),data={})
print("before",o.levels_completed,o.state)
for name in ["RESET"]:
 try:
  x=e.step(getattr(GameAction,name),data={})
  print(name,x.levels_completed,x.state)
 except Exception as q: print(name,"ERR",type(q).__name__,q)
