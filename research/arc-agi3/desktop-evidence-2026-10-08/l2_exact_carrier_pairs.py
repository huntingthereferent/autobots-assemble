from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
e=a.make('ar25');o=None
for z in PRE+[7,5]:o=e.step(GameAction.from_id(z),data={})
B=o.frame[0].copy()
# completion contract: exact normalized occupancy match between movable carrier and fixed receiver.
# Enumerate connected non-background components in returned whole board, preserving coordinates.
def comps(B,c):
 M=B==c;seen=set();out=[]
 for y,x in zip(*np.where(M)):
  if (x,y) in seen:continue
  st=[(x,y)];seen.add((x,y));q=[]
  while st:
   X,Y=st.pop();q.append((X,Y))
   for n in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=n[0]<64 and 0<=n[1]<64 and n not in seen and M[n[1],n[0]]:
     seen.add(n);st.append(n)
  out.append(q)
 return out
def norm(q):
 x0=min(x for x,y in q);y0=min(y for x,y in q)
 return frozenset((x-x0,y-y0) for x,y in q)
items=[]
for c in sorted(set(map(int,B.ravel()))):
 if c==9:continue
 for q in comps(B,c):
  if len(q)>=3:
   items.append((c,len(q),(min(x for x,y in q),min(y for x,y in q),max(x for x,y in q),max(y for x,y in q)),norm(q)))
for i,A in enumerate(items):
 for j,C in enumerate(items[i+1:],i+1):
  if A[3]==C[3]:
   print("EXACT_PAIR",i,j,"A",A[:3],"B",C[:3])
print("COMPONENTS")
for i,x in enumerate(items): print(i,x[:3])
