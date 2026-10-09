from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# Swallow ALL nonwhite connected components, including boundary-attached colors.
seen=set()
for c in np.unique(b):
 if c==9: continue
 mask=b==c
 for y,x in zip(*np.where(mask)):
  if (x,y) in seen: continue
  stack=[(x,y)]; seen.add((x,y)); comp=[]
  while stack:
   X,Y=stack.pop(); comp.append((X,Y))
   for X2,Y2 in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=X2<64 and 0<=Y2<64 and mask[Y2,X2] and (X2,Y2) not in seen:
     seen.add((X2,Y2)); stack.append((X2,Y2))
  print('c',int(c),'n',len(comp),'bbox',(min(x for x,y in comp),max(x for x,y in comp),min(y for x,y in comp),max(y for x,y in comp)))
