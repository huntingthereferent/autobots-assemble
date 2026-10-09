from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
# Return to exact B8 whole board. Completion witness in L1 was not just same carrier:
# receiver contained marker/provenance. Search cross-color same-envelope relations, including complements/embedded masks.
BASE=[3]*5+[2]*10+[7,5]
e=a.make('ar25');o=None
for z in BASE:o=e.step(GameAction.from_id(z),data={})
B=o.frame[0]
# print 3-lattice sampled nonwhite/non-gray structure as compact map, to expose paired objects without reducing referent for execution
for y in range(0,64,3):
 s=''
 for x in range(0,64,3):
  v=int(B[y,x]); s += {9:'.',0:'K',4:'Y',5:'G',10:'D',11:'N'}.get(v,'?')
 print(f'{y:02}',s)
# For each color bbox/component >=5, report other-color pixels inside its envelope: provenance/marker pairing.
def comps(c):
 M=B==c;seen=set();out=[]
 for y,x in zip(*np.where(M)):
  p=(int(x),int(y))
  if p in seen:continue
  st=[p];seen.add(p);q=[]
  while st:
   X,Y=st.pop();q.append((X,Y))
   for n in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=n[0]<64 and 0<=n[1]<64 and n not in seen and M[n[1],n[0]]:seen.add(n);st.append(n)
  out.append(q)
 return out
for c in [0,4,5,10,11]:
 for q in comps(c):
  if len(q)<5:continue
  x0=min(x for x,y in q);x1=max(x for x,y in q);y0=min(y for x,y in q);y1=max(y for x,y in q)
  co={}
  for y in range(y0,y1+1):
   for x in range(x0,x1+1):
    v=int(B[y,x]);co[v]=co.get(v,0)+1
  print('ENV',c,len(q),(x0,y0,x1,y1),'contents',co)
