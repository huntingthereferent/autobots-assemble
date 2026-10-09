from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def run(seq):
 e=a.make('ar25');o=None
 for z in seq:o=e.step(GameAction.from_id(z),data={})
 return e,o,o.frame[0].copy()
def sig(A):
 return {c:int(np.sum(A==c)) for c in [0,4,5,9,10,11]}
# Follow the actual 72->45 transition at y42. Find exact first inward step causing it.
parent=BASE+[2]*8
e,o,A=run(parent)
print("PARENT",sig(A),o.levels_completed)
seq=[]
for i in range(1,8):
 pre=A.copy(); o=e.step(GameAction.from_id(3),data={});A=o.frame[0].copy();seq.append(3)
 print("IN",i,"diff",int(np.sum(pre!=A)),"sig",sig(A),"lvl",o.levels_completed,"state",o.state)
 if o.levels_completed>1: print("SOLVED",parent+seq);raise SystemExit
# At each transition state, test all simple continuations independently; these are 42 relation walls.
walls=0
for n in range(1,8):
 for act in [1,2,3,4,5,7]:
  e,o,A=run(parent+[3]*n)
  oo=e.step(GameAction.from_id(act),data={});walls+=1
  if oo.levels_completed>1:
   print("SOLVED_BRANCH",parent+[3]*n+[act],"wall",walls);raise SystemExit
  print("W",n,act,"d",int(np.sum(A!=oo.frame[0])),"sig",sig(oo.frame[0]),"state",oo.state)
print("WALLS",walls)
