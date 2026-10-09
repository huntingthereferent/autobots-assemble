from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25');o=None
for z in [3]*5:o=e.step(GameAction.from_id(z),data={})
def comps(B,c):
 M=B==c; seen=set(); out=[]
 for y,x in zip(*np.where(M)):
  if (x,y) in seen: continue
  st=[(x,y)]; seen.add((x,y)); q=[]
  while st:
   p=st.pop();q.append(p); X,Y=p
   for n in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=n[0]<64 and 0<=n[1]<64 and n not in seen and M[n[1],n[0]]:
     seen.add(n);st.append(n)
  out.append(q)
 return sorted(out,key=len,reverse=True)
for n in range(1,11):
 o=e.step(GameAction.from_id(2),data={});B=o.frame[0]
 print("\nSTEP",n,"LEVEL",o.levels_completed)
 for c in [0,4,5,10,11]:
  C=comps(B,c)
  print(" color",c,[(len(q),(min(x for x,y in q),max(x for x,y in q),min(y for x,y in q),max(y for x,y in q))) for q in C[:6]])
