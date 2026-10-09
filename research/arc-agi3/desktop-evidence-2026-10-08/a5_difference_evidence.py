from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10:o=e.step(GameAction.from_id(i),data={})
# one A5 reaches re-expressed state; second reveals carried 30-cell relation.
o=e.step(GameAction.ACTION5,data={}); x=o.frame[0].copy()
o=e.step(GameAction.ACTION5,data={}); y=o.frame[0].copy()
print('status after recursive pair',o.levels_completed,o.state)
# The repeated difference itself: coordinates changed X->Y. Check whether applying native translations
# to X aligns that difference with colored structures/boundaries, without choosing a goal.
ys,xs=np.where(x!=y)
coords=list(zip(xs.tolist(),ys.tolist()))
print('diff coords',coords)
# group changed coords by old/new pair
for pair in sorted(set((int(x[yy,xx]),int(y[yy,xx])) for xx,yy in coords)):
 pts=[(xx,yy) for xx,yy in coords if (int(x[yy,xx]),int(y[yy,xx]))==pair]
 print(pair,pts)
