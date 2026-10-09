from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
frames=[]
for n in range(4):
 o=e.step(GameAction.ACTION5,data={}); frames.append(o.frame[0].copy())
# isolate the recursive 30-cell movement X2->X3->X4
for k in range(1,4):
 p,q=frames[k-1],frames[k]
 ys,xs=np.where(p!=q)
 print('step',k+1,'bbox',(int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())),'n',len(xs))
 # changed old/new color pairs
 vals={}
 for y,x in zip(ys,xs): vals[(int(p[y,x]),int(q[y,x]))]=vals.get((int(p[y,x]),int(q[y,x])),0)+1
 print(vals)
 # centroid of changed coordinates
 print('mean',float(xs.mean()),float(ys.mean()))
