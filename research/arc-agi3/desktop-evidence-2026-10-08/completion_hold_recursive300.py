from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque
a=Arcade(operation_mode=OperationMode.NORMAL); ROOT=[3]*5+[2]*10+[7,5]+[2]*5+[5]; acts=[1,2,3,4,5,7]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
_,o,A=run(ROOT); seen={A.tobytes():()}; q=deque([()])
edges=0; terminal=0
while q and edges<300:
 h=q.popleft()
 for z in acts:
  e,o,A=run(ROOT+list(h)); r=e.step(GameAction.from_id(z),data={}); B=r.frame[0].copy();edges+=1
  if r.levels_completed>1:
   sol=ROOT+list(h)+[z];print("SOLVED",sol,"edges",edges,"states",len(seen));raise SystemExit
  k=B.tobytes()
  if r.state.name!="NOT_FINISHED": terminal+=1
  elif k not in seen:
   seen[k]=h+(z,);q.append(h+(z,))
  if edges in (100,150,200,250,300):
   print("MARK",edges,"states",len(seen),"frontier",len(q),"terminal",terminal,"depth",len(h)+1)
  if edges>=300:break
print("DONE",edges,"states",len(seen),"frontier",len(q),"terminal",terminal,"maxdepth",max(map(len,seen.values())))
