from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
TARGET=(3,42)
def mover(A):
 # color4 largest comp bbox anchor
 M=A==4; seen=set(); best=[]
 for y,x in zip(*np.where(M)):
  p=(int(x),int(y))
  if p in seen:continue
  st=[p];seen.add(p);q=[]
  while st:
   X,Y=st.pop();q.append((X,Y))
   for n in ((X+1,Y),(X-1,Y),(X,Y+1),(X,Y-1)):
    if 0<=n[0]<64 and 0<=n[1]<64 and n not in seen and M[n[1],n[0]]:seen.add(n);st.append(n)
  if len(q)>len(best):best=q
 return len(best),(min(x for x,y in best),min(y for x,y in best)),(max(x for x,y in best),max(y for x,y in best))
e=a.make('ar25');o=None
for z in BASE:o=e.step(GameAction.from_id(z),data={})
print("START",mover(o.frame[0]))
seq=[]
# At each returned whole board, test each simple action on a fresh replay of current history;
# choose only action that preserves 72-shape and strictly reduces anchor Manhattan distance to fixed receiver.
for step in range(30):
 A=o.frame[0]; cur=mover(A); dist=abs(cur[1][0]-3)+abs(cur[1][1]-42)
 print("STEP",step,"cur",cur,"dist",dist,"seq",seq)
 if cur[0]==72 and cur[1]==TARGET: print("REGISTERED",seq);break
 cand=[]
 for act in [1,2,3,4]:
  ee=a.make('ar25');oo=None
  for z in BASE+seq+[act]:oo=ee.step(GameAction.from_id(z),data={})
  mm=mover(oo.frame[0]); dd=abs(mm[1][0]-3)+abs(mm[1][1]-42)
  cand.append((dd,act,mm,oo.levels_completed,oo.state))
 print(" CAND",cand)
 good=[x for x in cand if x[2][0]==72 and x[0]<dist]
 if not good: print("NO_DESCENT");break
 _,act,_,_,_=min(good)
 seq.append(act);o=e.step(GameAction.from_id(act),data={})
 if o.levels_completed>1: print("SOLVED",seq,o.levels_completed);break
