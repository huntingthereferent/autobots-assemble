from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
# The commutator partitions actions into {1,2} and {3,4}. Compare opposite members recursively:
# A1 vs A2, A3 vs A4 from same whole state.
frames={}
for act in [1,2,3,4]:
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 o=e.step(GameAction.from_id(act),data={}); frames[act]=o.frame[0].copy()
for u,v in [(1,2),(3,4),(1,3),(2,4)]:
 p,q=frames[u],frames[v]; ys,xs=np.where(p!=q)
 print(u,v,'difference',len(xs),'bbox',None if len(xs)==0 else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
 # symmetry of counts by color transitions
 pairs={}
 for y,x in zip(ys,xs): pairs[(int(p[y,x]),int(q[y,x]))]=pairs.get((int(p[y,x]),int(q[y,x])),0)+1
 print(pairs)
