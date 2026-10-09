from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
def run(seq):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for i in seq:
  o=e.step(GameAction.from_id(i),data={})
  if not o.frame: break
 return o
# Q=55 and P=12 both reduce to 2-cell boundary advance. Test whole-state equality recursively.
for n in [1,2,3,4,8,16,24,30,31]:
 p=run([1,2]*n); q=run([5,5]*n)
 if not p.frame or not q.frame: print(n,'terminal');continue
 ys,xs=np.where(p.frame[0]!=q.frame[0])
 print(n,'P_vs_Q',len(xs),'bbox',None if not len(xs) else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),'states',p.state,q.state)
