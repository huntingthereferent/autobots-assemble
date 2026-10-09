from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter,deque
a=Arcade(operation_mode=OperationMode.NORMAL); ROOT=[3]*5+[2]*10+[7,5]+[2]*5+[5]
acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
# Recursive returned-board audit from crossing->A5 hold.
# Collapse exact duplicate returned boards; 100 distinct relation edges max.
e,o,A=run(ROOT); seen={A.tobytes():()}; q=deque([((),A)])
edges=0
while q and edges<100:
 hist,parent=q.popleft()
 for z in acts:
  e,o,A=run(ROOT+list(hist)); r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy(); edges+=1
  if r.levels_completed>1:
   print("SOLVED",ROOT+list(hist)+( [z] ),"edges",edges);raise SystemExit
  key=B.tobytes(); new=key not in seen
  print("E",edges,"h",hist,"a",z,"diff",int(np.sum(A!=B)),"new",new,"state",r.state)
  if new and r.state.name=="NOT_FINISHED":
   seen[key]=hist+(z,);q.append((hist+(z,),B))
  if edges>=100:break
print("DONE edges",edges,"states",len(seen),"frontier",len(q))
