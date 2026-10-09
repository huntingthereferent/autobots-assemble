from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); base=[3]*5+[2]*10+[5]
# Recurse on the surviving relation itself: compare P^n whole states for both
# representations P12 and P34, and inspect the one-step A5 relation at each earned depth.
def state(pair,n,tail=[]):
 e=a.make('ar25')
 for i in base:o=e.step(GameAction.from_id(i),data={})
 for _ in range(n):
  for i in pair:o=e.step(GameAction.from_id(i),data={})
 for i in tail:o=e.step(GameAction.from_id(i),data={})
 return o
for n in [1,2,4,8,16,24,30,31]:
 x=state([1,2],n); y=state([3,4],n)
 dxy=np.count_nonzero(x.frame[0]!=y.frame[0])
 z=state([1,2],n,[5])
 dz=np.count_nonzero(x.frame[0]!=z.frame[0]) if len(z.frame) else -1
 print('n',n,'P12=P34 diff',dxy,'A5diff',dz,'A5L',z.levels_completed,'A5state',z.state)
