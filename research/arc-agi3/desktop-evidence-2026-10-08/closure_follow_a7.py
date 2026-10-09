from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]+[2]*4+[4]
def largest4(A):
 M=A==4;seen=set();best=[]
 for y,x in zip(*np.where(M)):
  p=(int(x),int(y))
  if p in seen:continue
  st=[p];seen.add(p);q=[]
  while st:
   X,Y=st.pop();q.append((X,Y))
   for n in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=n[0]<64 and 0<=n[1]<64 and n not in seen and M[n[1],n[0]]:seen.add(n);st.append(n)
  if len(q)>len(best):best=q
 return len(best),(min(x for x,y in best),min(y for x,y in best),max(x for x,y in best),max(y for x,y in best))
# follow A7 returned state, then recursively inspect simple actions for preserved 72 pair and movement.
for k in range(1,7):
 e=a.make('ar25');o=None
 for z in BASE+[7]*k:o=e.step(GameAction.from_id(z),data={})
 print("A7^",k,"mover",largest4(o.frame[0]),"lvl",o.levels_completed)
 for act in [1,2,3,4,5,7]:
  ee=a.make('ar25');oo=None
  for z in BASE+[7]*k+[act]:oo=ee.step(GameAction.from_id(z),data={})
  print(" ",act,largest4(oo.frame[0]),oo.levels_completed,oo.state)
