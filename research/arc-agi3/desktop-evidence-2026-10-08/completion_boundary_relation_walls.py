from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import deque
a=Arcade(operation_mode=OperationMode.NORMAL); BASE=[3]*5+[2]*10+[7,5]
def comps(A):
 out=[]
 for c in [0,4,5,10,11]:
  pts=set((int(x),int(y)) for y,x in zip(*np.where(A==c))); seen=set()
  for p in list(pts):
   if p in seen: continue
   q=[p];seen.add(p);cc=[]
   while q:
    x,y=q.pop();cc.append((x,y))
    for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
     if n in pts and n not in seen:seen.add(n);q.append(n)
   if len(cc)>=5:
    out.append((c,len(cc),(min(x for x,y in cc),max(x for x,y in cc),min(y for x,y in cc),max(y for x,y in cc))))
 return sorted(out,key=lambda z:(z[0],-z[1]))
# Completion-focused walls: derive simultaneous coupled endpoint candidates from each axis closure,
# then apply each permitted action once at those relation boundaries.
parents=[("B8",[]),("LEFT",[4]),("Y42",[4]+[2]*8),("BOTTOM",[4]+[2]*11),
         ("RIGHT",[3]),("UP",[1]*6)]
for name,p in parents:
 for act in [1,2,3,4,5,7]:
  e=a.make('ar25');o=None
  for z in BASE+p:o=e.step(GameAction.from_id(z),data={})
  pre=o.frame[0].copy(); o=e.step(GameAction.from_id(act),data={}); post=o.frame[0]
  diff=int(np.sum(pre!=post))
  print("WALL",name,"A",act,"diff",diff,"lvl",o.levels_completed,"state",o.state)
  if o.levels_completed>1:
   print("SOLVED",BASE+p+[act]); raise SystemExit
 print("STRUCT",name,comps(pre))
