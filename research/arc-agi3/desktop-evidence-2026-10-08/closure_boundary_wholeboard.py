from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]+[2]*4+[4]
e=a.make('ar25');o=None
for z in BASE:o=e.step(GameAction.from_id(z),data={})
B=o.frame[0].copy()
# Whole-board closure boundary: enumerate exact normalized-shape correspondences now, not inherited 72 assumption.
def comps(A,c):
 M=A==c;seen=set();out=[]
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
def norm(q):
 x0=min(x for x,y in q);y0=min(y for x,y in q)
 return frozenset((x-x0,y-y0) for x,y in q)
items=[]
for c in sorted(set(map(int,B.ravel()))):
 if c==9:continue
 for q in comps(B,c):
  if len(q)>=3:items.append((c,len(q),(min(x for x,y in q),min(y for x,y in q),max(x for x,y in q),max(y for x,y in q)),norm(q)))
print("BOUNDARY lvl",o.levels_completed)
for i,x in enumerate(items):print("C",i,x[:3])
print("EXACT PAIRS")
for i,A in enumerate(items):
 for j,C in enumerate(items[i+1:],i+1):
  if A[3]==C[3]:print(i,j,A[:3],C[:3])
# Returned-state action witnesses: see which exact correspondences survive/appear after each permitted simple action.
for act in [1,2,3,4,5,7]:
 ee=a.make('ar25');oo=None
 for z in BASE+[act]:oo=ee.step(GameAction.from_id(z),data={})
 A=oo.frame[0]
 its=[]
 for c in sorted(set(map(int,A.ravel()))):
  if c==9:continue
  for q in comps(A,c):
   if len(q)>=3:its.append((c,len(q),(min(x for x,y in q),min(y for x,y in q),max(x for x,y in q),max(y for x,y in q)),norm(q)))
 pairs=[(x[:3],y[:3]) for ii,x in enumerate(its) for y in its[ii+1:] if x[3]==y[3]]
 print("ACT",act,"lvl",oo.levels_completed,"pairs",pairs)
