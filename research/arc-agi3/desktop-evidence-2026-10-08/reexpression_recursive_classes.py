from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); solve=[3]*5+[2]*10
def get(first,second=None):
 e=a.make('ar25')
 for i in solve:o=e.step(GameAction.from_id(i),data={})
 for i in [first]+([] if second is None else [second]):o=e.step(GameAction.from_id(i),data={})
 return o.frame[0].copy(),o
# The first action is now an earned relation: R_a = AB(returned,a).
# Compare every returned whole board directly; then ask whether the SAME next action
# collapses their differences one layer later.
first={i:get(i)[0] for i in [1,2,3,4,5,7]}
print('FIRST-RETURNED PAIRWISE')
for i in first:
 for j in first:
  if i<j:
   ys,xs=np.where(first[i]!=first[j])
   print(i,j,len(xs),None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
print('SAME SECOND ACTION ACROSS FIRST WITNESSES')
for second in [1,2,3,4,5,7]:
 boards={i:get(i,second)[0] for i in [1,2,3,4,5,7]}
 # number of distinct boards by exact bytes
 groups={}
 for i,b in boards.items(): groups.setdefault(b.tobytes(),[]).append(i)
 print('second',second,'groups',list(groups.values()))
