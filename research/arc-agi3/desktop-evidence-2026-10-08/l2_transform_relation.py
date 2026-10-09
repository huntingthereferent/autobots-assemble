from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# determine exact normalized transforms between carrier/dot pairs
sets={}
for c in [0,4,5,11]:
 ys,xs=np.where(b==c)
 pts={(int(x),int(y)) for y,x in zip(ys,xs) if x<63 and y<63 and not 35<=x<=39}
 sets[c]=pts
def norm(s):
 mx=min(x for x,y in s); my=min(y for x,y in s)
 return {(x-mx,y-my) for x,y in s}
def transforms(s):
 s=norm(s); W=max(x for x,y in s); H=max(y for x,y in s)
 return {'id':s,'flipx':{(W-x,y) for x,y in s},'flipy':{(x,H-y) for x,y in s},'rot180':{(W-x,H-y) for x,y in s},'transpose':{(y,x) for x,y in s}}
for a1,a2 in [(5,4),(0,11)]:
 print('PAIR',a1,a2)
 target=norm(sets[a2])
 for name,s in transforms(sets[a1]).items():
  print(name, s==target, 'diff',len(s^target))
