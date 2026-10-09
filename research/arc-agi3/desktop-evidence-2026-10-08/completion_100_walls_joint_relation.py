from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, hashlib
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]
# Completion-focused 100 walls: derive 10 distinct board-returned parent states along the witnessed
# joint descent (A2^0..9), and at each test 10 short continuations built only from permitted
# simple relations: 1,2,3,4,5,7 and witnessed two-step corrections. Stop immediately on L2 closure.
cont=[[1],[2],[3],[4],[5],[7],[1,2],[2,1],[3,4],[4,3]]
walls=0; seen={}
for k in range(10):
 parent=BASE+[2]*k
 for u in cont:
  e=a.make('ar25');o=None
  for z in parent+u:
   o=e.step(GameAction.from_id(z),data={})
   if o.levels_completed>1:
    print("SOLVED",parent[len(BASE):],u,"FULL",parent+u,"lvl",o.levels_completed);raise SystemExit
  A=o.frame[0]; h=hashlib.sha1(A.tobytes()).hexdigest()[:10]
  yy,xx=np.where(A==0); kb=None if not len(xx) else (int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),len(xx))
  yy,xx=np.where(A==4); yb=None if not len(xx) else (int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()),len(xx))
  walls+=1;seen[h]=seen.get(h,0)+1
  print("W",walls,"P",k,"U",''.join(map(str,u)),"H",h,"Y",yb,"K",kb,"lvl",o.levels_completed,o.state)
print("TOTAL_WALLS",walls,"UNIQUE_RETURNED",len(seen),"NO_L2_CLOSURE")
