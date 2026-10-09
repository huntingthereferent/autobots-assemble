from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]; P=[1,2]
def frame(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 root=o.frame[0].copy()
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame:return None,o,root
 return o.frame[0].copy(),o,root
# Test what A5^2 actually is as a whole-state operator, then recurse Q=55.
for m in range(1,9):
 f,o,r=frame([5]*m)
 if f is None: print('5^',m,'terminal',o.state);continue
 ys,xs=np.where(r!=f)
 print('5^',m,'diffbase',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),'L',o.levels_completed,o.state)
# Q recursion and interaction with a single 5
for q in range(1,9):
 f,o,r=frame([5,5]*q)
 if f is None: print('Q',q,'terminal');break
 print('Q',q,'diffbase',np.count_nonzero(r!=f),'L',o.levels_completed,o.state)
