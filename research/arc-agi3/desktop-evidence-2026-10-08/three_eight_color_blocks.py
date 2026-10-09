from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)
BASE=[3]*5+[2]*10+[7,5]+[2]*4
# From immediately before first witnessed internal 11->4 block, follow only returned-state
# continuations that can move the overlap block across navy. Track CURRENT yellow-on-original-navy
# occupancy rather than transition counts. Test 10 earned branches, stop on closure.
branches=[[2],[2,4],[2,4,4],[2,3],[2,3,3],[2,2],[2,2,4],[2,2,3],[2,4,2],[2,3,2]]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return o.frame[0],o
P,_=run(BASE)
origN=P==11
for i,b in enumerate(branches,1):
 A,o=run(BASE+b)
 overlap=np.argwhere(origN&(A==4))
 pts=[(int(x),int(y)) for y,x in overlap]
 # connected groups of overlap in 4-neighbor grid
 S=set(pts); groups=[]
 while S:
  st=[S.pop()];g=[]
  while st:
   p=st.pop();g.append(p);x,y=p
   for q in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if q in S:S.remove(q);st.append(q)
  groups.append(g)
 print('W',i,'branch',b,'lvl',o.levels_completed,'NtoY_current',len(pts),'groups',sorted(map(len,groups),reverse=True),'pts',pts)
 if o.levels_completed>1:
  print('SOLVED',BASE+b);break
