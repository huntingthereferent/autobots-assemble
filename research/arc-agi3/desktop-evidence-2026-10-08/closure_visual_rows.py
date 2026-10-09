from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25');o=None
for z in [3]*5+[2]*9:o=e.step(GameAction.from_id(z),data={})
A=o.frame[0].copy()
o=e.step(GameAction.from_id(2),data={});B=o.frame[0].copy()
# print only changed local patches, preserving actual cells
for name,M in [('PRE',A),('RET',B)]:
 print(name)
 for y in range(40,55):
  print(y,''.join(' .0123456789AB'[int(v)+1] if int(v)<12 else '?' for v in M[y,0:64]))
