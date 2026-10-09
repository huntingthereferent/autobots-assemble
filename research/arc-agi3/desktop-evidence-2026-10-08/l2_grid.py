from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
for h in range(-8,9):
 for v in range(-8,9):
  e=a.make('ar25')
  for i in base: o=e.step(GameAction.from_id(i),data={})
  hs=([3]*h if h>0 else [4]*(-h)); vs=([2]*v if v>0 else [1]*(-v))
  for i in hs+vs:
   o=e.step(GameAction.from_id(i),data={})
   if o.levels_completed>1: break
  if o.levels_completed>1:
   print('SOLVED2',h,v,len(hs)+len(vs)); raise SystemExit
print('none')
