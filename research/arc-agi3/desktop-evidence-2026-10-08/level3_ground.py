from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
e=a.make('ar25');o=None
for z in SOL:o=e.step(GameAction.from_id(z),data={})
A=o.frame[0].copy()
print("LEVEL",o.levels_completed,"STATE",o.state,"SHAPE",A.shape)
print("COLORS",dict(Counter(A.flatten().tolist())))
# First returned relations only: whole-board differences and resulting level.
for z in [1,2,3,4,5,7]:
 ee=a.make('ar25');q=None
 for x in SOL:q=ee.step(GameAction.from_id(x),data={})
 r=ee.step(GameAction.from_id(z),data={});B=r.frame[0]
 print("A",z,"diff",int(np.count_nonzero(A!=B)),"lvl",r.levels_completed,"state",r.state)
