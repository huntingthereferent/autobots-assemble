from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# exact divider coordinates/color counts and fixed boundaries
for c in np.unique(b):
 ys,xs=np.where(b==c)
 if c in [10,11,5]:
  print('C',int(c),'n',len(xs),'xuniq',sorted(set(xs.tolist())),'yuniq',sorted(set(ys.tolist()))[:10],sorted(set(ys.tolist()))[-10:])
