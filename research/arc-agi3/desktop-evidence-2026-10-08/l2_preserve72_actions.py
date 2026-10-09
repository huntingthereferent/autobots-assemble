from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def state(extra):
 e=a.make('ar25');o=None
 for z in BASE+extra:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0].copy(),o
B,_=state([])
# exact 72 color4 component coordinates
def comps(A,c):
 M=A==c;seen=set();out=[]
 for y,x in zip(*np.where(M)):
  if (int(x),int(y)) in seen:continue
  st=[(int(x),int(y))];seen.add(st[0]);q=[]
  while st:
   X,Y=st.pop();q.append((X,Y))
   for p in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=p[0]<64 and 0<=p[1]<64 and p not in seen and M[p[1],p[0]]:seen.add(p);st.append(p)
  out.append(q)
 return out
def norm(q):
 x0=min(x for x,y in q);y0=min(y for x,y in q)
 return frozenset((x-x0,y-y0) for x,y in q)
Q=max(comps(B,4),key=len); NQ=norm(Q)
print("ROOT72",(min(x for x,y in Q),max(x for x,y in Q),min(y for x,y in Q),max(y for x,y in Q)))
for act in [1,2,3,4,5,7]:
 A,o=state([act]); matches=[]
 for c in [0,4,5,10,11]:
  for q in comps(A,c):
   if len(q)==72 and norm(q)==NQ:
    matches.append((c,(min(x for x,y in q),max(x for x,y in q),min(y for x,y in q),max(y for x,y in q))))
 print("ACT",act,"lvl",o.levels_completed,"preserved72",matches)
