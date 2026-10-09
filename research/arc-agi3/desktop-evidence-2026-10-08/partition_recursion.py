from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
seqs=[[1,1],[2,2],[1,2],[2,1],[3,3],[4,4],[3,4],[4,3]]
frames={}
for seq in seqs:
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 start=o.frame[0].copy()
 for i in seq:o=e.step(GameAction.from_id(i),data={})
 key=''.join(map(str,seq)); frames[key]=o.frame[0].copy()
 print(key,'changed',np.count_nonzero(start!=o.frame[0]),'L',o.levels_completed,'state',o.state)
for u,v in [('11','22'),('12','21'),('33','44'),('34','43')]:
 p,q=frames[u],frames[v]; ys,xs=np.where(p!=q)
 print('pair',u,v,'diff',len(xs),'bbox',None if len(xs)==0 else (int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())))
