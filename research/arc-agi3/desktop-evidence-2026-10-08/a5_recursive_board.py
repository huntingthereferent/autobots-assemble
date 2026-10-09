from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
# Inspect action5 as relation on the returned whole state: it previously caused a large transform.
e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
p=o.frame[0].copy(); o=e.step(GameAction.ACTION5,data={}); q=o.frame[0].copy()
print('A5 changed',np.count_nonzero(p!=q),'level',o.levels_completed)
for c in sorted(set(np.unique(p)).union(np.unique(q))):
 yp,xp=np.where(p==c); yq,xq=np.where(q==c)
 def bb(xs,ys): return None if len(xs)==0 else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max()),len(xs))
 print(int(c),bb(xp,yp),'->',bb(xq,yq))
# Apply A5 again: same permitted operation on its own returned board.
o2=e.step(GameAction.ACTION5,data={}); r=o2.frame[0]
print('A5 again changed',np.count_nonzero(q!=r),'level',o2.levels_completed,'state',o2.state)
print('returns_to_prior',np.array_equal(r,p))
