from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
# Compare L1 immediately before completion and exact returned L2, extracting all non-background component envelopes.
for name,seq in [('L1PRE',[3]*5+[2]*9),('L1CLOSE',[3]*5+[2]*10),('L2B8',[3]*5+[2]*10+[7,5])]:
 A,o=run(seq); print('\n',name,'lvl',o.levels_completed)
 for c in [0,4,5,10,11]:
  M=A==c;seen=set()
  for y,x in zip(*np.where(M)):
   p=(int(x),int(y))
   if p in seen:continue
   st=[p];seen.add(p);q=[]
   while st:
    X,Y=st.pop();q.append((X,Y))
    for n in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
     if 0<=n[0]<64 and 0<=n[1]<64 and n not in seen and M[n[1],n[0]]:seen.add(n);st.append(n)
   if len(q)>=4:
    bb=(min(x for x,y in q),min(y for x,y in q),max(x for x,y in q),max(y for x,y in q))
    # contents in bbox
    co={}
    for yy in range(bb[1],bb[3]+1):
     for xx in range(bb[0],bb[2]+1):
      v=int(A[yy,xx]);co[v]=co.get(v,0)+1
    print(' ',c,len(q),bb,'env',co)
