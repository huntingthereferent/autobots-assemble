from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
# parent immediately before first internal yellow/navy overlap
ROOT=[3]*5+[2]*10+[7,5]+[2]*4
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
R,_=run(ROOT); origN=R==11
# Track exact yellow-on-original-navy masks together with black-marker mask.
# BFS only over novel witnessed (color-mask, black-mask, whole-state) relations, depth <=5.
from collections import deque
def key(A):
 yn=np.argwhere(origN&(A==4))
 bk=np.argwhere(A==0)
 return (tuple(map(tuple,yn.tolist())),tuple(map(tuple,bk.tolist())),A.tobytes())
q=deque([([],R)]); seen={key(R)}; walls=0
while q and walls<100:
 hist,A=q.popleft()
 if len(hist)>=5: continue
 for act in [1,2,3,4,5,7]:
  B,o=run(ROOT+hist+[act]); k=key(B)
  if k in seen: continue
  seen.add(k); walls+=1
  yn=[(int(x),int(y)) for y,x in np.argwhere(origN&(B==4))]
  bk=[(int(x),int(y)) for y,x in np.argwhere(B==0)]
  print('W',walls,'h',hist+[act],'lvl',o.levels_completed,'YN',len(yn),'BLACK',len(bk),'YNPTS',yn)
  if o.levels_completed>1:
   print('SOLVED',ROOT+hist+[act]);raise SystemExit
  q.append((hist+[act],B))
print('DONE walls',walls,'novel',len(seen),'queue',len(q))
